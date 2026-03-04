# Detects columns where the data type is inconsistent.
# e.g. a column that's mostly numbers but has some strings mixed in.
# This breaks any downstream numeric analysis.

from typing import List
import pandas as pd
from detector.detectors.base import BaseDetector
from detector.models import Issue, IssueType, Severity

def is_numeric(value: str) -> bool:
    try:
        float(value.replace(",", "").replace("$", "").replace("%", "").strip())
        return True
    except:
        return False

class MixedTypesDetector(BaseDetector):

    def detect(self) -> List[Issue]:
        issues = []

        for col in self.df.columns:
            series = self.df[col].dropna().astype(str)
            series = series[series.str.strip() != ""]

            if len(series) < 5:
                continue

            numeric_count = sum(1 for v in series if is_numeric(v))
            numeric_ratio = numeric_count / len(series)

            # Only flag if the column is mostly numeric but not entirely
            # If it's less than 50% numeric it's probably just a string column
            if numeric_ratio < 0.5 or numeric_ratio == 1.0:
                continue

            # The non-numeric values are the problem
            non_numeric = [v for v in series if not is_numeric(v)]
            affected = len(non_numeric)

            issues.append(Issue(
                issue_type    = IssueType.MIXED_TYPES,
                column        = col,
                severity      = Severity.HIGH,
                affected_rows = int(affected),
                total_rows    = self.total_rows,
                examples      = non_numeric[:5],
                suggested_fix = f"Column '{col}' is {round(numeric_ratio*100)}% numeric — coerce to float, null non-numeric values",
                confidence    = round(numeric_ratio, 2),
                auto_fixable  = True,
            ))

        return issues