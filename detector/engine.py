#This is what FAST API calls, Loads the CSV colletcs all the sissues and then retruns the cleanifn report

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

DETECTORS = [
    MissingValuesDetector,
    DuplicateRowsDetector,
    DateFormatDetector,
    MixedTypesDetector,
    WhitespaceDetector,
]

def analyze_csv(filepath: str, filename: str, job_id: Optional[str] = None) -> CleaningReport:
    start = time.time()

    if job_id is None:
        job_id = str(uuid.uuid4())

    df = pd.read_csv(filepath, dtype=str)

    report = CleaningReport(
        job_id        = job_id,
        filename      = filename,
        rows_analyzed = len(df),
        cols_analyzed = len(df.columns),
    )

    for DetectorClass in DETECTORS:
        detector = DetectorClass(df)
        issues   = detector.detect()
        report.issues.extend(issues)

    severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    report.issues.sort(key=lambda i: severity_order[i.severity.value])

    report.processing_ms = int((time.time() - start) * 1000)

    return report