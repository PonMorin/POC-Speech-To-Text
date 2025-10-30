import os
import asyncio
from dotenv import load_dotenv
load_dotenv()
from google.cloud import storage
from google.cloud import speech_v2
from utils.const import (
    OUTPUT_LANGS, 
    SPEECH_TO_TEXT_MODEL, 
    LOCATION, 
    MAX_LINE
)
from utils.parser import parse_transcript
from utils.summarizer import summarizer

async def batch_recognize_gcs(uri: str, gcs_output_path: str):
    """
    Transcribes audio from a GCS URI and updates the state with the raw text.
    """
    print("\n\033[92m--- Speech To Text ---\033[00m")
    # state["time_taken"] = time.time()
    
    project_id = str(os.getenv("GOOGLE_CLOUD_PROJECT_ID"))
    recognizer_id = str(os.getenv("GOOGLE_CLOUD_RECOGNIZER_ID"))
    location = LOCATION

    client = speech_v2.SpeechClient()
    recognizer_name = f"projects/{project_id}/locations/{location}/recognizers/{recognizer_id}"

    config = speech_v2.RecognitionConfig(
        auto_decoding_config=speech_v2.AutoDetectDecodingConfig(),
        language_codes=OUTPUT_LANGS,
        model=SPEECH_TO_TEXT_MODEL,
        features=speech_v2.RecognitionFeatures(
            enable_word_confidence=True,
        ),
    )
    
    print(f"\033[93mStart processing {uri}\033[00m")
    
    file_metadata = speech_v2.BatchRecognizeFileMetadata(uri=uri)
    filename = os.path.basename(uri)
    absolute_filename = os.path.splitext(filename)[0]
    output_config = speech_v2.GcsOutputConfig(uri=gcs_output_path)
    recognition_output_config = speech_v2.RecognitionOutputConfig(gcs_output_config=output_config)
    
    request = speech_v2.BatchRecognizeRequest(
        recognizer=recognizer_name,
        config=config,
        files=[file_metadata],
        recognition_output_config=recognition_output_config,
    )

    operation = client.batch_recognize(request=request)
    print("Batch transcription started. Polling for completion...")

    while not operation.done():
        print("⏱️ Still processing... waiting 10s before next check...")
        await asyncio.sleep(10)

    response = operation.result()
    print("\033[93m✅ Transcription complete!\033[00m")
    
    result_metadata = response.results[uri]

    if result_metadata.error and result_metadata.error.code != 0:
        print("❌ Transcription failed. Full error details below:")
        print(result_metadata.error)
        raise ValueError(f"Transcription failed: {result_metadata.error.message}")
        
    output_json_uri = result_metadata.uri
    print(f"Output JSON file is at: {output_json_uri}")

    try:
        storage_client = storage.Client()
        bucket_name, blob_name = output_json_uri.replace("gs://", "").split("/", 1)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        print(f"Downloading result file: {blob_name}...")
        json_content_string = blob.download_as_text()
        print(f"Successfully downloaded result")

        # Parsing transcript
        final_text, total_lines = parse_transcript(json_content_string, "plain")
            
        print(f"\033[93m✅ Successfully extracted transcript\033[00m")
        
        return final_text, total_lines, absolute_filename

    except Exception as e:
        print(f"An error occurred while processing the result file: {e}")
        raise e
    
async def summarize_document(docs: str, total_lines: int) -> str:
    """
    Summarize the content of a document using the language model.
    """
    print("\033[92m--- Summarizing Text ---\033[00m")

    summary_text: str
    if total_lines > MAX_LINE:
        print(f"\033[93mMap Reduce Method is selected, total lines > {MAX_LINE}\033[00m")
        summary_text = await summarizer(docs=docs, method="map_reduce")
    else:
        print(f"\033[93mRefine Method is selected, total lines < {MAX_LINE}\033[00m")
        summary_text = await summarizer(docs=docs, method="refine")
        
    # Calculate time
    # elapsed_time: float = 0
    # start_time = state.get("time_taken", None)
    # if start_time:
    #     elapsed_time = round((time.time() - start_time) / 60, 2)
        # print(f"\n\033[96m ===========> ⏱️ Speech To Text operation time taken: {elapsed_time/60:.2f} minutes <===========\n\033[00m")
    # else:
    #     print("\nStart time not found")

    return summary_text