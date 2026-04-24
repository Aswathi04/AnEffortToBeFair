import os
from google.cloud import storage

# Decision: Cloud Run provides an in-memory /tmp directory. 
# We will download files there temporarily so pandas can read them natively 
# without needing extra libraries like gcsfs.
TMP_DIR = "/tmp/fairlend"
os.makedirs(TMP_DIR, exist_ok=True)

def upload_file_to_gcs(file_content: bytes, destination_blob_name: str) -> str:
    """Uploads a file to the Google Cloud Storage bucket."""
    bucket_name = os.getenv("BUCKET_NAME")
    if not bucket_name:
        raise ValueError("BUCKET_NAME environment variable not set.")

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_string(file_content)
    
    return destination_blob_name

def download_file_from_gcs(source_blob_name: str) -> str:
    """Downloads a file from GCS to the local /tmp directory and returns the path."""
    bucket_name = os.getenv("BUCKET_NAME")
    if not bucket_name:
        raise ValueError("BUCKET_NAME environment variable not set.")

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    local_path = os.path.join(TMP_DIR, source_blob_name)
    
    # Ensure the subdirectories exist if the blob name contains slashes
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    
    blob.download_to_filename(local_path)
    
    return local_path