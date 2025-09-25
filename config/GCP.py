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
        print("\nGoogle Cloud Platform client initialized.\n")
    return _gcs_client


# 🏁
# -------- use "initialize_gcs_client()"" to initialize the GCS client --------
# ✨