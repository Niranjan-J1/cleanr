from typing import List
import pandas as pd
from detector.detectors.base import BaseDetector
from detector.models import Issue, IssueType, Severity, FixTier

class WhitespaceDetector(BaseDetector):

    def detect(self) -> List[Issue]:
        issues = []

        for col in self.df.columns:
            series = self.df[col].dropna().astype(str)

            if len(series) == 0:
                continue

            whitespace_mask = series != series.str.strip()
            affected        = whitespace_mask.sum()

            if affected == 0:
                continue

            examples = list(
                series[whitespace_mask].head(5).apply(lambda v: repr(v))
            )

            issues.append(Issue(
                issue_type    = IssueType.WHITESPACE,
                column        = col,
                severity      = Severity.LOW,
                fix_tier      = FixTier.AUTO,
                affected_rows = int(affected),
                total_rows    = self.total_rows,
                examples      = examples,
                suggested_fix = f"Strip whitespace from {affected} values in '{col}'",
                confidence    = 1.0,
            ))

        return issues