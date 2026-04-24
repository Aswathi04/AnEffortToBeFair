from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from storage.gcs import download_file_from_gcs
from storage.firestore_client import save_audit_record
from model.preprocess import load_and_preprocess
from model.baseline import train_baseline
from model.debias import run_debiasing

router = APIRouter()

class DebiasRequest(BaseModel):
    session_id: str
    fairness_weight: float

@router.post("/debias")
async def apply_debiasing(request: DebiasRequest):
    """
    Rebuilds the data splits, runs the Fairlearn adversarial debiasing 
    using the provided slider weight, saves the new metrics, and returns them.
    """
    session_id = request.session_id
    gcs_path = f"{session_id}/dataset.csv"

    # 1. Retrieve data
    try:
        local_filepath = download_file_from_gcs(gcs_path)
    except Exception:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    # 2. Re-run preprocessing and baseline to guarantee identical train/test splits
    X, y, sensitive, _ = load_and_preprocess(local_filepath)
    _, _, data_splits = train_baseline(X, y, sensitive)
    X_train, X_test, y_train, y_test, s_train, s_test = data_splits

    # 3. Run the core Fairlearn engine using the slider's fairness_weight [cite: 166]
    mitigator, metrics = run_debiasing(
        X_train, y_train, s_train, X_test, y_test, s_test, request.fairness_weight
    )

    # 4. Update the Firestore audit record with the new debiased metrics
    audit_data = {
        "debiased_metrics": metrics,
        "fairness_weight_used": request.fairness_weight
    }
    save_audit_record(session_id, audit_data)

    # 5. Return the metrics (matches the API contract exactly) [cite: 168-177]
    return metrics