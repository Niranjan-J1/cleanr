#Every detetctor inherits from this class, forces consistatn interface, each detetctor returns a list of issue 

from abc import ABC, abstractmethod
from typing import List
import pandas as pd
from detector.models import Issue


class BaseDetector(ABC):

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.total_rows = len(df)

    @abstractmethod
    def detect(self) -> List[Issue]:
        # Each subclass implements this
        pass

    def sample_values(self, values, n=5) -> List[str]:
        # Returns up to n example values as strings for the report
        unique = list(set(str(v) for v in values if v != ""))
        return unique[:n]