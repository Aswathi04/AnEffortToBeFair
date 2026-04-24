from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from storage.gcs import download_file_from_gcs
from model.preprocess import load_and_preprocess
from model.baseline import train_baseline
from model.debias import run_debiasing
from model.counterfactual import run_counterfactual
from storage.firestore_client import get_audit_record

router = APIRouter()

class CounterfactualRequest(BaseModel):
    session_id: str
    applicant: dict
    flip_attribute: str
    original_value: str
    flipped_value: str

@router.post("/counterfactual")
async def test_counterfactual(request: CounterfactualRequest):
    """
    Reconstructs the debiased model state, runs a single applicant,
    flips a protected attribute, and returns both decisions.
    """
    session_id = request.session_id
    gcs_path = f"{session_id}/dataset.csv"

    # Fetch data and audit record to know what slider weight was last used
    try:
        local_filepath = download_file_from_gcs(gcs_path)
    except Exception:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    audit_record = get_audit_record(session_id)
    weight = audit_record.get("fairness_weight_used", 1.0) # default to max fairness if missing

    # Rebuild the exact debiased model state
    X, y, sensitive, _ = load_and_preprocess(local_filepath)
    _, _, data_splits = train_baseline(X, y, sensitive)
    X_train, X_test, y_train, y_test, s_train, s_test = data_splits
    
    mitigator, _ = run_debiasing(X_train, y_train, s_train, X_test, y_test, s_test, weight)

    # Run the counterfactual test [cite: 182-185]
    result = run_counterfactual(
        mitigator,
        request.applicant,
        request.flip_attribute,
        request.original_value,
        request.flipped_value
    )

    return result