
import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np

RESULTS_DIR = "benchmark_results"
CHARTS_DIR  = "benchmark_results/charts"
os.makedirs(CHARTS_DIR, exist_ok=True)

# ── Style ─────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor": "#0d1117",
    "axes.facecolor":   "#161b22",
    "axes.edgecolor":   "#30363d",
    "axes.labelcolor":  "#c9d1d9",
    "xtick.color":      "#8b949e",
    "ytick.color":      "#8b949e",
    "text.color":       "#c9d1d9",
    "grid.color":       "#21262d",
    "grid.linewidth":   0.8,
    "font.family":      "monospace",
    "axes.titlepad":    14,
    "axes.titlesize":   13,
    "axes.labelsize":   11,
})

GREEN  = "#3fb950"
AMBER  = "#d29922"
RED    = "#f85149"
BLUE   = "#58a6ff"
PURPLE = "#bc8cff"


def load(name):
    path = os.path.join(RESULTS_DIR, f"{name}.json")
    if not os.path.exists(path):
        print(f"  Skipping {name}.json — not found")
        return None
    with open(path) as f:
        return json.load(f)


# ── Chart 1: Performance — Cleanr vs Pandas ──────────────────────────────────
def chart_performance():
    data = load("performance")
    if not data:
        return

    rows  = [d["rows"] for d in data]
    p_ms  = [d["pandas_ms"] for d in data]
    c_ms  = [d["cleanr_ms"] for d in data]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("CLEANR  ·  Performance vs Pandas Baseline", color="#c9d1d9", fontsize=14, y=1.02)

    # Left: latency comparison
    x = np.arange(len(rows))
    w = 0.35
    ax1.bar(x - w/2, p_ms, w, label="Pandas baseline", color=AMBER,  alpha=0.85)
    ax1.bar(x + w/2, c_ms, w, label="Cleanr pipeline", color=GREEN, alpha=0.85)
    ax1.set_yscale("log")
    ax1.set_xticks(x)
    ax1.set_xticklabels([f"{r:,}" for r in rows], rotation=30, ha="right")
    ax1.set_xlabel("Dataset size (rows)")
    ax1.set_ylabel("Time (ms, log scale)")
    ax1.set_title("Detection Latency")
    ax1.legend(facecolor="#21262d", edgecolor="#30363d")
    ax1.grid(axis="y", alpha=0.4)

    # Right: speedup
    speedups = [d["speedup"] for d in data]
    ax2.plot([f"{r:,}" for r in rows], speedups, color=BLUE, marker="o", linewidth=2)
    ax2.axhline(1, color="#30363d", linestyle="--", linewidth=1)
    ax2.fill_between(range(len(rows)), speedups, 1,
                     where=[s > 1 for s in speedups], alpha=0.15, color=BLUE)
    ax2.set_xticklabels([f"{r:,}" for r in rows], rotation=30, ha="right")
    ax2.set_xlabel("Dataset size (rows)")
    ax2.set_ylabel("Speedup (×)")
    ax2.set_title("Cleanr Speedup over Pandas")
    ax2.grid(alpha=0.4)

    plt.tight_layout()
    out = os.path.join(CHARTS_DIR, "performance.png")
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"  Saved {out}")


# ── Chart 2: Accuracy ─────────────────────────────────────────────────────────
def chart_accuracy():
    data = load("accuracy")
    if not data:
        return

    rows      = [d["rows"] for d in data]
    precision = [d["precision"] for d in data]
    recall    = [d["recall"]    for d in data]
    f1        = [d["f1"]        for d in data]
    xlabels   = [f"{r:,}" for r in rows]

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.suptitle("CLEANR  ·  Detection Accuracy", color="#c9d1d9", fontsize=14)

    ax.plot(xlabels, precision, color=BLUE,   marker="o", linewidth=2, label="Precision")
    ax.plot(xlabels, recall,    color=GREEN,  marker="s", linewidth=2, label="Recall")
    ax.plot(xlabels, f1,        color=AMBER,  marker="^", linewidth=2.5, label="F1",
            linestyle="--")

    ax.set_ylim(0, 1.05)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))
    ax.set_xlabel("Dataset size (rows)")
    ax.set_ylabel("Score")
    ax.set_title("Precision / Recall / F1 vs Dataset Size")
    ax.legend(facecolor="#21262d", edgecolor="#30363d")
    ax.grid(alpha=0.4)

    plt.tight_layout()
    out = os.path.join(CHARTS_DIR, "accuracy.png")
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"  Saved {out}")


# ── Chart 3: Latency breakdown ────────────────────────────────────────────────
def chart_latency():
    data = load("latency")
    if not data:
        return

    rows      = [d["rows"]        for d in data]
    t_read    = [d["t_read_ms"]   for d in data]
    t_detect  = [d["t_detect_ms"] for d in data]
    t_fix     = [d["t_fix_ms"]    for d in data]
    t_write   = [d["t_write_ms"]  for d in data]
    xlabels   = [f"{r:,}" for r in rows]
    x         = np.arange(len(rows))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("CLEANR  ·  End-to-End Pipeline Latency", color="#c9d1d9", fontsize=14)

    # Stacked bar
    ax1.bar(x, t_read,   label="Read",   color=BLUE,   alpha=0.9)
    ax1.bar(x, t_detect, label="Detect", color=GREEN,  alpha=0.9, bottom=t_read)
    bot2 = [a+b for a,b in zip(t_read, t_detect)]
    ax1.bar(x, t_fix,    label="Fix",    color=AMBER,  alpha=0.9, bottom=bot2)
    bot3 = [a+b for a,b in zip(bot2, t_fix)]
    ax1.bar(x, t_write,  label="Write",  color=PURPLE, alpha=0.9, bottom=bot3)
    ax1.set_yscale("log")
    ax1.set_xticks(x)
    ax1.set_xticklabels(xlabels, rotation=30, ha="right")
    ax1.set_xlabel("Dataset size (rows)")
    ax1.set_ylabel("Time (ms, log scale)")
    ax1.set_title("Pipeline Stage Breakdown")
    ax1.legend(facecolor="#21262d", edgecolor="#30363d")
    ax1.grid(axis="y", alpha=0.4)

    # Throughput
    rps = [d["rows_per_sec"] for d in data]
    ax2.plot(xlabels, rps, color=GREEN, marker="o", linewidth=2)
    ax2.fill_between(range(len(rows)), rps, alpha=0.15, color=GREEN)
    ax2.set_xticks(range(len(rows)))
    ax2.set_xticklabels(xlabels, rotation=30, ha="right")
    ax2.set_xlabel("Dataset size (rows)")
    ax2.set_ylabel("rows / second")
    ax2.set_title("Throughput")
    ax2.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax2.grid(alpha=0.4)

    plt.tight_layout()
    out = os.path.join(CHARTS_DIR, "latency.png")
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"  Saved {out}")


# ── Chart 4: Concurrency ──────────────────────────────────────────────────────
def chart_concurrency():
    data = load("concurrency")
    if not data:
        return

    workers   = [d["concurrent"]       for d in data]
    p50       = [d.get("p50_ms", 0)    for d in data]
    p95       = [d.get("p95_ms", 0)    for d in data]
    p99       = [d.get("p99_ms", 0)    for d in data]
    rps       = [d.get("throughput_rps", 0) for d in data]
    success   = [d.get("success_rate", 0)   for d in data]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("CLEANR  ·  Concurrent Job Scalability", color="#c9d1d9", fontsize=14)

    # Latency percentiles
    ax1.plot(workers, p50, color=GREEN,  marker="o", linewidth=2, label="p50")
    ax1.plot(workers, p95, color=AMBER,  marker="s", linewidth=2, label="p95")
    ax1.plot(workers, p99, color=RED,    marker="^", linewidth=2, label="p99")
    ax1.set_xlabel("Concurrent workers")
    ax1.set_ylabel("Latency (ms)")
    ax1.set_title("Request Latency Percentiles")
    ax1.legend(facecolor="#21262d", edgecolor="#30363d")
    ax1.grid(alpha=0.4)

    # Throughput + success rate
    color2 = BLUE
    ax2.bar(workers, rps, color=color2, alpha=0.7, width=2)
    ax2.set_xlabel("Concurrent workers")
    ax2.set_ylabel("Throughput (req/s)", color=color2)
    ax2.tick_params(axis="y", labelcolor=color2)
    ax2.set_title("Throughput & Success Rate")

    ax3 = ax2.twinx()
    ax3.plot(workers, success, color=GREEN, marker="o", linewidth=2)
    ax3.set_ylabel("Success rate (%)", color=GREEN)
    ax3.set_ylim(0, 110)
    ax3.tick_params(axis="y", labelcolor=GREEN)
    ax3.spines["right"].set_color(GREEN)

    plt.tight_layout()
    out = os.path.join(CHARTS_DIR, "concurrency.png")
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"  Saved {out}")


# ── Chart 5: NN accuracy ──────────────────────────────────────────────────────
def chart_nn():
    data = load("nn")
    if not data:
        return

    # Threshold sweep
    sweep = data.get("threshold_sweep", [])
    if sweep:
        thresholds = [d["threshold"] for d in sweep]
        f1s        = [d["f1"]        for d in sweep]
        precs      = [d["precision"] for d in sweep]
        recs       = [d["recall"]    for d in sweep]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
        fig.suptitle("CLEANR  ·  Neural Network Anomaly Detection", color="#c9d1d9", fontsize=14)

        ax1.plot(thresholds, precs, color=BLUE,  marker="o", label="Precision")
        ax1.plot(thresholds, recs,  color=GREEN, marker="s", label="Recall")
        ax1.plot(thresholds, f1s,   color=AMBER, marker="^", linewidth=2.5,
                 linestyle="--", label="F1")
        best_t = thresholds[f1s.index(max(f1s))]
        ax1.axvline(best_t, color=RED, linestyle=":", linewidth=1.5,
                    label=f"Best threshold ({best_t})")
        ax1.set_ylim(0, 1.05)
        ax1.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))
        ax1.set_xlabel("Anomaly score threshold")
        ax1.set_ylabel("Score")
        ax1.set_title("Precision / Recall vs Threshold")
        ax1.legend(facecolor="#21262d", edgecolor="#30363d")
        ax1.grid(alpha=0.4)

        # Latency
        lat = data.get("latency", [])
        if lat:
            rows_l = [d["rows"]         for d in lat]
            ms_l   = [d["inference_ms"] for d in lat]
            ax2.plot([f"{r:,}" for r in rows_l], ms_l,
                     color=PURPLE, marker="o", linewidth=2)
            ax2.set_xlabel("Dataset size (rows)")
            ax2.set_ylabel("Inference time (ms)")
            ax2.set_title("C++ NN Inference Latency")
            ax2.set_xticklabels([f"{r:,}" for r in rows_l], rotation=30, ha="right")
            ax2.grid(alpha=0.4)

        plt.tight_layout()
        out = os.path.join(CHARTS_DIR, "nn.png")
        plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close()
        print(f"  Saved {out}")


# ── Summary table ─────────────────────────────────────────────────────────────
def print_resume_summary():
    print("\n" + "="*65)
    print("  RESUME-READY METRICS SUMMARY")
    print("="*65)

    perf = load("performance")
    if perf:
        max_rps = max(d["rows_per_s"] for d in perf)
        avg_speedup = sum(d["speedup"] for d in perf) / len(perf)
        print(f"\n  Performance:")
        print(f"    • Peak throughput:      {max_rps:>10,} rows/sec")
        print(f"    • Avg speedup vs naive: {avg_speedup:>10.1f}×")

    acc = load("accuracy")
    if acc:
        best = max(acc, key=lambda x: x["f1"])
        avg_f1 = sum(d["f1"] for d in acc) / len(acc)
        print(f"\n  Detection Accuracy:")
        print(f"    • Best F1 score:        {best['f1']*100:>9.1f}%  ({best['rows']:,} rows)")
        print(f"    • Avg F1 across sizes:  {avg_f1*100:>9.1f}%")

    lat = load("latency")
    if lat:
        r1k  = next((d for d in lat if d["rows"] == 1030), lat[2])
        r100k = next((d for d in lat if d["rows"] >= 100000), lat[-1])
        print(f"\n  Latency:")
        print(f"    • ~1,000-row file:      {r1k['t_total_ms']:>9.1f} ms end-to-end")
        print(f"    • ~100,000-row file:    {r100k['t_total_ms']:>9.1f} ms end-to-end")

    print("\n" + "="*65)
    print("  Use these numbers in your resume bullets!")
    print("="*65 + "\n")