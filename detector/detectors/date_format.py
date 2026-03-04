# Detects columns that have inconsistent date formats.
# e.g. some rows say "01/15/2023" and others say "2023-01-15"
# Uses dateutil to try parsing every value and tracks what formats appear.

from typing import List
import pandas as pd
from dateutil import parser as dateparser
from detector.detectors.base import BaseDetector
from detector.models import Issue, IssueType, Severity

# If a column name contains any of these words we prioritize it as a date column
DATE_COLUMN_HINTS = {"date", "time", "created", "updated", "modified", "at", "on", "day"}

def looks_like_date(value: str) -> bool:
    try:
        dateparser.parse(value, fuzzy=False)
        return True
    except:
        return False

def get_format_signature(value: str) -> str:
    # Returns a rough signature of the format so we can detect inconsistency
    # e.g. "2023-01-15" -> "YYYY-MM-DD", "01/15/2023" -> "MM/DD/YYYY"
    value = value.strip()
    if "-" in value and value.index("-") == 4:
        return "YYYY-MM-DD"
    elif "/" in value:
        parts = value.split("/")
        if len(parts) == 3:
            if len(parts[2]) == 4:
                return "MM/DD/YYYY"
            elif len(parts[0]) == 4:
                return "YYYY/MM/DD"
    elif " " in value:
        return "MONTH DD YYYY"
    return "OTHER"

class DateFormatDetector(BaseDetector):

    def detect(self) -> List[Issue]:
        issues = []

        for col in self.df.columns:
            series = self.df[col].dropna().astype(str)
            series = series[series.str.strip() != ""]

            if len(series) == 0:
                continue

            # Check if this looks like a date column
            # Sample up to 20 values and see how many parse as dates
            sample = series.sample(min(20, len(series)), random_state=42)
            date_count = sum(1 for v in sample if looks_like_date(v))
            date_ratio = date_count / len(sample)

            # Skip if less than 70% of sampled values look like dates
            if date_ratio < 0.7:
                continue

            # Now check format consistency across all values
            formats_seen = {}
            for value in series:
                sig = get_format_signature(value)
                formats_seen[sig] = formats_seen.get(sig, 0) + 1

            # If only one format, no problem
            if len(formats_seen) <= 1:
                continue

            affected = len(series) - max(formats_seen.values())
            examples = list(series.sample(min(5, len(series)), random_state=1))

            issues.append(Issue(
                issue_type    = IssueType.DATE_FORMAT,
                column        = col,
                severity      = Severity.HIGH,
                affected_rows = int(affected),
                total_rows    = self.total_rows,
                examples      = examples,
                suggested_fix = f"Normalize all dates in '{col}' to ISO 8601 format: YYYY-MM-DD",
                confidence    = round(date_ratio, 2),
                auto_fixable  = True,
            ))

        return issues