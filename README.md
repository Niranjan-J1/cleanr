# CLEANR — AI-Powered CSV Data Cleaning Engine

**Live Demo:** [http://44.222.65.231:8000](http://44.222.65.231:8000)  
**Stack:** React · FastAPI · Python · C++17 · Docker · AWS EC2

---

## What is CLEANR?

CLEANR is a full-stack data cleaning platform that automatically detects and fixes data quality issues in CSV files. Upload a dirty CSV, review AI-generated fix recommendations per issue type, apply them with one click, and download a clean file — all in under a second for typical datasets.

---

## Features

| Feature | Description |
|---|---|
| Missing Values | Detects missing/null cells, recommends drop or fill (median/mode) per column type |
| Duplicate Rows | Finds exact and near-duplicate rows, ignoring ID-like columns |
| Date Format | Standardizes inconsistent date formats to ISO 8601 |
| Mixed Types | Detects columns with mixed numeric and string values |
| Whitespace | Strips leading/trailing whitespace from all string columns |
| Negative Values | Flags negative prices, quantities, and salaries |
| Anomaly Detection | C++17 autoencoder neural network detects statistical outliers (98.5% precision) |
| Fuzzy Deduplication | Levenshtein + Jaccard similarity catches near-duplicate records |
| Regression Imputation | Cross-column regression network predicts missing numeric values |

---

## Architecture
```
React Frontend (port 8000)
        │
        ▼
FastAPI Backend (/upload, /report, /fix, /download)
        │
        ├── Python Rule-Based Detectors (6 detectors)
        │       ├── MissingValuesDetector
        │       ├── DuplicateRowsDetector
        │       ├── DateFormatDetector
        │       ├── MixedTypesDetector
        │       ├── WhitespaceDetector
        │       └── NegativeValuesDetector
        │
        └── C++17 Neural Network Engine (subprocess)
                ├── Autoencoder (anomaly detection)
                ├── Fuzzy Deduplication (Levenshtein + Jaccard)
                └── Regression Imputation
```

---

## Benchmark Results

### Latency

<img width="1934" height="772" alt="image" src="https://github.com/user-attachments/assets/8f185e64-53bf-416f-9610-4410f025110b" />


| Rows | Total | Rows/sec |
|------|-------|----------|
| 1,000 | **128ms** | 8,074 |
| 10,000 | 818ms | 12,595 |
| 100,000 | **7.8s** | 13,257 |

### Performance vs Pandas Baseline

| Rows | Pandas | CLEANR | Speedup |
|------|--------|--------|---------|
| 10,000 | 2,591ms | 2,074ms | **1.25×** |
| 50,000 | 9,230ms | 8,470ms | **1.09×** |

### NN Anomaly Detection

| Rows | Precision | Recall | F1 |
|------|-----------|--------|----|
| 5,000 | **98.5%** | 27.6% | 0.431 |
| 10,000 | **99.2%** | 32.8% | 0.492 |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite |
| Backend | FastAPI, Uvicorn, Python 3.11 |
| Data | Pandas, NumPy, python-dateutil |
| ML Engine | C++17, CMake — zero external ML libraries |
| Infrastructure | Docker, AWS EC2, AWS S3, CloudFront |
| CI/CD | GitHub Actions |

---

## Running Locally

### Backend
```bash
git clone https://github.com/Niranjan-J1/cleanr.git
cd cleanr
python -m venv .venv
source .venv/bin/activate
pip install -r api/requirements.txt
uvicorn api.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### C++ Engine (for anomaly detection)
```bash
cd engine_nn
mkdir build && cd build
cmake ..
make
cp cleanr-engine ../../api/
```

---

## Running Benchmarks
```bash
pip install matplotlib
python benchmarks/run_all.py --skip-concurrency
```

---

## Project Structure
```
cleanr/
├── api/                    # FastAPI backend
├── detector/               # Python rule-based detectors
├── engine_nn/              # C++17 neural network engine
├── frontend/               # React + Vite UI
├── benchmarks/             # Benchmark suite
└── infra/                  # Docker + deployment config
```

---

## License

MIT
