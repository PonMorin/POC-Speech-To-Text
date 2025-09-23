from Config.GCP import load_credentials_base64
from dotenv import load_dotenv
load_dotenv()
load_credentials_base64()
import os

from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech

from google.cloud import speech_v2

PROJECT_ID = "cbm-cgs-uiim-prd"

from pydub import AudioSegment

def convert_mov_to_wav_specific(input_file: str, output_file: str) -> str:
    """
    Converts a .mov file to a .wav file with specific audio settings:
    - Codec: pcm_s16le (16-bit PCM)
    - Sampling rate: 16000 Hz
    - Channels: 1 (mono)

    Args:
        input_file (str): Path to the input .mov file.
        output_file (str): Path to save the output .wav file.

    Returns:
        str: Path to the converted .wav file.
    """
    # Load the audio from the input file
    audio = AudioSegment.from_file(input_file, format="mov")

    audio = audio.set_channels(1)
    
    audio = audio.set_frame_rate(16000)
    
    audio = audio.set_sample_width(2)

    # Export the audio to the output file in wav format
    audio.export(output_file, format="wav")

    return output_file

def batch_recognize_gcs(project_id, location, recognizer_id, gcs_uri, gcs_output_uri):
    """Performs batch speech recognition on a GCS file."""

    client = speech_v2.SpeechClient()

    recognizer_name = f"projects/{project_id}/locations/{location}/recognizers/{recognizer_id}"

    config = speech_v2.RecognitionConfig(
        auto_decoding_config=speech_v2.AutoDetectDecodingConfig(),
        language_codes=["th-TH"],
        model="long",
    )

    file_metadata = speech_v2.BatchRecognizeFileMetadata(
        uri=gcs_uri
    )

    output_config = speech_v2.GcsOutputConfig(
        uri=gcs_output_uri
    )

    recognition_output_config = speech_v2.RecognitionOutputConfig(
        gcs_output_config=output_config
    )


    request = speech_v2.BatchRecognizeRequest(
        recognizer=recognizer_name,
        config=config,
        files=[file_metadata],
        recognition_output_config=recognition_output_config,
    )

    # Perform the batch recognition request
    operation = client.batch_recognize(request=request)

    print("Waiting for operation to complete...")
    response = operation.result()

    print("Operation completed. Check your GCS bucket for the output file.")
    print(response)

    # NOTE: The structure of the batch response is slightly different.
    # You need to iterate through response.results which maps GCS URI to the transcript.
    # The output from a batch request is a dictionary mapping the file URI to its recognition results.
    transcript_results = response.results[gcs_uri]
    
    if not transcript_results.transcript:
        print(f"No transcription results for {gcs_uri}")
        if transcript_results.error:
            print(f"Error: {transcript_results.error.message}")
        return

    for result in transcript_results.transcript.results:
        print(f"Transcript: {result.alternatives[0].transcript}")


if __name__ == "__main__":
    gcs_uri = "gs://cbm-cgs-acb-km-assets/km-video/standard_output.wav"
    gcs_output_path = "gs://cbm-cgs-acb-km-assets/km-video/results/"

    project_id = "cbm-cgs-uiim-prd"
    location = "global"
    recognizer_id = "_"
    
    batch_recognize_gcs(project_id, location, recognizer_id, gcs_uri, gcs_output_path)