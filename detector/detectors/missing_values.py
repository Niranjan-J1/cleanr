#detetcst missing, null and disguised null values --> things like NA none or somethothing that is tehcnically not empty but is 

from typing import List
import pandas as pd
from detector.detectors.base import BaseDetector
from detector.models import Issue, IssueType, Severity


# Values that look like data but actually mean "nothing"
DISGUISED_NULLS = {
    "n/a", "na", "none", "null", "nil", "nan",
    "-", "--", "?", "unknown", "missing", "blank", ""
}

class MissingValuesDetector(BaseDetector):

    def detect(self) -> List[Issue]:
        issues = []

        for col in self.df.columns:
            series = self.df[col]

            # Find true nulls
            null_mask = series.isna()

            # Find disguised nulls — values that look like data but mean nothing
            disguised_mask = series.astype(str).str.strip().str.lower().isin(DISGUISED_NULLS)

            combined_mask = null_mask | disguised_mask
            affected = combined_mask.sum()

            if affected == 0:
                continue

            # Collect examples of what the disguised nulls look like
            examples = list(
                series[disguised_mask & ~null_mask]
                .astype(str).unique()[:5]
            )
            if not examples:
                examples = ["(empty)"]

            # Severity based on how much of the column is missing
            pct = affected / self.total_rows
            if pct > 0.3:
                severity = Severity.HIGH
            elif pct > 0.05:
                severity = Severity.MEDIUM
            else:
                severity = Severity.LOW

            issues.append(Issue(
                issue_type    = IssueType.MISSING_VALUES,
                column        = col,
                severity      = severity,
                affected_rows = int(affected),
                total_rows    = self.total_rows,
                examples      = examples,
                suggested_fix = f"Impute {affected} missing values using column median/mode",
                confidence    = 0.99,
                auto_fixable  = True,
            ))

        return issues