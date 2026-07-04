from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from model.gemini_explainer import explain_bias

router = APIRouter()

class ExplainRequest(BaseModel):
    metrics: dict
    stage: str

@router.post("/explain")
async def explain(body: ExplainRequest):
    try:
        explanation = explain_bias(body.metrics, body.stage)
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))