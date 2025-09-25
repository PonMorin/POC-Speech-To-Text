import os
from google.cloud import storage
from google.oauth2 import service_account
import json
from dotenv import load_dotenv
import base64

load_dotenv()

# --- Global variable สำหรับเก็บ GCS Client ---
_gcs_client = None

def load_credentials_base64():
    ### base 64 encode
    b64_string = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_BASE64")

    if b64_string:
        try:
            decoded_json = base64.b64decode(b64_string).decode()
            data = json.loads(decoded_json)
            service_account_json = data
            # print(type(data))
            # print(data)
            
        except Exception as e:
            print("Error decoding Base64 or parsing JSON:", e)
    else:
        print("Error: Environment variable not set.")
    ###

    # service_account_info_str = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") 
    # print(service_account_info_str)
    # if not service_account_info_str:
    #     raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable not set or is empty.")
    try:
    #     service_account_json = json.loads(service_account_info_str)
        credentials = service_account.Credentials.from_service_account_info(service_account_json)
        # ✅ สำคัญ: เขียน service_account.json ลงไฟล์ temp
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".json") as f:
            json.dump(service_account_json, f)
            temp_path = f.name

        # ✅ ตั้งค่า ADC โดยใช้ไฟล์นี้
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_path
        return credentials
    # except json.JSONDecodeError as e:
    #     raise ValueError(f"Error decoding JSON from GOOGLE_APPLICATION_CREDENTIALS: {e}")
    except Exception as e:
        raise RuntimeError(f"Error creating credentials from service account info: {e}")

def initialize_gcs_client():
    global _gcs_client
    if _gcs_client is None:
        credentials = load_credentials_base64()
        _gcs_client = storage.Client(credentials=credentials)
        print("Google Cloud Storage client initialized.")
    return _gcs_client

def get_gcs_client():
    if _gcs_client is None:
        raise RuntimeError("GCS client not initialized. Call initialize_gcs_client() during app startup.")
    return _gcs_client  

def upload_to_gcs(bucket_name: str, file_obj, destination_blob_name: str):
    client = get_gcs_client()
    CHUNK_SIZE = 1024 * 1024 * 30
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name, chunk_size=CHUNK_SIZE)

    if blob.exists():
        return None
    
    blob.upload_from_file(file_obj)
    return blob.public_url

def list_blobs_in_folder(bucket_name: str, folder_prefix: str) -> list[str]:

    storage_client = storage.Client() 
    blobs = storage_client.list_blobs(
        bucket_name,
        prefix=folder_prefix
    ) 

    file_names = [blob.name for blob in blobs]
    
    return file_names

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
