# test_detector.py — run this to verify the detector works
# delete this file after testing

import sys
sys.path.insert(0, ".")

from detector.engine import analyze_csv

report = analyze_csv("test_data.csv", "test_data.csv", "test-job-001")
import json
print(json.dumps(report.to_dict(), indent=2))
