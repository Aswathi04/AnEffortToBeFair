from fastapi import APIRouter, UploadFile, File, HTTPException
import uuid
import pandas as pd
import io
from utils.storage_handler import save_local_file

router = APIRouter()

@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    session_id = str(uuid.uuid4())
    try:
        contents = await file.read()
        save_local_file(contents, session_id)
        df = pd.read_csv(io.BytesIO(contents), nrows=5)
        return {
            "session_id": session_id,
            "columns": df.columns.tolist(),
            "status": "success"
        }
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))