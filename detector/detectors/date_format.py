from typing import List
import pandas as pd
from dateutil import parser as dateparser
from detector.detectors.base import BaseDetector
from detector.models import Issue, IssueType, Severity, FixTier

def looks_like_date(value: str) -> bool:
    try:
        dateparser.parse(value, fuzzy=False)
        return True
    except:
        return False

def get_format_signature(value: str) -> str:
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

            sample     = series.sample(min(20, len(series)), random_state=42)
            date_count = sum(1 for v in sample if looks_like_date(v))
            date_ratio = date_count / len(sample)

            if date_ratio < 0.7:
                continue

            formats_seen = {}
            for value in series:
                sig = get_format_signature(value)
                formats_seen[sig] = formats_seen.get(sig, 0) + 1

            if len(formats_seen) <= 1:
                continue

            affected = len(series) - max(formats_seen.values())
            examples = list(series.sample(min(5, len(series)), random_state=1))

            issues.append(Issue(
                issue_type    = IssueType.DATE_FORMAT,
                column        = col,
                severity      = Severity.HIGH,
                fix_tier      = FixTier.AUTO,   # format normalization is unambiguous
                affected_rows = int(affected),
                total_rows    = self.total_rows,
                examples      = examples,
                suggested_fix = f"Normalize all dates in '{col}' to ISO 8601: YYYY-MM-DD",
                confidence    = round(date_ratio, 2),
            ))

        return issues