FairLend AI Audit
Real-time disparate impact analysis and bias mitigation for lending decisions.
FairLend AI Audit is a full-stack application that lets you upload a lending dataset, train a baseline credit approval model, measure its fairness across demographic groups, and then apply a mitigation algorithm to reduce disparities — all with a single, adjustable tradeoff control between accuracy and fairness.

The Problem
Lending algorithms can unintentionally reproduce or amplify historical bias, even when protected attributes like race and gender are never used as direct model inputs. Regulators and lenders need a way to quantify that risk in concrete, auditable terms — not just intuit it.
FairLend AI Audit answers a simple question: if you approve loans with this model, how differently does it treat similarly qualified applicants across demographic groups — and how much accuracy would you trade to close that gap?

How It Works
The application runs a three-stage pipeline:
    1. Upload — a CSV of loan application data is ingested and previewed.
    2. Audit — a baseline logistic regression model is trained on approved features (income, loan amount, debt-to-income ratio, loan-to-value ratio), and fairness metrics are computed across demographic groups.
    3. Debias — a constrained optimization technique re-trains the model under a fairness constraint, producing a new model with a measurably smaller disparity — with the strength of that constraint controlled by a single tunable weight.
CSV Upload  →  Baseline Model  →  Fairness Metrics  →  Mitigated Model  →  Before/After Comparison
Fairness Metrics
Two standard fairness criteria are computed for every model:
    • Demographic Parity (DP) Gap — the difference in approval rates between demographic groups.
    • Equalized Odds (EO) Gap — the difference in true positive rates between groups (i.e., are equally qualified applicants treated equally?).
Bias Mitigation
Mitigation is performed using Fairlearn's ExponentiatedGradient reduction technique, constrained by a demographic parity bound. Rather than using a fixed fairness threshold, the bound is calculated relative to each dataset's own baseline disparity — so the fairness/accuracy tradeoff control behaves consistently and meaningfully regardless of how biased the input data starts out.

Real-World Validation
The pipeline has been tested end-to-end against real regulatory data: mortgage applications from the Home Mortgage Disclosure Act (HMDA) public dataset (California, 2023, ~227,000 records after cleaning).
	Accuracy	DP Gap	EO Gap
Baseline	79.7%	0.039	0.018
Debiased	77.2%	0.022 (−44%)	0.025

This mirrors a well-known finding in the fairness literature: optimizing for demographic parity doesn't automatically improve equalized odds, and can occasionally trade one fairness notion for another — which is exactly the kind of nuance this tool is designed to surface, not hide.

Data Pipeline
Raw HMDA exports go through a cleaning pipeline before modeling:
    • Filtering to originated vs. denied loan actions
    • Converting income to consistent units
    • Resolving mixed exact/bucketed debt-to-income values to numeric midpoints
    • Removing data-entry outliers (e.g. erroneous multi-billion dollar income entries)
    • Explicit exclusion of interest_rate as a candidate feature, after confirming it leaks the outcome label (it's only populated for approved loans)
    • An explicit allowlist of permitted model features, preventing proxy variables (like neighborhood demographic composition) from silently entering the model

Tech Stack
Backend
    • FastAPI (Python)
    • scikit-learn — baseline logistic regression modeling
    • Fairlearn — fairness metrics and bias mitigation
    • Google Gemini API integration for AI-assisted analysis
Frontend
    • React + Vite

Architecture
├── main.py                  # FastAPI entrypoint
├── routers/
│   ├── upload.py             # Dataset ingestion
│   ├── train.py              # Baseline model training + audit
│   ├── debias_router.py      # Bias mitigation
│   └── gemini_router.py      # AI-assisted analysis
├── model/
│   ├── preprocess.py          # Feature extraction & allowlisting
│   ├── baseline.py            # Model training
│   ├── debias.py               # Fairness-constrained retraining
│   ├── metrics.py              # Fairness metric computation
│   └── counterfactual.py       # Individual-level fairness testing
└── fairlend-ui/               # React frontend

Running Locally
Backend
# from the project root
python -m venv venv
venv\Scripts\Activate.ps1      # Windows PowerShell
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt

uvicorn main:app --reload
The API will be available at http://127.0.0.1:8000.
Frontend
cd fairlend-ui
npm install
npm run dev
The app will be available at the URL Vite prints in the terminal (typically http://localhost:5173).
Environment Variables
The Gemini integration and cloud storage features require the following to be set (e.g. in a .env file):
GEMINI_API_KEY=your_key_here
BUCKET_NAME=your_gcs_bucket        # optional, for future cloud storage support
FIRESTORE_COLLECTION=your_collection   # optional, for future cloud storage support
Basic Usage
    1. Start the backend and frontend as above.
    2. Upload a lending CSV (columns: race, gender, income, loan_amount, dti, ltv, loan_approved).
    3. Run an audit to see baseline fairness metrics.
    4. Adjust the fairness weight and run debiasing to see the mitigated model's tradeoffs.

Roadmap
    • Counterfactual fairness testing (individual-level "what if this applicant's protected attribute were different?" analysis)
    • Cloud-backed persistent storage for multi-session audit history
    • Deployment to a persistent-filesystem hosting environment

Why This Project
Fairness in algorithmic decision-making isn't a checkbox — it's a set of measurable, sometimes competing tradeoffs. This project was built to make those tradeoffs visible and interactive, using real regulatory data rather than synthetic examples, so the numbers reflect the kind of bias that actually shows up in lending markets today.

