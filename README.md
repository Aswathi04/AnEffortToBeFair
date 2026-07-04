# FairLend — AI Fairness Auditing Platform

> *An effort to be fair.* A tool for detecting, explaining, and mitigating bias in machine learning models — built for anyone who believes the algorithm should treat everyone equally.

---

## What it does

FairLend lets you upload a trained ML model and dataset, audit it for bias across protected attributes (gender, race, age, etc.), and apply debiasing techniques — all through a clean web interface. Gemini AI explains the bias findings in plain language so non-technical stakeholders can understand the results.

**Three core workflows:**

- **Upload** — Upload your dataset and model for analysis
- **Audit** — Detect bias using fairness metrics (demographic parity, equalized odds, etc.) powered by Microsoft Fairlearn
- **Debias** — Apply mitigation strategies and compare the fairness/accuracy tradeoff before and after

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI + Uvicorn |
| ML & Fairness | scikit-learn, Fairlearn |
| AI Explanations | Google Gemini AI |
| Storage | Google Cloud Storage, Firebase/Firestore |
| Frontend | React (fairlend-ui) |
| Data | pandas, numpy |
| Containerisation | Docker |

---

## Project Structure

```
AnEffortToBeFair/
├── main.py               # FastAPI app entry point
├── routers/
│   ├── upload.py         # Dataset/model upload endpoints
│   ├── train.py          # Audit/training endpoints
│   └── debias_router.py  # Debiasing endpoints
├── model/                # ML model logic
├── utils/                # Helper functions
├── storage/              # Cloud storage integration
├── data/                 # Sample/reference datasets
├── fairlend-ui/          # React frontend
├── Dockerfile
└── requirements.txt
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+ (for the frontend)
- Google Cloud project with Storage and Firestore enabled
- Firebase Admin credentials

### Backend Setup

```bash
# Clone the repo
git clone https://github.com/Aswathi04/AnEffortToBeFair.git
cd AnEffortToBeFair

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Fill in your Google Cloud and Firebase credentials in .env

# Run the API
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

The API will be live at `http://localhost:8000`. Visit `http://localhost:8000/docs` for the interactive Swagger UI.

### Frontend Setup

```bash
cd fairlend-ui
npm install
npm start
```

### Docker

```bash
docker build -t fairlend .
docker run -p 8000:8000 fairlend
```

---

## API Endpoints

| Method | Route | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/upload` | Upload dataset and model |
| POST | `/audit` | Run bias audit |
| POST | `/debias` | Apply debiasing and return results |

Full interactive docs available at `/docs` when the server is running.

---

## Environment Variables

Create a `.env` file in the project root:

```
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
FIREBASE_ADMIN_SDK=path/to/firebase_admin.json
GEMINI_API_KEY=your_gemini_api_key
```

---

## Fairness Metrics Used

- **Demographic Parity** — equal positive prediction rates across groups
- **Equalized Odds** — equal true positive and false positive rates
- **Equal Opportunity** — equal true positive rates across groups

Mitigation strategies are applied via Fairlearn's `ExponentiatedGradient` and `ThresholdOptimizer`.

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## License

MIT
