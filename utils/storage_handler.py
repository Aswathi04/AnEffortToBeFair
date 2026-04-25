import os

def save_local_file(file_content, session_id):
    base_dir = os.path.join("data", session_id)
    os.makedirs(base_dir, exist_ok=True)
    file_path = os.path.join(base_dir, "dataset.csv")
    with open(file_path, "wb") as f:
        f.write(file_content)
    return file_path

def get_local_path(session_id):
    return os.path.join("data", session_id, "dataset.csv")