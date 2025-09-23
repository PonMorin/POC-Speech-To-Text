from Config.GCP import load_credentials_base64
from dotenv import load_dotenv
load_dotenv()
load_credentials_base64()


from google.cloud import storage
import json
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
    """
    Performs batch speech recognition and saves the final transcript as a .txt file.
    """

    client = speech_v2.SpeechClient()
    recognizer_name = f"projects/{project_id}/locations/{location}/recognizers/{recognizer_id}"

    # --- ส่วนของการตั้งค่าและส่ง Request (เหมือนเดิม) ---
    config = speech_v2.RecognitionConfig(
        auto_decoding_config=speech_v2.AutoDetectDecodingConfig(),
        language_codes=["th-TH"],
        model="long",
    )
    file_metadata = speech_v2.BatchRecognizeFileMetadata(uri=gcs_uri)
    output_config = speech_v2.GcsOutputConfig(uri=gcs_output_uri)
    recognition_output_config = speech_v2.RecognitionOutputConfig(gcs_output_config=output_config)
    request = speech_v2.BatchRecognizeRequest(
        recognizer=recognizer_name,
        config=config,
        files=[file_metadata],
        recognition_output_config=recognition_output_config,
    )

    print("Sending transcription request...")
    operation = client.batch_recognize(request=request)
    print("Waiting for operation to complete...")
    response = operation.result()
    print("Operation completed.")
    

    result_metadata = response.results[gcs_uri]

    if result_metadata.error and result_metadata.error.code != 0:
        print("❌ Transcription failed. Full error details below:")
        print(result_metadata.error)
        return
        
    output_json_uri = result_metadata.uri
    print(f"Output JSON file is at: {output_json_uri}")

    try:
        storage_client = storage.Client()
        bucket_name, blob_name = output_json_uri.replace("gs://", "").split("/", 1)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        print(f"Downloading result file: {blob_name}...")
        json_content_string = blob.download_as_text()
        
        data = json.loads(json_content_string)
        
        full_transcript = []
        for result in data['results']:
            if 'alternatives' in result and len(result['alternatives']) > 0:
                full_transcript.append(result['alternatives'][0]['transcript'])
        
        final_text = "\n".join(full_transcript)
        
        output_txt_filename = "transcript_output.txt"
        with open(output_txt_filename, "w", encoding="utf-8") as f:
            f.write(final_text)
            
        print(f"✅ Successfully extracted and saved transcript to '{output_txt_filename}'")

    except Exception as e:
        print(f"An error occurred while processing the result file: {e}")


if __name__ == "__main__":
    gcs_uri = "gs://cbm-cgs-acb-km-assets/km-video/standard_output.wav"
    gcs_output_path = "gs://cbm-cgs-acb-km-assets/km-video/results/"

    project_id = "cbm-cgs-uiim-prd"
    location = "global"
    recognizer_id = "_"
    
    batch_recognize_gcs(project_id, location, recognizer_id, gcs_uri, gcs_output_path)