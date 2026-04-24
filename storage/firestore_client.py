import os
from google.cloud import firestore

def save_audit_record(session_id: str, data: dict):
    """
    Saves or updates an audit record in Firestore.
    Uses merge=True so we can update the same session sequentially 
    (e.g., baseline first, then debiased later).
    """
    collection_name = os.getenv("FIRESTORE_COLLECTION")
    if not collection_name:
        raise ValueError("FIRESTORE_COLLECTION environment variable not set.")

    db = firestore.Client()
    doc_ref = db.collection(collection_name).document(session_id)
    
    # merge=True prevents overwriting existing data if we only send partial updates
    doc_ref.set(data, merge=True)

def get_audit_record(session_id: str) -> dict:
    """
    Retrieves a complete audit record by session_id.
    """
    collection_name = os.getenv("FIRESTORE_COLLECTION")
    if not collection_name:
        raise ValueError("FIRESTORE_COLLECTION environment variable not set.")

    db = firestore.Client()
    doc_ref = db.collection(collection_name).document(session_id)
    doc = doc_ref.get()

    if doc.exists:
        return doc.to_dict()
    return {}