import os

from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech

import uuid

from config.gcp import initialize_gcs_client
from dotenv import load_dotenv
load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID")

def create_recognizer(recognizer_id: str) -> cloud_speech.Recognizer:
    """Сreates a recognizer with an unique ID and default recognition configuration.
    Args:
        recognizer_id (str): The unique identifier for the recognizer to be created.
    Returns:
        cloud_speech.Recognizer: The created recognizer object with configuration.
    """
    # Instantiates a client
    client = SpeechClient()

    request = cloud_speech.CreateRecognizerRequest(
        parent=f"projects/{PROJECT_ID}/locations/asia-southeast1",
        recognizer_id=recognizer_id,
        recognizer=cloud_speech.Recognizer(
            default_recognition_config=cloud_speech.RecognitionConfig(
                language_codes=["th-TH"],
                model="chirp_2",
            ),
        ),
    )
    # Sends the request to create a recognizer and waits for the operation to complete
    operation = client.create_recognizer(request=request)
    recognizer = operation.result()

    print("Created Recognizer:", recognizer.name)
    return recognizer

if __name__ == "__main__":
    initialize_gcs_client()
    create_recognizer(str("cimie-recognizers"))