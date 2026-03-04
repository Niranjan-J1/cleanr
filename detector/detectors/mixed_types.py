from typing import List
import pandas as pd
from detector.detectors.base import BaseDetector
from detector.models import Issue, IssueType, Severity, FixTier, FixOption

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

            if numeric_ratio < 0.5 or numeric_ratio == 1.0:
                continue

            non_numeric   = [v for v in series if not is_numeric(v)]
            affected      = len(non_numeric)

            issues.append(Issue(
                issue_type    = IssueType.MIXED_TYPES,
                column        = col,
                severity      = Severity.HIGH,
                fix_tier      = FixTier.SUGGEST,
                affected_rows = int(affected),
                total_rows    = self.total_rows,
                examples      = non_numeric[:5],
                suggested_fix = f"'{col}' is {round(numeric_ratio*100)}% numeric — {affected} non-numeric values need a decision",
                confidence    = round(numeric_ratio, 2),
                fix_options   = [
                    FixOption(
                        label   = "Set non-numeric values to empty",
                        action  = "coerce_null",
                        preview = "blank"
                    ),
                    FixOption(
                        label   = "Drop rows with non-numeric values",
                        action  = "drop_rows",
                        preview = f"removes {affected} rows"
                    ),
                    FixOption(
                        label   = "Keep as text column",
                        action  = "keep_as_text",
                        preview = "no change"
                    ),
                ]
            ))

        return issues