import subprocess
import json
import os
import tempfile
import platform
from typing import Optional
from detector.models import Issue, IssueType, Severity, FixTier, FixOption

# Path to the compiled C++ binary
BINARY_NAME = "cleanr-engine.exe" if platform.system() == "Windows" else "cleanr-engine"
BINARY_PATH = os.path.join(os.path.dirname(__file__), "..", "api", BINARY_NAME)

def _run_engine(task: str, csv_path: str) -> Optional[dict]:
    """Call the C++ binary and return parsed JSON output."""
    if not os.path.exists(BINARY_PATH):
        print(f"Warning: C++ engine not found at {BINARY_PATH}")
        return None

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        output_path = tmp.name

    try:
        result = subprocess.run(
            [BINARY_PATH, task, csv_path, output_path],
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )

        if result.returncode != 0:
            print(f"C++ engine error: {result.stderr}")
            return None

        with open(output_path, "r") as f:
            return json.load(f)

    except subprocess.TimeoutExpired:
        print("C++ engine timed out")
        return None
    except Exception as e:
        print(f"C++ engine exception: {e}")
        return None
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def detect_anomalies(csv_path: str, total_rows: int) -> list[Issue]:
    """Run autoencoder anomaly detection and return Issue objects."""
    data = _run_engine("--anomalies", csv_path)
    if not data or not data.get("anomalies"):
        return []

    anomalies = data["anomalies"]
    if not anomalies:
        return []

    numeric_cols = data.get("numeric_columns", [])
    col_str = ", ".join(numeric_cols) if numeric_cols else "numeric columns"

    return [Issue(
        issue_type    = IssueType.ANOMALY,
        column        = None,
        severity      = Severity.HIGH,
        fix_tier      = FixTier.SUGGEST,
        affected_rows = len(anomalies),
        total_rows    = total_rows,
        examples      = [f"Row {a['row']} (score={round(a['score'], 3)})"
                        for a in anomalies[:5]],
        suggested_fix = f"{len(anomalies)} statistically anomalous rows detected across {col_str}",
        confidence    = round(min(a["score"] for a in anomalies), 3),
        fix_options   = [
            FixOption(label="Drop anomalous rows",
                     action="drop_rows",
                     preview=f"removes {len(anomalies)} rows"),
            FixOption(label="Keep and flag only",
                     action="keep",
                     preview="no change"),
        ]
    )]


def detect_fuzzy_duplicates(csv_path: str, total_rows: int) -> list[Issue]:
    """Run fuzzy deduplication and return Issue objects."""
    data = _run_engine("--fuzzy-dedup", csv_path)
    if not data or not data.get("duplicate_pairs"):
        return []

    pairs = data["duplicate_pairs"]
    if not pairs:
        return []

    # Group by column
    by_column = {}
    for p in pairs:
        col = p["column"]
        by_column.setdefault(col, []).append(p)

    issues = []
    for col, col_pairs in by_column.items():
        examples = [
            f"\"{p['value_a']}\" ≈ \"{p['value_b']}\" ({round(p['similarity']*100)}%)"
            for p in col_pairs[:4]
        ]
        issues.append(Issue(
            issue_type    = IssueType.FUZZY_DUPLICATE,
            column        = col,
            severity      = Severity.MEDIUM,
            fix_tier      = FixTier.FLAG_ONLY,
            affected_rows = len(col_pairs) * 2,
            total_rows    = total_rows,
            examples      = examples,
            suggested_fix = f"{len(col_pairs)} near-duplicate pairs found in '{col}' — review manually",
            confidence    = round(sum(p["similarity"] for p in col_pairs) / len(col_pairs), 3),
            fix_options   = []
        ))

    return issues


def get_imputation_suggestions(csv_path: str) -> dict:
    """Run regression imputation and return predicted values by row/column."""
    data = _run_engine("--impute", csv_path)
    if not data or not data.get("imputations"):
        return {}

    # Return as dict keyed by "column:row" for easy lookup
    result = {}
    for imp in data["imputations"]:
        key = f"{imp['column']}:{imp['row']}"
        result[key] = round(imp["predicted_value"], 4)

    return result