from fastapi import APIRouter, HTTPException
from storage.firestore_client import get_audit_record

router = APIRouter()

@router.get("/report/{session_id}")
async def generate_report(session_id: str):
    """
    Fetches the complete audit history for a given session.
    """
    audit_record = get_audit_record(session_id)
    if not audit_record:
        raise HTTPException(status_code=404, detail="Audit record not found.")

    return {
        "session_id": session_id,
        "report_data": audit_record
    }