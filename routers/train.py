from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from storage.gcs import download_file_from_gcs
from storage.firestore_client import save_audit_record
from model.preprocess import load_and_preprocess
from model.baseline import train_baseline

router = APIRouter()

# Define the expected JSON body from the frontend
class TrainRequest(BaseModel):
    session_id: str

@router.post("/train-baseline")
async def train_baseline_model(request: TrainRequest):
    """
    Downloads the session's CSV, preprocesses it, trains the biased baseline model,
    saves the metrics to Firestore, and returns them to the frontend.
    """
    session_id = request.session_id
    gcs_path = f"{session_id}/dataset.csv"
    
    # 1. Download the raw CSV from Cloud Storage
    try:
        local_filepath = download_file_from_gcs(gcs_path)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Dataset not found for this session.")

    # 2. Clean and prep the data
    X, y, sensitive, _ = load_and_preprocess(local_filepath)

    # 3. Train the baseline model and compute the initial bias metrics
    baseline_model, metrics, data_splits = train_baseline(X, y, sensitive)

    # 4. Save these baseline metrics to our Firestore database for the final report
    audit_data = {
        "session_id": session_id,
        "baseline_metrics": metrics
    }
    save_audit_record(session_id, audit_data)

    # 5. Return the exact response shape the frontend expects
    return {
        "session_id": session_id,
        **metrics
    }