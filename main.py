from config.gcp import initialize_gcs_client
from src.speech_to_text import batch_recognize_gcs

if __name__ == "__main__":
    # ---------------------
    initialize_gcs_client()
    # ---------------------
    audio_uri = "gs://cbm-cgs-acb-km-assets/km-video/standard_output.wav"
    gcs_output_path = "gs://cbm-cgs-acb-km-assets/km-video/results/"

    project_id = "cbm-cgs-uiim-prd"
    location = "global"
    recognizer_id = "cimie-dev"
    batch_recognize_gcs(project_id, location, recognizer_id, audio_uri, gcs_output_path)