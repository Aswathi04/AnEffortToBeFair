from fastapi import APIRouter, UploadFile, File
import uuid
import pandas as pd
import io
from storage.gcs import upload_file_to_gcs

router = APIRouter()

@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """
    Accepts a CSV upload, assigns a session ID, stores it in Cloud Storage,
    and returns basic dataset stats to the frontend.
    """
    # Read the uploaded file into memory
    contents = await file.read()
    
    # Generate a unique session ID for this audit run
    session_id = str(uuid.uuid4())
    
    # Save to Cloud Storage. We hardcode the filename as 'dataset.csv' 
    # within a session folder so the train endpoint knows exactly where to find it.
    gcs_path = f"{session_id}/dataset.csv"
    upload_file_to_gcs(contents, gcs_path)
    
    # Parse the CSV with pandas to count rows and extract columns for the UI
    df = pd.read_csv(io.BytesIO(contents), low_memory=False)
    
    return {
        "session_id": session_id,
        "rows": len(df),
        "columns": df.columns.tolist()
    }