from typing import List
import pandas as pd
from detector.detectors.base import BaseDetector
from detector.models import Issue, IssueType, Severity, FixTier, FixOption

class NegativeValuesDetector(BaseDetector):

    def detect(self) -> List[Issue]:
        issues = []

        # Columns where negative values are never valid
        price_hints    = {"price", "cost", "amount", "fee", "salary", "revenue", "total"}
        quantity_hints = {"quantity", "qty", "count", "units", "stock"}

        for col in self.df.columns:
            col_lower = col.lower()
            is_price    = any(h in col_lower for h in price_hints)
            is_quantity = any(h in col_lower for h in quantity_hints)

            if not (is_price or is_quantity):
                continue

            numeric = pd.to_numeric(self.df[col], errors='coerce')
            neg_mask = numeric < 0
            affected = neg_mask.sum()

            if affected == 0:
                continue

            examples = []
            for _, row in self.df[neg_mask].head(3).iterrows():
                examples.append(f"Row {row.name} ({col}={row[col]})")

            issues.append(Issue(
                issue_type    = IssueType.NEGATIVE_VALUES,
                column        = col,
                severity      = Severity.HIGH,
                fix_tier      = FixTier.SUGGEST,
                affected_rows = int(affected),
                total_rows    = self.total_rows,
                examples      = examples,
                suggested_fix = f"{affected} negative values in '{col}' — likely data entry errors",
                confidence    = 0.95,
                fix_options   = [
                    FixOption(label="Drop rows with negative values",
                             action="drop_rows",
                             preview=f"removes {int(affected)} rows"),
                    FixOption(label="Convert to absolute value",
                             action="abs_values",
                             preview="e.g. -15.00 → 15.00"),
                    FixOption(label="Keep and flag only",
                             action="keep",
                             preview="no change"),
                ],
            ))

        return issues