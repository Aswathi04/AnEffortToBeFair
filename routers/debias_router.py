from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from utils.storage_handler import get_local_path
from model.preprocess import load_and_preprocess
from model.baseline import train_baseline
from model.debias import run_debiasing

router = APIRouter()

class DebiasRequest(BaseModel):
    session_id: str
    fairness_weight: float
    protected_column: str
    target_column: str

@router.post("/debias")
async def apply_debiasing(request: DebiasRequest):
    local_filepath = get_local_path(request.session_id)
    if not os.path.exists(local_filepath):
        raise HTTPException(status_code=404, detail="Dataset not found.")

    X, y, sensitive, _ = load_and_preprocess(
        local_filepath,
        protected_col=request.protected_column,
        target_col=request.target_column
    )
    _, _, data_splits = train_baseline(X, y, sensitive)
    X_train, X_test, y_train, y_test, s_train, s_test = data_splits

    mitigator, metrics = run_debiasing(
        X_train, y_train, s_train,
        X_test, y_test, s_test,
        request.fairness_weight
    )

    return metrics