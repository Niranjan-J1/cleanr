from typing import List
import pandas as pd
from detector.detectors.base import BaseDetector
from detector.models import Issue, IssueType, Severity, FixTier

class DuplicateRowsDetector(BaseDetector):

    def detect(self) -> List[Issue]:
        issues = []

        duplicate_mask = self.df.duplicated(keep='first')
        affected = duplicate_mask.sum()

        if affected == 0:
            return issues

        examples = []
        for _, row in self.df[duplicate_mask].head(3).iterrows():
            examples.append(" | ".join(str(v) for v in row.values[:4]))

        issues.append(Issue(
            issue_type    = IssueType.DUPLICATE_ROWS,
            column        = None,
            severity      = Severity.HIGH,
            fix_tier      = FixTier.AUTO,   # duplicates are certain, just remove them
            affected_rows = int(affected),
            total_rows    = self.total_rows,
            examples      = examples,
            suggested_fix = f"Remove {affected} duplicate rows, keep first occurrence",
            confidence    = 1.0,
        ))

        return issues