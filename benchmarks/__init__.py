
import sys
import os
import argparse

# Make sure project root is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmarks.generate_datasets import generate
from benchmarks.bench_performance  import run as run_performance
from benchmarks.bench_accuracy     import run as run_accuracy
from benchmarks.bench_latency      import run as run_latency
from benchmarks.bench_nn           import run as run_nn
from benchmarks.generate_charts    import (
    chart_performance, chart_accuracy, chart_latency, chart_nn, print_resume_summary
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-concurrency", action="store_true",
                        help="Skip concurrency test (requires running API)")
    parser.add_argument("--skip-nn", action="store_true",
                        help="Skip NN benchmark (requires compiled binary)")
    parser.add_argument("--data-dir", default="benchmark_data")
    args = parser.parse_args()

    os.makedirs(args.data_dir, exist_ok=True)
    os.makedirs("benchmark_results/charts", exist_ok=True)

    # ── Step 1: Generate datasets ─────────────────────────────────────────────
    print("\n" + "="*60)
    print("  STEP 1/5 — Generating benchmark datasets")
    print("="*60)
    sizes = [100, 500, 1_000, 5_000, 10_000, 50_000, 100_000]
    for n in sizes:
        if not os.path.exists(os.path.join(args.data_dir, f"dirty_{n}.csv")):
            generate(n, error_rate=0.20, out_dir=args.data_dir)
        else:
            print(f"  Reusing existing dirty_{n}.csv")

    # ── Step 2: Performance ───────────────────────────────────────────────────
    print("\n" + "="*60)
    print("  STEP 2/5 — Performance vs Pandas baseline")
    print("="*60)
    run_performance(args.data_dir)

    # ── Step 3: Accuracy ──────────────────────────────────────────────────────
    print("\n" + "="*60)
    print("  STEP 3/5 — Detection accuracy (precision / recall / F1)")
    print("="*60)
    run_accuracy(args.data_dir)

    # ── Step 4: Latency ───────────────────────────────────────────────────────
    print("\n" + "="*60)
    print("  STEP 4/5 — End-to-end pipeline latency")
    print("="*60)
    run_latency(args.data_dir)

    # ── Step 5: NN ────────────────────────────────────────────────────────────
    if not args.skip_nn:
        print("\n" + "="*60)
        print("  STEP 5/5 — Neural network inference accuracy & latency")
        print("="*60)
        run_nn(args.data_dir)
    else:
        print("\n  Skipping NN benchmark (--skip-nn)")

    # ── Concurrency (optional) ────────────────────────────────────────────────
    if not args.skip_concurrency:
        print("\n" + "="*60)
        print("  OPTIONAL — Concurrent job scalability")
        print("  (Requires: uvicorn api.main:app --port 8000 running)")
        print("="*60)
        try:
            from benchmarks.bench_concurrency import run as run_concurrency
            run_concurrency()
        except SystemExit:
            print("  Skipped — API not running.")

    # ── Charts ────────────────────────────────────────────────────────────────
    print("\n" + "="*60)
    print("  Generating charts...")
    print("="*60)
    chart_performance()
    chart_accuracy()
    chart_latency()
    chart_nn()
    print_resume_summary()

    print("\nAll done! Results in benchmark_results/")
    print("Charts in    benchmark_results/charts/")


if __name__ == "__main__":
    main()