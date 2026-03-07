
import os
import sys
import json
import pandas as pd
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ── label normaliser ──────────────────────────────────────────────────────────
# Map IssueType enum values → ground-truth label strings

ISSUE_TO_LABEL = {
    "MISSING_VALUES": "missing_value",
    "DUPLICATE_ROWS": "duplicate",
    "DATE_FORMAT":    "bad_date",
    "MIXED_TYPES":    "mixed_type",
    "WHITESPACE":     "whitespace",
    "NEGATIVE_VALUES":"negative_value",
    "ANOMALY":        "anomaly",
}


def run_detectors(df):
    from detector.detectors.missing_values  import MissingValuesDetector
    from detector.detectors.duplicate_rows  import DuplicateRowsDetector
    from detector.detectors.date_format     import DateFormatDetector
    from detector.detectors.mixed_types     import MixedTypesDetector
    from detector.detectors.whitespace      import WhitespaceDetector
    from detector.detectors.negative_values import NegativeValuesDetector

    issues = []
    for D in [MissingValuesDetector, DuplicateRowsDetector, DateFormatDetector,
              MixedTypesDetector, WhitespaceDetector, NegativeValuesDetector]:
        issues.extend(D(df).detect())
    return issues


def issues_to_row_labels(issues, df) -> dict:
    """
    Convert Issue objects → { row_idx: set(labels) }.
    For column-level issues we mark ALL affected rows in that column.
    For DUPLICATE_ROWS we mark every duplicate row index.
    """
    detected = defaultdict(set)

    for issue in issues:
        label = ISSUE_TO_LABEL.get(issue.issue_type.value, issue.issue_type.value)

        if issue.issue_type.value == "DUPLICATE_ROWS":
            # Find actual duplicate row indices
            dup_mask = df.duplicated(keep='first')
            for idx in df[dup_mask].index:
                detected[idx].add(label)

        elif issue.column and issue.column in df.columns:
            from detector.detectors.missing_values import DISGUISED_NULLS as DN

            col = df[issue.column]

            if issue.issue_type.value == "MISSING_VALUES":
                null_mask      = col.isna()
                disguised_mask = col.astype(str).str.strip().str.lower().isin(DN)
                for idx in df[null_mask | disguised_mask].index:
                    detected[idx].add(label)

            elif issue.issue_type.value == "NEGATIVE_VALUES":
                numeric = pd.to_numeric(col, errors='coerce')
                for idx in df[numeric < 0].index:
                    detected[idx].add(label)

            elif issue.issue_type.value == "WHITESPACE":
                ws_mask = col.astype(str) != col.astype(str).str.strip()
                for idx in df[ws_mask].index:
                    detected[idx].add(label)

            elif issue.issue_type.value == "MIXED_TYPES":
                non_num = pd.to_numeric(col, errors='coerce').isna()
                not_null = col.notna() & (col.astype(str).str.strip() != "")
                for idx in df[non_num & not_null].index:
                    detected[idx].add(label)

            else:
                # DATE_FORMAT etc — mark all affected rows proportionally
                for idx in range(issue.affected_rows):
                    detected[idx].add(label)

    return dict(detected)


def precision_recall_f1(tp, fp, fn):
    p = tp / (tp + fp) if (tp + fp) > 0 else 0
    r = tp / (tp + fn) if (tp + fn) > 0 else 0
    f = 2 * p * r / (p + r) if (p + r) > 0 else 0
    return round(p, 4), round(r, 4), round(f, 4)


def evaluate(n, data_dir="benchmark_data"):
    csv_path = os.path.join(data_dir, f"dirty_{n}.csv")
    gt_path  = os.path.join(data_dir, f"ground_truth_{n}.json")

    if not os.path.exists(csv_path) or not os.path.exists(gt_path):
        print(f"  Skipping {n} — files not found.")
        return None

    df = pd.read_csv(csv_path, dtype=str)
    df.columns = [c.strip() for c in df.columns]

    with open(gt_path) as f:
        ground_truth = json.load(f)   # { "row_idx_str": [labels] }

    # Normalise GT keys to int
    gt = {int(k): set(v) for k, v in ground_truth.items()}

    issues   = run_detectors(df)
    detected = issues_to_row_labels(issues, df)

    # Compute TP, FP, FN across all rows
    all_rows = set(gt.keys()) | set(detected.keys())
    tp = fp = fn = 0

    for row in all_rows:
        gt_labels  = gt.get(row, set())
        det_labels = detected.get(row, set())
        tp += len(gt_labels & det_labels)
        fp += len(det_labels - gt_labels)
        fn += len(gt_labels - det_labels)

    p, r, f = precision_recall_f1(tp, fp, fn)
    total_errors = sum(len(v) for v in gt.values())

    return {
        "rows":          n,
        "total_errors":  total_errors,
        "tp": tp, "fp": fp, "fn": fn,
        "precision":     p,
        "recall":        r,
        "f1":            f,
    }


def run(data_dir="benchmark_data"):
    sizes = [100, 500, 1_000, 5_000, 10_000]
    results = []

    print(f"\n{'Size':>8} | {'Errors':>7} | {'TP':>5} | {'FP':>5} | {'FN':>5} | "
          f"{'Precision':>10} | {'Recall':>8} | {'F1':>8}")
    print("-" * 75)

    for n in sizes:
        r = evaluate(n, data_dir)
        if r is None:
            continue
        results.append(r)
        print(f"{r['rows']:>8,} | {r['total_errors']:>7} | {r['tp']:>5} | "
              f"{r['fp']:>5} | {r['fn']:>5} | {r['precision']:>10.3f} | "
              f"{r['recall']:>8.3f} | {r['f1']:>8.3f}")

    os.makedirs("benchmark_results", exist_ok=True)
    with open("benchmark_results/accuracy.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to benchmark_results/accuracy.json")
    return results


if __name__ == "__main__":
    run()