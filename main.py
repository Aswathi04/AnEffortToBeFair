from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables from .env file for local development
load_dotenv()

# Import all our routers
from routers import upload, train, debias_router, explain, report

app = FastAPI(
    title="FairLend AI API",
    description="Bias detection and in-processing fairness engine."
)

# Configure CORS so the React frontend can make requests to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Warning: Using "*" for hackathon speed. Lock down in prod!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the API endpoints 
app.include_router(upload.router, tags=["Upload"])
app.include_router(train.router, tags=["Baseline"])
app.include_router(debias_router.router, tags=["Debias"])
app.include_router(explain.router, tags=["Explain"])
app.include_router(report.router, tags=["Report"])

@app.get("/")
async def health_check():
    """Simple health check endpoint to verify the server is running."""
    return {"status": "online", "message": "FairLend AI backend is up."}