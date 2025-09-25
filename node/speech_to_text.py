import time
import asyncio
from dotenv import load_dotenv
load_dotenv()

from google.cloud import storage
import json
from google.cloud import speech_v2
from utils.const import OUTPUT_LANGS, SPEECH_TO_TEXT_MODEL, LOCATION
from state import GraphState
import os
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain_google_vertexai import ChatVertexAI
from utils.splitter import text_splitter
from utils.const import CHUNK_SIZE, CHUNK_OVERLAP

async def batch_recognize_gcs(state: GraphState) -> GraphState:
    """
    Transcribes audio from a GCS URI and updates the state with the raw text.
    """
    print("\033[92m--- Speech To Text ---\033[00m")
    state["time_taken"] = time.time()
    
    project_id = str(os.getenv("GOOGLE_CLOUD_PROJECT_ID"))
    recognizer_id = str(os.getenv("GOOGLE_CLOUD_RECOGNIZER_ID"))
    location = LOCATION

    client = speech_v2.SpeechClient()
    recognizer_name = f"projects/{project_id}/locations/{location}/recognizers/{recognizer_id}"

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

    operation = client.batch_recognize(request=request)
    print("Batch transcription started. Polling for completion...")

    while not operation.done():
        print("⏱️ Still processing... waiting 60s before next check...")
        await asyncio.sleep(60)  # check every 60 seconds

    response = operation.result()
    print("\033[93m✅ Transcription complete!\033[00m")

    
    result_metadata = response.results[state["audio_uri"]]

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
        
        data = json.loads(json_content_string)
        
        full_transcript = []
        for result in data['results']:
            if 'alternatives' in result and len(result['alternatives']) > 0:
                full_transcript.append(result['alternatives'][0]['transcript'])
        
        final_text = "\n".join(full_transcript)
            
        print(f"\033[93m✅ Successfully extracted transcript\033[00m")
        
        state["raw_text"] = final_text
        return state

    except Exception as e:
        print(f"An error occurred while processing the result file: {e}")
        raise e
    
def summarize_document(state: GraphState) -> GraphState:
    """
    Summarize the content of a document using the language model.
    """
    print("\033[92m--- Summarizing Text ---\033[00m")
    
    raw_text = state["raw_text"]
    if not raw_text:
        print("No text to summarize.")
        return {"result_summarize": "ไม่มีข้อความสำหรับสรุป"}

    splitter = text_splitter(CHUNK_SIZE, CHUNK_OVERLAP)
    
    doc = Document(page_content=raw_text)
    docs = splitter.split_documents([doc])

    llm = ChatVertexAI(
        model="gemini-2.5-flash",
        temperature=0
    )
    
    question_template = """
    Act as a professional technical meeting minutes writer. 
    Tone: formal
    Format: Technical meeting summary
    Tasks:
    - output as **Thai language**
    - highlight action items and owners
    - highlight the agreements
    - Use bullet points if needed
    {text}
    CONCISE SUMMARY IN THAI:
    """
    
    question_prompt = PromptTemplate(template=question_template, input_variables=["text"])
    
    refine_template = """
    Your job is to produce a final summary
    We have provided an existing summary up to a certain point: {existing_answer}
    We have the opportunity to refine the existing summary
    (only if needed) with some more context below.
    ------------
    {text}
    ------------
    Given the new context, refine the original summary in Thai.
    """
    
    refine_prompt = PromptTemplate(
        template=refine_template,
        input_variables=["existing_answer", "text"],
    )
    
    chain = load_summarize_chain(
        llm,
        chain_type="refine",
        return_intermediate_steps=False, # Set to False for cleaner output
        question_prompt=question_prompt,
        refine_prompt=refine_prompt,
    )
    
    response = chain.invoke({"input_documents": docs})
    
    summary_text = response['output_text']
    print("\033[93m✅ Summarization complete\033[00m")
    
    return {"result_summarize": summary_text}