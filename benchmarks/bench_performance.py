import time
import tracemalloc
import csv
import os
import json
import sys
import pandas as pd

# ── Pandas baseline ───────────────────────────────────────────────────────────

def pandas_baseline(df: pd.DataFrame) -> dict:
    """
    Naive single-pass Pandas cleaning — what a junior dev would write.
    Detects: missing values, duplicates, obvious type issues.
    Returns a dict of findings (we only measure time/memory, not quality).
    """
    results = {}

    # Missing values
    results["missing"] = df.isnull().sum().to_dict()

    # Disguised nulls
    NULLS = {"n/a","na","none","null","nil","nan","-","--","?","unknown","missing","blank",""}
    for col in df.columns:
        mask = df[col].astype(str).str.strip().str.lower().isin(NULLS)
        results[f"disguised_{col}"] = int(mask.sum())

    # Duplicates
    results["duplicates"] = int(df.duplicated().sum())

    # Mixed types (check if numeric cols have non-numeric)
    for col in df.select_dtypes(include="object").columns:
        non_num = pd.to_numeric(df[col], errors="coerce").isna().sum()
        results[f"mixed_{col}"] = int(non_num)

    return results


# ── Cleanr detector runner ────────────────────────────────────────────────────

def cleanr_detect(df: pd.DataFrame) -> list:
    """Run all Cleanr rule-based detectors."""
    # Add project root to path so we can import detector
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

    from detector.detectors.missing_values  import MissingValuesDetector
    from detector.detectors.duplicate_rows  import DuplicateRowsDetector
    from detector.detectors.date_format     import DateFormatDetector
    from detector.detectors.mixed_types     import MixedTypesDetector
    from detector.detectors.whitespace      import WhitespaceDetector
    from detector.detectors.negative_values import NegativeValuesDetector

    detectors = [
        MissingValuesDetector,
        DuplicateRowsDetector,
        DateFormatDetector,
        MixedTypesDetector,
        WhitespaceDetector,
        NegativeValuesDetector,
    ]
    issues = []
    for D in detectors:
        issues.extend(D(df).detect())
    return issues


# ── Measurement helpers ───────────────────────────────────────────────────────

def measure(fn, df):
    """Returns (elapsed_ms, peak_memory_mb, result)."""
    tracemalloc.start()
    t0     = time.perf_counter()
    result = fn(df)
    elapsed_ms  = (time.perf_counter() - t0) * 1000
    _, peak     = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    peak_mb = peak / 1024 / 1024
    return elapsed_ms, peak_mb, result


# ── Main ──────────────────────────────────────────────────────────────────────

def run(data_dir="benchmark_data"):
    sizes = [100, 500, 1_000, 5_000, 10_000, 50_000, 100_000]
    results = []

    print(f"\n{'Size':>8} | {'Pandas ms':>10} | {'Cleanr ms':>10} | "
          f"{'Pandas MB':>10} | {'Cleanr MB':>10} | {'Speedup':>8} | {'rows/s':>10}")
    print("-" * 80)

    for n in sizes:
        path = os.path.join(data_dir, f"dirty_{n}.csv")
        if not os.path.exists(path):
            print(f"  Skipping {n} — file not found. Run generate_datasets.py first.")
            continue

        df = pd.read_csv(path, dtype=str)

        # Warm up
        pandas_baseline(df)

        # Measure — 3 runs, take median
        p_times, p_mems = [], []
        c_times, c_mems = [], []

        for _ in range(3):
            t, m, _ = measure(pandas_baseline, df)
            p_times.append(t); p_mems.append(m)

        for _ in range(3):
            t, m, _ = measure(cleanr_detect, df)
            c_times.append(t); c_mems.append(m)

        p_ms  = sorted(p_times)[1]   # median of 3
        c_ms  = sorted(c_times)[1]
        p_mb  = sorted(p_mems)[1]
        c_mb  = sorted(c_mems)[1]
        speedup   = p_ms / c_ms if c_ms > 0 else 0
        rows_per_s = n / (c_ms / 1000)

        results.append({
            "rows": n,
            "pandas_ms": round(p_ms, 2),
            "cleanr_ms": round(c_ms, 2),
            "pandas_mb": round(p_mb, 2),
            "cleanr_mb": round(c_mb, 2),
            "speedup":   round(speedup, 2),
            "rows_per_s": int(rows_per_s),
        })

        print(f"{n:>8,} | {p_ms:>10.1f} | {c_ms:>10.1f} | "
              f"{p_mb:>10.2f} | {c_mb:>10.2f} | {speedup:>7.2f}x | {rows_per_s:>10,.0f}")

    # Save results
    os.makedirs("benchmark_results", exist_ok=True)
    with open("benchmark_results/performance.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to benchmark_results/performance.json")
    return results


if __name__ == "__main__":
    run()