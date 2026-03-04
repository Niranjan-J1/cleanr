import sys, json
sys.path.insert(0, ".")

from detector.engine import analyze_csv
from detector.fixer import Fixer
import pandas as pd

# Step 1 — analyze
report = analyze_csv("test_data.csv", "test_data.csv", "test-job-001")
print("=== ISSUES FOUND ===")
print(json.dumps(report.to_dict(), indent=2))

# Step 2 — simulate user selections for SUGGEST tier issues
# In the real app these come from the frontend
user_selections = {
    "age:MISSING_VALUES":    "fill_median",
    "email:MISSING_VALUES":  "fill_mode",
    "salary:MIXED_TYPES":    "coerce_null",  # Bob Jones stays empty, not invented
}

# Step 3 — fix
df = pd.read_csv("test_data.csv", dtype=str)
fixer = Fixer(df, report, user_selections)
clean_df = fixer.apply_all()

print("\n=== CLEAN CSV ===")
print(clean_df.to_string())

clean_df.to_csv("test_data_clean.csv", index=False)
print("\n✓ Saved to test_data_clean.csv")