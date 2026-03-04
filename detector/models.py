#finds the issues that go into the cleaning report


from dataclasses import dataclass,field 
from typing import List, Optional 
from enum import Enum 


class Severity(Enum):
    HIGH   = "HIGH"
    MEDIUM = "MEDIUM"
    LOW    = "LOW"

class IssueType(Enum):
    MISSING_VALUES         = "MISSING_VALUES"
    DATE_FORMAT            = "DATE_FORMAT_INCONSISTENT"
    DUPLICATE_ROWS         = "DUPLICATE_ROWS"
    MIXED_TYPES            = "MIXED_TYPES"
    TYPO_CATEGORICAL       = "TYPO_CATEGORICAL"
    OUTLIER_NUMERIC        = "OUTLIER_NUMERIC"
    INVALID_EMAIL          = "INVALID_EMAIL"
    INVALID_PHONE          = "INVALID_PHONE"
    WHITESPACE             = "WHITESPACE"
    CASE_INCONSISTENCY     = "CASE_INCONSISTENCY"
    NUMERIC_AS_STRING      = "NUMERIC_AS_STRING"
    HEADER_ISSUES          = "HEADER_ISSUES"

@dataclass 
class Issue:
    issue_type:     IssueType
    column:         Optional[str]      # None if row-level issue (e.g. duplicates)
    severity:       Severity
    affected_rows:  int
    total_rows:     int
    examples:       List[str]          # sample bad values so user can see them
    suggested_fix:  str                # human readable description of fix
    confidence:     float              # 0.0 - 1.0
    auto_fixable:   bool = True        # can we fix this without user input?

    def to_dict(self) -> dict:
        return {
            "issue_type":    self.issue_type.value,
            "column":        self.column,
            "severity":      self.severity.value,
            "affected_rows": self.affected_rows,
            "total_rows":    self.total_rows,
            "affected_pct":  round(self.affected_rows / self.total_rows * 100, 1),
            "examples":      self.examples,
            "suggested_fix": self.suggested_fix,
            "confidence":    self.confidence,
            "auto_fixable":  self.auto_fixable,
        }

@dataclass
class CleaningReport:
    job_id:          str
    filename:        str
    rows_analyzed:   int
    cols_analyzed:   int
    issues:          List[Issue] = field(default_factory=list)
    processing_ms:   int = 0

    def to_dict(self) -> dict:
        return {
            "job_id":        self.job_id,
            "filename":      self.filename,
            "rows_analyzed": self.rows_analyzed,
            "cols_analyzed": self.cols_analyzed,
            "total_issues":  len(self.issues),
            "issues":        [i.to_dict() for i in self.issues],
            "processing_ms": self.processing_ms,
        }   