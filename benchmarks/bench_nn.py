
import os
import sys
import json
import time
import subprocess
import tempfile
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Path to compiled binary — adjust if needed
ENGINE = os.path.join(os.path.dirname(__file__), "..", "api", "cleanr-engine")
if sys.platform == "win32":
    ENGINE += ".exe"


def run_nn_anomalies(csv_path: str) -> tuple:
    """Run C++ engine anomaly detection. Returns (results_list, elapsed_ms)."""
    if not os.path.exists(ENGINE):
        return [], 0

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        out_path = tmp.name

    t0 = time.perf_counter()
    proc = subprocess.run(
        [ENGINE, "--anomalies", csv_path, out_path],
        capture_output=True, timeout=120,
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000

    if proc.returncode != 0:
        os.unlink(out_path)
        return [], elapsed_ms

    with open(out_path) as f:
        data = json.load(f)
    os.unlink(out_path)

    return data.get("anomalies", []), elapsed_ms


def evaluate_nn(n, data_dir="benchmark_data", threshold=0.10):
    csv_path = os.path.join(data_dir, f"dirty_{n}.csv")
    gt_path  = os.path.join(data_dir, f"ground_truth_{n}.json")

    if not os.path.exists(csv_path):
        return None

    with open(gt_path) as f:
        gt = {int(k): set(v) for k, v in json.load(f).items()}

    # Ground truth anomaly rows
    gt_anomaly_rows = {idx for idx, labels in gt.items() if "anomaly" in labels}

    anomalies, elapsed_ms = run_nn_anomalies(csv_path)

    # Detected anomaly rows
    detected_rows = set()
    for a in anomalies:
        if a.get("score", 0) >= threshold:
            detected_rows.add(a.get("row", -1))

    tp = len(gt_anomaly_rows & detected_rows)
    fp = len(detected_rows - gt_anomaly_rows)
    fn = len(gt_anomaly_rows - detected_rows)

    p = tp / (tp + fp) if (tp + fp) > 0 else 0
    r = tp / (tp + fn) if (tp + fn) > 0 else 0
    f = 2 * p * r / (p + r) if (p + r) > 0 else 0

    return {
        "rows":           n,
        "threshold":      threshold,
        "gt_anomalies":   len(gt_anomaly_rows),
        "detected":       len(detected_rows),
        "tp": tp, "fp": fp, "fn": fn,
        "precision":      round(p, 4),
        "recall":         round(r, 4),
        "f1":             round(f, 4),
        "inference_ms":   round(elapsed_ms, 2),
        "ms_per_1k_rows": round(elapsed_ms / n * 1000, 2),
    }


def threshold_sweep(n=5000, data_dir="benchmark_data"):
    """Find the best threshold by sweeping 0.05 → 0.25."""
    thresholds = [0.05, 0.08, 0.10, 0.12, 0.15, 0.18, 0.20, 0.25]
    results = []

    print(f"\n=== Threshold sweep on {n:,} rows ===")
    print(f"{'Threshold':>10} | {'Precision':>10} | {'Recall':>8} | {'F1':>8} | {'Detected':>9}")
    print("-" * 55)

    for t in thresholds:
        r = evaluate_nn(n, data_dir, threshold=t)
        if r is None:
            continue
        results.append(r)
        print(f"{t:>10.2f} | {r['precision']:>10.3f} | {r['recall']:>8.3f} | "
              f"{r['f1']:>8.3f} | {r['detected']:>9}")

    best = max(results, key=lambda x: x["f1"]) if results else None
    if best:
        print(f"\nBest threshold: {best['threshold']} (F1={best['f1']})")
    return results


def latency_by_size(data_dir="benchmark_data"):
    sizes = [100, 500, 1_000, 5_000, 10_000, 50_000, 100_000]
    results = []

    print(f"\n=== NN Inference Latency by Dataset Size ===")
    print(f"{'Rows':>8} | {'Latency ms':>12} | {'ms/1k rows':>12} | {'rows/sec':>10}")
    print("-" * 50)

    for n in sizes:
        path = os.path.join(data_dir, f"dirty_{n}.csv")
        if not os.path.exists(path):
            continue

        # 3 runs, take best
        times = []
        for _ in range(3):
            _, ms = run_nn_anomalies(path)
            times.append(ms)
        best_ms = min(times)
        rows_per_sec = int(n / (best_ms / 1000)) if best_ms > 0 else 0

        r = {
            "rows": n,
            "inference_ms": round(best_ms, 2),
            "ms_per_1k": round(best_ms / n * 1000, 2),
            "rows_per_sec": rows_per_sec,
        }
        results.append(r)
        print(f"{n:>8,} | {best_ms:>11.1f}ms | {r['ms_per_1k']:>11.2f}ms | "
              f"{rows_per_sec:>10,}")

    return results


def run(data_dir="benchmark_data"):
    if not os.path.exists(ENGINE):
        print(f"WARNING: Engine binary not found at {ENGINE}")
        print("Compile with: cd engine_nn/build && cmake --build . --config Release")
        print("Skipping NN benchmarks.\n")
        return {}

    # Accuracy at default threshold
    sizes = [100, 500, 1_000, 5_000, 10_000]
    accuracy_results = []

    print(f"\n=== NN Anomaly Detection Accuracy (threshold=0.10) ===")
    print(f"{'Rows':>8} | {'GT Anomalies':>13} | {'Detected':>9} | "
          f"{'Precision':>10} | {'Recall':>8} | {'F1':>8}")
    print("-" * 65)

    for n in sizes:
        r = evaluate_nn(n, data_dir, threshold=0.10)
        if r is None:
            continue
        accuracy_results.append(r)
        print(f"{n:>8,} | {r['gt_anomalies']:>13} | {r['detected']:>9} | "
              f"{r['precision']:>10.3f} | {r['recall']:>8.3f} | {r['f1']:>8.3f}")

    # Threshold sweep
    sweep = threshold_sweep(5000 if os.path.exists(
        os.path.join(data_dir, "dirty_5000.csv")) else 1000, data_dir)

    # Latency
    latency = latency_by_size(data_dir)

    results = {
        "accuracy": accuracy_results,
        "threshold_sweep": sweep,
        "latency": latency,
    }

    os.makedirs("benchmark_results", exist_ok=True)
    with open("benchmark_results/nn.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to benchmark_results/nn.json")
    return results


if __name__ == "__main__":
    run()
























