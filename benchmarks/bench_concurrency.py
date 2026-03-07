
import os
import sys
import json
import time
import threading
import statistics
import requests

API_BASE   = "http://localhost:8000"
DATA_FILE  = "benchmark_data/dirty_1000.csv"   # use 1k row file for each request


def single_request(result_list, idx):
    """Upload a file and record latency. Thread-safe via result_list append."""
    try:
        with open(DATA_FILE, "rb") as f:
            t0 = time.perf_counter()
            resp = requests.post(
                f"{API_BASE}/upload",
                files={"file": ("bench.csv", f, "text/csv")},
                timeout=60,
            )
            upload_ms = (time.perf_counter() - t0) * 1000

        if resp.status_code != 200:
            result_list.append({"success": False, "error": resp.text})
            return

        job_id = resp.json()["job_id"]

        # Apply all recommended fixes
        t1 = time.perf_counter()
        fix_resp = requests.post(
            f"{API_BASE}/fix/{job_id}",
            json={"selections": {}},
            timeout=60,
        )
        fix_ms = (time.perf_counter() - t1) * 1000

        total_ms = upload_ms + fix_ms
        result_list.append({
            "success":    fix_resp.status_code == 200,
            "upload_ms":  round(upload_ms, 2),
            "fix_ms":     round(fix_ms, 2),
            "total_ms":   round(total_ms, 2),
        })
    except Exception as e:
        result_list.append({"success": False, "error": str(e)})


def run_concurrent(n_concurrent: int) -> dict:
    results = []
    threads = [threading.Thread(target=single_request, args=(results, i))
               for i in range(n_concurrent)]

    t0 = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    wall_ms = (time.perf_counter() - t0) * 1000

    successes = [r for r in results if r.get("success")]
    failures  = len(results) - len(successes)
    latencies = [r["total_ms"] for r in successes]

    if not latencies:
        return {"concurrent": n_concurrent, "success_rate": 0, "error": "all failed"}

    latencies.sort()
    p50 = statistics.median(latencies)
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)] if len(latencies) >= 100 else latencies[-1]
    throughput = len(successes) / (wall_ms / 1000)

    return {
        "concurrent":   n_concurrent,
        "success":      len(successes),
        "failures":     failures,
        "success_rate": round(len(successes) / len(results) * 100, 1),
        "p50_ms":       round(p50, 1),
        "p95_ms":       round(p95, 1),
        "p99_ms":       round(p99, 1),
        "throughput_rps": round(throughput, 2),
        "wall_ms":      round(wall_ms, 1),
    }


def check_api_available():
    try:
        r = requests.get(f"{API_BASE}/health", timeout=3)
        return r.status_code == 200
    except:
        return False


def run():
    if not os.path.exists(DATA_FILE):
        print(f"ERROR: {DATA_FILE} not found. Run generate_datasets.py first.")
        sys.exit(1)

    if not check_api_available():
        print(f"ERROR: API not reachable at {API_BASE}")
        print("Start it with: uvicorn api.main:app --reload --port 8000")
        sys.exit(1)

    concurrency_levels = [1, 2, 5, 10, 20, 50]
    results = []

    print(f"\n{'Workers':>8} | {'Success%':>9} | {'p50 ms':>8} | "
          f"{'p95 ms':>8} | {'p99 ms':>8} | {'req/s':>8}")
    print("-" * 65)

    for n in concurrency_levels:
        r = run_concurrent(n)
        results.append(r)
        if "error" in r:
            print(f"{n:>8} | FAILED: {r['error']}")
        else:
            print(f"{n:>8} | {r['success_rate']:>8.1f}% | {r['p50_ms']:>8.1f} | "
                  f"{r['p95_ms']:>8.1f} | {r['p99_ms']:>8.1f} | "
                  f"{r['throughput_rps']:>8.2f}")
        time.sleep(2)  # brief pause between levels

    os.makedirs("benchmark_results", exist_ok=True)
    with open("benchmark_results/concurrency.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to benchmark_results/concurrency.json")
    return results


if __name__ == "__main__":
    run()