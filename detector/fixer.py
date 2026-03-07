import pandas as pd
from dateutil import parser as dateparser
from detector.models import CleaningReport, IssueType, FixTier

DISGUISED_NULLS = {
    "n/a", "na", "none", "null", "nil", "nan",
    "-", "--", "?", "unknown", "missing", "blank", ""
}

class Fixer:

    def __init__(self, df: pd.DataFrame, report: CleaningReport,
                 user_selections: dict = None):
        self.df              = df.copy()
        self.report          = report
        self.user_selections = user_selections or {}

    def _fix_headers(self):
        self.df.columns = [col.strip() for col in self.df.columns]

    def apply_all(self) -> pd.DataFrame:
        self._fix_headers()

        # Run whitespace fixes FIRST so duplicate detection works correctly
        for issue in self.report.issues:
            if issue.fix_tier == FixTier.AUTO and issue.issue_type == IssueType.WHITESPACE:
                self._fix_whitespace(issue.column)

        # Now run remaining auto fixes
        for issue in self.report.issues:
            if issue.fix_tier == FixTier.AUTO and issue.issue_type != IssueType.WHITESPACE:
                self._apply_auto(issue)

        # Run suggestion fixes
        for issue in self.report.issues:
            if issue.fix_tier == FixTier.SUGGEST:
                key    = f"{issue.column}:{issue.issue_type.value}"
                action = self.user_selections.get(key)
                if action:
                    self._apply_suggestion(issue, action)

        # Drop rows where Name is empty after all fixes
        if "Name" in self.df.columns:
            self.df = self.df[
                self.df["Name"].astype(str).str.strip().apply(
                    lambda v: v.lower() not in DISGUISED_NULLS and v != "nan"
                )
            ].reset_index(drop=True)

        # Clean up float formatting (34.0 → 34) — run last
        self._clean_float_formatting()

        return self.df

    def _clean_float_formatting(self):
        for col in self.df.columns:
            try:
                numeric = pd.to_numeric(self.df[col], errors='coerce')
                if numeric.notna().sum() == 0:
                    continue
                # Only convert if ALL non-null values are whole numbers
                whole = numeric.dropna().apply(
                    lambda x: float(x) == int(float(x))
                ).all()
                if whole:
                    self.df[col] = self.df[col].apply(
                        lambda x: str(int(float(x)))
                        if x is not None
                        and str(x).strip().lower() not in DISGUISED_NULLS
                        and _is_numeric(x)
                        else x
                    )
            except:
                pass

    def _apply_auto(self, issue):
        if issue.issue_type == IssueType.DUPLICATE_ROWS:
            self._fix_duplicates()
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
        elif issue.issue_type == IssueType.NEGATIVE_VALUES: 
            self._fix_negative_values(col, action)

    # --- AUTO fixes ---

    def _fix_duplicates(self):
        df_stripped = self.df.apply(
            lambda col: col.str.strip() if col.dtype == object else col
        )
        id_hints = {"id", "index", "row", "num", "number", "key"}
        cols_to_check = [
            c for c in df_stripped.columns
            if not any(hint in c.lower() for hint in id_hints)
        ]
        mask = df_stripped[cols_to_check].duplicated(keep='first')
        self.df = self.df[~mask].reset_index(drop=True)

    def _fix_whitespace(self, column: str):
        if column in self.df.columns:
            self.df[column] = self.df[column].astype(str).str.strip()

    def _fix_dates(self, column: str):
        if column not in self.df.columns:
            return

        def normalize(value):
            val = str(value).strip()
            if "9999" in val or "99-99" in val:
                return value
            try:
                parsed = dateparser.parse(val, fuzzy=False, dayfirst=True)  # ← add dayfirst=True
                if parsed.year > 2100 or parsed.year < 1900:
                    return value
                return parsed.strftime("%Y-%m-%d")
            except:
                return value

        self.df[column] = self.df[column].apply(normalize)

    # --- SUGGEST fixes ---

    def _fix_missing(self, column: str, action: str):
        if column not in self.df.columns:
            return

        self.df[column] = self.df[column].apply(
            lambda v: None if str(v).strip().lower() in DISGUISED_NULLS else v
        )

        if action == "fill_median":
            numeric = pd.to_numeric(self.df[column], errors='coerce')
            median  = numeric.median()
            # Keep as integer if the column contains whole numbers
            if float(median) == int(float(median)):
                fill_val = str(int(median))
            else:
                fill_val = str(round(median, 2))
            self.df[column] = self.df[column].fillna(fill_val)

        elif action == "fill_mean":
            numeric  = pd.to_numeric(self.df[column], errors='coerce')
            mean_val = numeric.mean()
            if float(mean_val) == int(float(mean_val)):
                fill_val = str(int(mean_val))
            else:
                fill_val = str(round(mean_val, 2))
            self.df[column] = self.df[column].fillna(fill_val)

        elif action == "fill_mode":
            mode = self.df[column].dropna().mode()
            if len(mode) > 0:
                self.df[column] = self.df[column].fillna(mode[0])

        elif action == "drop_rows":
            self.df = self.df[self.df[column].notna()].reset_index(drop=True)

        elif action == "leave_empty":
            pass

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
            mask = self.df[column].apply(_is_numeric)
            self.df = self.df[mask].reset_index(drop=True)
        elif action == "keep_as_text":
            pass

    def _fix_anomaly(self, action: str, issue):
        if action == "drop_rows":
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

    def _fix_negative_values(self, column: str, action: str):
        if column not in self.df.columns:
            return
        numeric = pd.to_numeric(self.df[column], errors='coerce')
        if action == "drop_rows":
            self.df = self.df[~(numeric < 0)].reset_index(drop=True)
        elif action == "abs_values":
            self.df[column] = numeric.abs().apply(
                lambda x: str(int(x)) if x == int(x) else str(round(x, 2))
                if pd.notna(x) else self.df.loc[self.df.index[0], column]
            )

# --- Helper ---
def _is_numeric(v):
    try:
        float(str(v).replace(",", "").replace("$", "").strip())
        return True
    except:
        return False
    
