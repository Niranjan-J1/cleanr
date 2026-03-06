import pandas as pd
from dateutil import parser as dateparser
from detector.models import CleaningReport, IssueType, FixTier, FixOption

DISGUISED_NULLS = {
    "n/a", "na", "none", "null", "nil", "nan",
    "-", "--", "?", "unknown", "missing", "blank", ""
}

class Fixer:

    def __init__(self, df: pd.DataFrame, report: CleaningReport,
                 user_selections: dict = None):
        self.df               = df.copy()
        self.report           = report
        # user_selections: { "column_name:ISSUE_TYPE": "action" }
        # e.g. { "age:MISSING_VALUES": "fill_median", "salary:MIXED_TYPES": "drop_rows" }
        self.user_selections  = user_selections or {}

    def _fix_headers(self):
        # Strip whitespace from column names and normalize
        self.df.columns = [col.strip() for col in self.df.columns]

    def apply_all(self) -> pd.DataFrame:
        self._fix_headers()
        for issue in self.report.issues:

            if issue.fix_tier == FixTier.AUTO:
                # Apply automatically, no user input needed
                self._apply_auto(issue)

            elif issue.fix_tier == FixTier.SUGGEST:
                # Only apply if user made a selection
                key    = f"{issue.column}:{issue.issue_type.value}"
                action = self.user_selections.get(key)
                if action:
                    self._apply_suggestion(issue, action)
                # If no selection, leave the data untouched

        return self.df

    def _apply_auto(self, issue):
        if issue.issue_type == IssueType.DUPLICATE_ROWS:
            self._fix_duplicates()
        elif issue.issue_type == IssueType.WHITESPACE:
            self._fix_whitespace(issue.column)
        elif issue.issue_type == IssueType.DATE_FORMAT:
            self._fix_dates(issue.column)

    def _apply_suggestion(self, issue, action: str):
        col = issue.column

        if issue.issue_type == IssueType.MISSING_VALUES:
            self._fix_missing(col, action)

        elif issue.issue_type == IssueType.MIXED_TYPES:
            self._fix_mixed_types(col, action)
        elif issue.issue_type == IssueType.ANOMALY:
            self._fix_anomaly(action, issue)

    def _fix_anomaly(self, action: str, issue):
        if action == "drop_rows":
            # Parse row indices from examples
            # Examples format: "Row 8 (score=0.293)"
            rows_to_drop = []
            for example in issue.examples:
                try:
                    row_num = int(example.split("Row ")[1].split(" ")[0])
                    rows_to_drop.append(row_num)
                except:
                    pass
            if rows_to_drop:
                self.df = self.df.drop(index=rows_to_drop, errors='ignore')
                self.df = self.df.reset_index(drop=True)

    # --- AUTO fixes ---

    def _fix_duplicates(self):
        self.df = self.df.drop_duplicates(keep='first').reset_index(drop=True)

    def _fix_whitespace(self, column: str):
        if column in self.df.columns:
            self.df[column] = self.df[column].astype(str).str.strip()

    def _fix_dates(self, column: str):
        if column not in self.df.columns:
            return
        def normalize(value):
            try:
                return dateparser.parse(str(value), fuzzy=False).strftime("%Y-%m-%d")
            except:
                return value
        self.df[column] = self.df[column].apply(normalize)

    # --- SUGGEST fixes ---

    def _fix_missing(self, column: str, action: str):
        if column not in self.df.columns:
            return

        # Replace disguised nulls with real NaN first
        self.df[column] = self.df[column].apply(
            lambda v: None if str(v).strip().lower() in DISGUISED_NULLS else v
        )

        if action == "fill_median":
            numeric = pd.to_numeric(self.df[column], errors='coerce')
            self.df[column] = numeric.fillna(numeric.median()).astype(str)

        elif action == "fill_mean":
            numeric = pd.to_numeric(self.df[column], errors='coerce')
            self.df[column] = numeric.fillna(numeric.mean()).astype(str)

        elif action == "fill_mode":
            mode = self.df[column].dropna().mode()
            if len(mode) > 0:
                self.df[column] = self.df[column].fillna(mode[0])

        elif action == "drop_rows":
            self.df = self.df[self.df[column].notna()].reset_index(drop=True)

        elif action == "leave_empty":
            pass  # already NaN, nothing to do

    def _fix_mixed_types(self, column: str, action: str):
        if column not in self.df.columns:
            return

        if action == "coerce_null":
            self.df[column] = pd.to_numeric(
                self.df[column].astype(str)
                    .str.replace(",", "").str.replace("$", "").str.strip(),
                errors='coerce'
            )

        elif action == "drop_rows":
            def is_numeric(v):
                try:
                    float(str(v).replace(",","").replace("$","").strip())
                    return True
                except:
                    return False
            mask = self.df[column].apply(is_numeric)
            self.df = self.df[mask].reset_index(drop=True)

        elif action == "keep_as_text":
            pass  # no change