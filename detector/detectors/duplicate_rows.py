#finds exact duplicate rows 

from typing import List
import pandas as pd
from detector.detectors.base import BaseDetector
from detector.models import Issue, IssueType, Severity

class DuplicateRowsDetector(BaseDetector):

    def detect(self) -> List[Issue]:
        issues = []

        # keep=False marks ALL copies of a duplicate, including the first
        # keep='first' marks only the copies after the first occurrence
        duplicate_mask = self.df.duplicated(keep='first')
        affected = duplicate_mask.sum()

        if affected == 0:
            return issues

        # Show a couple example duplicate rows so user can verify
        examples = []
        dup_rows = self.df[duplicate_mask].head(3)
        for _, row in dup_rows.iterrows():
            examples.append(" | ".join(str(v) for v in row.values[:4]))

        issues.append(Issue(
            issue_type    = IssueType.DUPLICATE_ROWS,
            column        = None,           # row-level issue, not column-level
            severity      = Severity.HIGH,
            affected_rows = int(affected),
            total_rows    = self.total_rows,
            examples      = examples,
            suggested_fix = f"Remove {affected} duplicate rows, keep first occurrence",
            confidence    = 1.0,            # duplicates are certain, no guessing
            auto_fixable  = True,
        ))

        return issues