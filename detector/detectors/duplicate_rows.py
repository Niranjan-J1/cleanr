from typing import List
import pandas as pd
from detector.detectors.base import BaseDetector
from detector.models import Issue, IssueType, Severity, FixTier

class DuplicateRowsDetector(BaseDetector):

 def detect(self) -> List[Issue]:
    issues = []

    df_clean = self.df.copy()
    df_clean.columns = [c.strip() for c in df_clean.columns]
    df_clean = df_clean.apply(
        lambda col: col.str.strip() if col.dtype == object else col
    )

    # Exclude id-like columns from duplicate check
    # Two rows that are identical except for an auto-generated ID are still duplicates
    id_hints = {"id", "index", "row", "num", "number", "key"}
    cols_to_check = [
        c for c in df_clean.columns
        if not any(hint in c.lower() for hint in id_hints)
    ]

    duplicate_mask = df_clean[cols_to_check].duplicated(keep='first')
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
        fix_tier      = FixTier.AUTO,
        affected_rows = int(affected),
        total_rows    = self.total_rows,
        examples      = examples,
        suggested_fix = f"Remove {affected} duplicate rows (ignoring ID column), keep first occurrence",
        confidence    = 1.0,
    ))

    return issues