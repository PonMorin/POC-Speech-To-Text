from Config.GCP import load_credentials_base64
from dotenv import load_dotenv
load_dotenv()
load_credentials_base64()
import os

from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech

PROJECT_ID = "cbm-cgs-uiim-prd"


def quickstart_v2(audio_file: str) -> cloud_speech.RecognizeResponse:
    """Transcribe an audio file.
    Args:
        audio_file (str): Path to the local audio file to be transcribed.
    Returns:
        cloud_speech.RecognizeResponse: The response from the recognize request, containing
        the transcription results
    """
    # Reads a file as bytes
    with open(audio_file, "rb") as f:
        audio_content = f.read()

    # Instantiates a client
    client = SpeechClient()

    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=["th-TH"],
        model="long",
    )

    request = cloud_speech.RecognizeRequest(
        recognizer=f"projects/{PROJECT_ID}/locations/global/recognizers/_",
        config=config,
        content=audio_content,
    )

    # Transcribes the audio into text
    response = client.recognize(request=request)

    for result in response.results:
        print(f"Transcript: {result.alternatives[0].transcript}")

    return response

if __name__ == "__main__":
    quickstart_v2("/Users/ponmorin/Documents/SCG_KM_ChatBot/POC/POC-Speech-To-Text/data/test.wav")