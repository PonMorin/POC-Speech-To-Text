import os
from typing import List
from google.cloud import storage
# from google.oauth2 import service_account
# import json
from dotenv import load_dotenv
# import base64

load_dotenv()

# --- Global variable สำหรับเก็บ GCS Client ---
_gcs_client = None

def get_gcs_client():
    if _gcs_client is None:
        raise RuntimeError("GCS client not initialized. Call initialize_gcs_client() during app startup.")
    return _gcs_client  

def upload_to_gcs(client, bucket_name: str, file_obj, destination_blob_name: str):
    # client = get_gcs_client()
    CHUNK_SIZE = 1024 * 1024 * 30
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name, chunk_size=CHUNK_SIZE)

    if blob.exists():
        return None
    
    with open(file_obj, "rb") as f:
        blob.upload_from_file(f)
    return blob.public_url

def list_blobs_in_folder(bucket_name: str, folder_prefix: str, file_type: str) -> list[str]:

    storage_client = storage.Client() 
    blobs = storage_client.list_blobs(
        bucket_name,
        prefix=folder_prefix
    ) 

    files: List[str] = []
    for blob in blobs:
        blob_name: str = blob.name
        if blob_name.endswith(file_type):
            full_path = f"gs://{bucket_name}/{blob_name}"
            files.append(full_path)
    
    return files

from google.cloud import storage

def move_blob_in_same_bucket(bucket_name: str, source_blob_name: str, destination_folder: str) -> bool:

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    source_blob = bucket.blob(source_blob_name)
    file_name = source_blob_name.split('/')[-1]
    destination_blob_name = destination_folder + file_name

    # ตรวจสอบว่าไฟล์ต้นฉบับมีอยู่จริง
    if not source_blob.exists():
        print(f"Error: Source file '{source_blob_name}' not found.")
        return False
        
    # COPY
    try:
        bucket.copy_blob(
            source_blob, 
            bucket, 
            new_name=destination_blob_name
        )
        print(f"Successfully copied '{source_blob_name}' to '{destination_blob_name}'.")

    except Exception as e:
        print(f"Error during copy: {e}")
        return False

    # DELETE
    try:
        source_blob.delete()
        print(f"Successfully deleted original file '{source_blob_name}'.")
        return True
    
    except Exception as e:
        print(f"Warning: Copy successful, but failed to delete original file: {e}")
        return False
