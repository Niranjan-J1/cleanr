
import csv
import json
import random
import string
import os
from datetime import datetime, timedelta

random.seed(42)

# ── helpers ──────────────────────────────────────────────────────────────────

def rand_name():
    first = random.choice([
        "Alice","Bob","Carol","David","Emma","Frank","Grace","Henry",
        "Isla","Jack","Karen","Leo","Mia","Noah","Olivia","Paul",
        "Quinn","Rosa","Sam","Tara","Uma","Victor","Wendy","Xena","Yusuf","Zara"
    ])
    last = random.choice([
        "Smith","Jones","Brown","Wilson","Taylor","Davies","Evans",
        "Thomas","Roberts","Walker","White","Thompson","Martin","Clarke"
    ])
    return f"{first} {last}"

def rand_email(name):
    parts = name.lower().split()
    return f"{parts[0]}.{parts[1]}@example.com"

def rand_date(start_year=2020, end_year=2024):
    start = datetime(start_year, 1, 1)
    end   = datetime(end_year, 12, 31)
    return (start + timedelta(days=random.randint(0, (end - start).days))).strftime("%Y-%m-%d")

def rand_dept():
    return random.choice(["Engineering","Marketing","Sales","HR","Finance","Operations"])

def rand_status():
    return random.choice(["active","inactive","pending"])

# ── clean row factory ─────────────────────────────────────────────────────────

def clean_row(i):
    name = rand_name()
    return {
        "id":         i,
        "name":       name,
        "email":      rand_email(name),
        "age":        random.randint(22, 60),
        "salary":     random.randint(40000, 150000),
        "join_date":  rand_date(),
        "department": rand_dept(),
        "status":     rand_status(),
    }

# ── error injectors ───────────────────────────────────────────────────────────
# Each returns (modified_row, error_label) or (row, None) if no error injected.

INJECTORS = {
    "missing_value": lambda row: (
        {**row, random.choice(["name","email","age","salary"]): ""},
        "missing_value"
    ),
    "disguised_null": lambda row: (
        {**row, random.choice(["age","salary","status"]): random.choice(["N/A","NULL","none","?","-"])},
        "missing_value"   # same fix type
    ),
    "anomaly_age": lambda row: (
        {**row, "age": random.choice([0, 999, -5, 200])},
        "anomaly"
    ),
    "anomaly_salary": lambda row: (
        {**row, "salary": random.choice([-5000, -1, 9999999])},
        "anomaly"
    ),
    "negative_salary": lambda row: (
        {**row, "salary": -abs(row["salary"])},
        "negative_value"
    ),
    "bad_date": lambda row: (
        {**row, "join_date": random.choice([
            "9999-99-99","not-a-date","32/13/2020","2020-13-01"
        ])},
        "bad_date"
    ),
    "mixed_type": lambda row: (
        {**row, "age": random.choice(["thirty","twenty-five","n/a","old"])},
        "mixed_type"
    ),
    "whitespace": lambda row: (
        {**row, "name": f"  {row['name']}  ", "status": f" {row['status']} "},
        "whitespace"
    ),
    "case_inconsistency": lambda row: (
        {**row, "status": row["status"].upper()},
        "case_inconsistency"
    ),
    "duplicate": None,   # handled separately
}

# ── main generator ────────────────────────────────────────────────────────────

def generate(n_rows: int, error_rate: float = 0.20, out_dir: str = ".") -> dict:
    """
    Generate a dirty CSV of n_rows rows.
    Returns a ground-truth dict: { row_index: [error_labels] }
    """
    os.makedirs(out_dir, exist_ok=True)
    rows        = [clean_row(i + 1) for i in range(n_rows)]
    ground_truth = {}   # { row_idx: [label, ...] }

    injector_names = [k for k in INJECTORS if k != "duplicate"]
    n_errors = int(n_rows * error_rate)

    # Pick random rows to corrupt (allow multi-error per row at low rate)
    error_rows = random.sample(range(n_rows), min(n_errors, n_rows))

    for idx in error_rows:
        inj_name = random.choice(injector_names)
        rows[idx], label = INJECTORS[inj_name](rows[idx])
        ground_truth.setdefault(idx, []).append(label)

    # Inject ~3% duplicates
    n_dups = max(1, int(n_rows * 0.03))
    dup_sources = random.sample(range(n_rows - n_dups), n_dups)
    dup_rows    = []
    for src in dup_sources:
        dup_idx = len(rows) + len(dup_rows)
        dup_rows.append(dict(rows[src], id=dup_idx + 1))
        ground_truth[dup_idx] = ["duplicate"]
    rows.extend(dup_rows)

    # Write CSV
    csv_path = os.path.join(out_dir, f"dirty_{n_rows}.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    # Write ground truth
    gt_path = os.path.join(out_dir, f"ground_truth_{n_rows}.json")
    with open(gt_path, "w") as f:
        json.dump(ground_truth, f, indent=2)

    total_errors = sum(len(v) for v in ground_truth.values())
    print(f"  Generated {len(rows)} rows | {total_errors} injected errors → {csv_path}")
    return ground_truth


if __name__ == "__main__":
    sizes = [100, 500, 1_000, 5_000, 10_000, 50_000, 100_000]
    print("Generating benchmark datasets...")
    os.makedirs("benchmark_data", exist_ok=True)
    for n in sizes:
        generate(n, error_rate=0.20, out_dir="benchmark_data")
    print("Done.")