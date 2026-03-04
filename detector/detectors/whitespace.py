# Detects leading/trailing whitespace and invisible characters.
# These cause silent bugs — "John " != "John" in joins and lookups.

from typing import List
import pandas as pd
from detector.detectors.base import BaseDetector
from detector.models import Issue, IssueType, Severity

class WhitespaceDetector(BaseDetector):

    def detect(self) -> List[Issue]:
        issues = []

        for col in self.df.columns:
            series = self.df[col].dropna().astype(str)

            if len(series) == 0:
                continue

            # Find values that have leading or trailing whitespace
            whitespace_mask = series != series.str.strip()
            affected = whitespace_mask.sum()

            if affected == 0:
                continue

            examples = list(
                series[whitespace_mask]
                .head(5)
                .apply(lambda v: repr(v))  # repr shows the spaces clearly e.g. 'John '
            )

            issues.append(Issue(
                issue_type    = IssueType.WHITESPACE,
                column        = col,
                severity      = Severity.LOW,
                affected_rows = int(affected),
                total_rows    = self.total_rows,
                examples      = examples,
                suggested_fix = f"Strip leading/trailing whitespace from {affected} values in '{col}'",
                confidence    = 1.0,
                auto_fixable  = True,
            ))

        return issues