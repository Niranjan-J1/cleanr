import time
import uuid
import pandas as pd
from typing import Optional
from detector.models import CleaningReport
from detector.detectors.missing_values import MissingValuesDetector
from detector.detectors.duplicate_rows import DuplicateRowsDetector
from detector.detectors.date_format import DateFormatDetector
from detector.detectors.mixed_types import MixedTypesDetector
from detector.detectors.whitespace import WhitespaceDetector
from detector import nn_engine

DETECTORS = [
    MissingValuesDetector,
    DuplicateRowsDetector,
    DateFormatDetector,
    MixedTypesDetector,
    WhitespaceDetector,
]

def analyze_csv(filepath: str, filename: str, job_id: str) -> CleaningReport:
    start = time.time()

    df = pd.read_csv(filepath, dtype=str)
    df.columns = [col.strip() for col in df.columns]

    total_rows = len(df)
    total_cols = len(df.columns)

    # Run rule-based detectors
    issues = []
    for DetectorClass in DETECTORS:
        detector = DetectorClass(df)
        issues.extend(detector.detect())

    # Run NN engine (C++ binary)
    nn_issues = []
    try:
        nn_issues.extend(nn_engine.detect_anomalies(filepath, total_rows))
        nn_issues.extend(nn_engine.detect_fuzzy_duplicates(filepath, total_rows))
    except Exception as e:
        print(f"NN engine skipped: {e}")

    # Merge — NN issues go after rule-based, sorted by severity
    all_issues = issues + nn_issues
    severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    all_issues.sort(key=lambda i: severity_order.get(i.severity.value, 3))

    elapsed = int((time.time() - start) * 1000)

    return CleaningReport(
        job_id        = job_id,
        filename      = filename,
        rows_analyzed = total_rows,
        cols_analyzed = total_cols,
        issues        = all_issues,
        processing_ms = elapsed,
    )