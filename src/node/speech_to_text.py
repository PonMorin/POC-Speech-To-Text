from dotenv import load_dotenv
load_dotenv()
from google.cloud import storage
import json
from google.cloud import speech_v2
from google.cloud.speech_v2.types import cloud_speech
from utils.const import OUTPUT_LANGS, SPEECH_TO_TEXT_MODEL, LOCATION
from state import GraphState
import os

def batch_recognize_gcs(state: GraphState) -> cloud_speech.BatchRecognizeResponse | None:
    """
    Transcribes audio from multiple Google Cloud Storage URIs using the Google Cloud Speech-to-Text API.
    The transcription results are stored in another Google Cloud Storage bucket.
    Args:
        audio_uri (str): Google Cloud Storage URIs of the input audio files.
            E.g., ["gs://[BUCKET]/[FILE]", "gs://[BUCKET]/[FILE]"]
        gcs_output_uri (str): The Google Cloud Storage bucket URI where the output transcript will be stored.
            E.g., gs://[BUCKET]
    Returns:
        cloud_speech.BatchRecognizeResponse: The response containing the URIs of the transcription results.
    """
    project_id = str(os.getenv("GOOGLE_CLOUD_PROJECT_ID"))
    recognizer_id = str(os.getenv("GOOGLE_CLOUD_RECOGNIZER_ID"))
    location = LOCATION

    client = speech_v2.SpeechClient()
    recognizer_name = f"projects/{project_id}/locations/{location}/recognizers/{recognizer_id}"

    # --- ส่วนของการตั้งค่าและส่ง Request (เหมือนเดิม) ---
    config = speech_v2.RecognitionConfig(
        auto_decoding_config=speech_v2.AutoDetectDecodingConfig(),
        language_codes=OUTPUT_LANGS,
        model=SPEECH_TO_TEXT_MODEL,
    )
    file_metadata = speech_v2.BatchRecognizeFileMetadata(uri=state["audio_uri"])
    output_config = speech_v2.GcsOutputConfig(uri=state["gcs_output_path"])
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
    

    result_metadata = response.results[state["audio_uri"]]

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
        
        output_txt_filename = "transcript_output.md"
        with open(output_txt_filename, "w", encoding="utf-8") as f:
            f.write(final_text)
            
        print(f"✅ Successfully extracted and saved transcript to '{output_txt_filename}'")
        
        return response

    except Exception as e:
        print(f"An error occurred while processing the result file: {e}")
        return None