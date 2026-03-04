from typing import List
import pandas as pd
from detector.detectors.base import BaseDetector
from detector.models import Issue, IssueType, Severity, FixTier, FixOption

DISGUISED_NULLS = {
    "n/a", "na", "none", "null", "nil", "nan",
    "-", "--", "?", "unknown", "missing", "blank", ""
}

class MissingValuesDetector(BaseDetector):

    def detect(self) -> List[Issue]:
        issues = []

        for col in self.df.columns:
            series = self.df[col]
            null_mask      = series.isna()
            disguised_mask = series.astype(str).str.strip().str.lower().isin(DISGUISED_NULLS)
            combined_mask  = null_mask | disguised_mask
            affected       = combined_mask.sum()

            if affected == 0:
                continue

            examples = list(
                series[disguised_mask & ~null_mask].astype(str).unique()[:5]
            )
            if not examples:
                examples = ["(empty)"]

            pct = affected / self.total_rows
            if pct > 0.3:
                severity = Severity.HIGH
            elif pct > 0.05:
                severity = Severity.MEDIUM
            else:
                severity = Severity.LOW

            # Build fix options based on column type
            fix_options = self._build_fix_options(series, combined_mask, col)

            issues.append(Issue(
                issue_type    = IssueType.MISSING_VALUES,
                column        = col,
                severity      = severity,
                fix_tier      = FixTier.SUGGEST,   # always suggest, never auto
                affected_rows = int(affected),
                total_rows    = self.total_rows,
                examples      = examples,
                suggested_fix = f"{affected} missing values detected in '{col}'",
                confidence    = 0.99,
                fix_options   = fix_options,
            ))

        return issues

    def _build_fix_options(self, series, missing_mask, col_name) -> List[FixOption]:
        options = []

        # Check if column is numeric
        clean = series[~missing_mask]
        numeric = pd.to_numeric(clean, errors='coerce')
        is_numeric = numeric.notna().sum() / max(len(clean), 1) > 0.7

        if is_numeric:
            median = round(numeric.median(), 2)
            mean   = round(numeric.mean(), 2)
            options.append(FixOption(
                label   = f"Fill with median ({median})",
                action  = "fill_median",
                preview = str(median)
            ))
            options.append(FixOption(
                label   = f"Fill with mean ({mean})",
                action  = "fill_mean",
                preview = str(mean)
            ))
        else:
            # Categorical
            mode_vals = clean.astype(str).mode()
            if len(mode_vals) > 0:
                mode = mode_vals[0]
                options.append(FixOption(
                    label   = f"Fill with most common value ('{mode}')",
                    action  = "fill_mode",
                    preview = mode
                ))

        options.append(FixOption(
            label   = "Leave empty (keep as blank)",
            action  = "leave_empty",
            preview = ""
        ))
        options.append(FixOption(
            label   = "Drop rows with missing values",
            action  = "drop_rows",
            preview = f"removes {int(missing_mask.sum())} rows"
        ))

        return options