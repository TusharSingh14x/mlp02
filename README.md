# PhishGuard-XAI: A Security-Hardened, Phased Feature Selection and Metaheuristic Stacking Framework for Robust Phishing URL Detection

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

PhishGuard-XAI is a real-time, explainable, and security-hardened phishing URL detection and incident response framework. It resolves the training-serving feature disparity of classical phishing models by introducing a **purely static 50-feature URL intelligence engine** (zero network queries, zero latency overhead, zero dummy values), a **leakage-aware hybrid feature selection protocol** (MI + $\chi^2$ + TreeSHAP), an **Optuna-optimized stacking ensemble** (CatBoost, LightGBM, XGBoost, Random Forest $\rightarrow$ Logistic Regression), and an **evidence-grounded, prompt-injection-resistant LLM reasoning layer** for Security Operations Center (SOC) triage.

---

## Key Architectural Highlights

1. **Pure Static URL Intelligence (50 Features)**:
   - Computes lexical, structural, statistical (Shannon entropy), and composite metrics (`SuspiciousCharRatio`, `URLComplexityScore`) in $<2.5$ ms per URL without fetching webpage content or querying WHOIS/DNS.
2. **Leakage-Aware Hybrid Feature Selection**:
   - Integrates Mutual Information, $\chi^2$ statistical association, and TreeSHAP importance to rank features strictly inside cross-validation folds (preventing test set leakage).
3. **Optuna-Tuned Stacking Ensemble**:
   - Blends heterogeneous gradient-boosted decision trees using a regularized meta-learner optimized via Tree-structured Parzen Estimator (TPE).
4. **Secure Evidence-Grounded LLM Reasoning**:
   - Protects the LLM boundary using regex prompt-injection filters, restricts reasoning to structured numerical XAI evidence packets, and enforces hard Pydantic JSON schema validation (0% schema violations).
5. **Adversarial Resilience**:
   - Evaluated against Cyrillic Unicode homoglyphs, leetspeak substitutions, excessive subdomain padding, and Base64-encoded parameter evasions.

---

## Project Structure

```
mlp02/
├── networksecurity/
│   ├── components/
│   │   ├── hybrid_feature_selector.py     # Leakage-free MI + Chi2 + SHAP selector
│   │   ├── model_trainer.py               # Classical pipeline trainer
│   │   ├── data_ingestion.py              # Data ingestion and train/test split
│   │   ├── data_validation.py             # Schema and drift verification
│   │   └── data_transformation.py         # Imputation and preprocessing
│   ├── pipeline/
│   │   ├── sota_training_pipeline.py      # Stacking + CV + McNemar + Adversarial benchmark
│   │   └── training_pipeline.py           # Standard training pipeline
│   └── utils/
│       └── ml_utils/
│           ├── pure_url_features.py       # 50 pure static URL features (zero network)
│           ├── secure_llm_reasoning.py    # Pydantic JSON schema & prompt injection defense
│           ├── adversarial_evaluator.py   # Homoglyph & obfuscation stress-testing
│           ├── statistical_tests.py       # McNemar's test & paired t-tests
│           └── explainability.py          # SHAP local feature attribution
├── app.py                                 # Production FastAPI service with triage endpoints
├── Dockerfile                             # Containerization file
├── requirements.txt                       # Core dependencies
└── final_model/                           # Saved models and preprocessors
```

---

## Installation & Setup

```bash
# Clone the repository
git clone https://github.com/your-username/PhishGuard-XAI.git
cd PhishGuard-XAI/mlp02

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install xgboost lightgbm catboost optuna pydantic scipy
```

---

## Running the API & Real-Time Dashboard

Start the FastAPI backend:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Access the service at `http://localhost:8000/`:

* **Web UI**: Input a raw URL to inspect prediction, risk severity, and feature contributions.
* **`POST /predict`**: Submit URLs or CSV batches for classification.
* **`GET /pure-features?url=<URL>`**: Extract the 50 pure static URL features in real time.
* **`GET /incident-report?url=<URL>`**: Generate an evidence-grounded, prompt-injection-safe SOC incident report.
* **`GET /metrics`**: Retrieve cross-validation accuracy, confusion matrices, and ROC-AUC curves.
* **`GET /train`**: Trigger an automated retraining and validation cycle.

---

## Running the SOTA Benchmarking & Adversarial Suite

To reproduce the experimental tables, cross-validation metrics, and adversarial stress tests reported in the research paper:

```bash
python3 -c "
import pandas as pd
from networksecurity.pipeline.sota_training_pipeline import SOTAPhishingPipeline

df = pd.read_csv('Network_Data/phisingData.csv')
X = df.drop(columns=['Result'])
y = df['Result'].map({-1: 0, 1: 1})

pipeline = SOTAPhishingPipeline()
results = pipeline.run_benchmark(X, y, feature_modes=['All', 'Top-30', 'Top-20'])
print('Benchmark completed successfully!')
"
```

---

## Research Publication Details

A full manuscript draft detailing the theoretical formulations, threat model, experimental results, and comparative benchmarks against recent literature is available in:
`research_paper_manuscript.md`
