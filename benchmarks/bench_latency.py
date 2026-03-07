
import os
import sys
import time
import json
import tempfile
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def time_stage(fn, *args, **kwargs):
    t0 = time.perf_counter()
    result = fn(*args, **kwargs)
    return (time.perf_counter() - t0) * 1000, result


def run_pipeline_staged(csv_path: str):
    from detector.detectors.missing_values  import MissingValuesDetector
    from detector.detectors.duplicate_rows  import DuplicateRowsDetector
    from detector.detectors.date_format     import DateFormatDetector
    from detector.detectors.mixed_types     import MixedTypesDetector
    from detector.detectors.whitespace      import WhitespaceDetector
    from detector.detectors.negative_values import NegativeValuesDetector
    from detector.models  import CleaningReport, IssueType
    from detector.fixer   import Fixer

    # Stage 1: Read
    t_read, df = time_stage(pd.read_csv, csv_path, dtype=str)
    df.columns = [c.strip() for c in df.columns]
    total_rows = len(df)

    # Stage 2: Detect
    def detect_all():
        issues = []
        for D in [MissingValuesDetector, DuplicateRowsDetector, DateFormatDetector,
                  MixedTypesDetector, WhitespaceDetector, NegativeValuesDetector]:
            issues.extend(D(df).detect())
        return issues

    t_detect, issues = time_stage(detect_all)

    # Stage 3: Fix — auto-select first option for each SUGGEST issue
    report = CleaningReport(
        job_id="bench", filename="bench.csv",
        rows_analyzed=total_rows, cols_analyzed=len(df.columns),
        issues=issues, processing_ms=0,
    )
    selections = {}
    for issue in issues:
        if issue.fix_tier.value == "SUGGEST" and issue.fix_options:
            key = f"{issue.column}:{issue.issue_type.value}"
            selections[key] = issue.fix_options[0].action

    def fix_all():
        return Fixer(df, report, selections).apply_all()

    t_fix, clean_df = time_stage(fix_all)

    # Stage 4: Write
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        tmp_path = tmp.name

    t_write, _ = time_stage(clean_df.to_csv, tmp_path, index=False)
    os.unlink(tmp_path)

    t_total = t_read + t_detect + t_fix + t_write

    return {
        "rows":      total_rows,
        "t_read_ms":   round(t_read,   2),
        "t_detect_ms": round(t_detect, 2),
        "t_fix_ms":    round(t_fix,    2),
        "t_write_ms":  round(t_write,  2),
        "t_total_ms":  round(t_total,  2),
        "rows_per_sec": int(total_rows / (t_total / 1000)),
    }


def run(data_dir="benchmark_data"):
    sizes = [100, 500, 1_000, 5_000, 10_000, 50_000, 100_000]
    results = []

    print(f"\n{'Rows':>8} | {'Read':>8} | {'Detect':>8} | {'Fix':>8} | "
          f"{'Write':>8} | {'TOTAL':>8} | {'rows/s':>10}")
    print("-" * 75)

    for n in sizes:
        path = os.path.join(data_dir, f"dirty_{n}.csv")
        if not os.path.exists(path):
            print(f"  Skipping {n} — file not found.")
            continue

        # 3 runs, take best (warm cache)
        runs = [run_pipeline_staged(path) for _ in range(3)]
        r = min(runs, key=lambda x: x["t_total_ms"])
        results.append(r)

        print(f"{r['rows']:>8,} | {r['t_read_ms']:>7.1f}ms | {r['t_detect_ms']:>7.1f}ms | "
              f"{r['t_fix_ms']:>7.1f}ms | {r['t_write_ms']:>7.1f}ms | "
              f"{r['t_total_ms']:>7.1f}ms | {r['rows_per_sec']:>10,}")

    os.makedirs("benchmark_results", exist_ok=True)
    with open("benchmark_results/latency.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to benchmark_results/latency.json")
    return results


if __name__ == "__main__":
    run()