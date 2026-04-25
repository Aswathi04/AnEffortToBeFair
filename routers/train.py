from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from utils.storage_handler import get_local_path
from model.preprocess import load_and_preprocess
from model.baseline import train_baseline

router = APIRouter()

class TrainRequest(BaseModel):
    session_id: str
    protected_column: str
    target_column: str

@router.post("/audit")
async def train_baseline_model(request: TrainRequest):
    session_id = request.session_id

    local_filepath = get_local_path(session_id)
    if not os.path.exists(local_filepath):
        raise HTTPException(status_code=404, detail="Dataset not found for this session.")

    try:
        X, y, sensitive, _ = load_and_preprocess(
            local_filepath,
            protected_col=request.protected_column,
            target_col=request.target_column
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    baseline_model, metrics, data_splits = train_baseline(X, y, sensitive)

    return {
        "session_id": session_id,
        **metrics
    }