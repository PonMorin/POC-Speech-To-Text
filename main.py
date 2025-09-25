import os
from config.GCP import initialize_gcs_client
from src.speech_to_text import batch_recognize_gcs
from dotenv import load_dotenv
load_dotenv()
from utils.const import LOCATION

if __name__ == "__main__":
    # ---------------------
    initialize_gcs_client()
    # ---------------------
    audio_uri: str = "gs://cbm-cgs-acb-km-assets/km-video/standard_output.wav"
    gcs_output_path: str = "gs://cbm-cgs-acb-km-assets/km-video/results/"

    project_id = str(os.getenv("GOOGLE_CLOUD_PROJECT_ID"))
    recognizer_id = str(os.getenv("GOOGLE_CLOUD_RECOGNIZER_ID"))
    batch_recognize_gcs(project_id, LOCATION, recognizer_id, audio_uri, gcs_output_path)
