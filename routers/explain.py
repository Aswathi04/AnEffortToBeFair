from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from storage.gcs import download_file_from_gcs
from model.preprocess import load_and_preprocess, ALLOWED_FEATURE_COLS
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
    session_id = request.session_id
    gcs_path = f"{session_id}/dataset.csv"

    try:
        local_filepath = download_file_from_gcs(gcs_path)
    except Exception:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    audit_record = get_audit_record(session_id)
    weight = audit_record.get("fairness_weight_used", 1.0)

    X, y, sensitive, _ = load_and_preprocess(local_filepath)
    _, baseline_metrics, data_splits, scaler = train_baseline(X, y, sensitive)
    X_train, X_test, y_train, y_test, s_train, s_test = data_splits

    mitigator, _ = run_debiasing(
        X_train, y_train, s_train, X_test, y_test, s_test,
        weight, baseline_dp_gap=baseline_metrics["demographic_parity_gap"]
    )

    result = run_counterfactual(
        mitigator, scaler, ALLOWED_FEATURE_COLS,
        request.applicant,
        request.flip_attribute,
        request.original_value,
        request.flipped_value
    )
    return result