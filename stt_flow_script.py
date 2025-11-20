import os
import asyncio
from dotenv import load_dotenv
load_dotenv()
from node.funcs.lister import list_blobs_in_bucket
from node.funcs.speech_to_text import batch_recognize_gcs, summarize_document
from node.funcs.uploader import upload_doc_to_bucket
from node.funcs.preprocess import remove_stop_words, chunk_document
from node.funcs.eval import similarity
from config.GCP import initialize_gcs_client

async def run_task(uri: str, output_folder: str, client):
    # 2. Speech to text
    raw_text, total_lines, absolute_filename = await batch_recognize_gcs(
        uri=uri,
        gcs_output_path="gs://cbm-cgs-acb-km-assets/km-video/results/"
    )
    
    # Checking empty text from speech to text
    if not raw_text:
        print("\033[91mText is empty, skipping this audio...\033[00m")
        out_dir = f"output"
        os.makedirs(out_dir, exist_ok=True)
        # Saving empty audio
        with open(f"{out_dir}/empty.md", "a") as f:
            f.write(absolute_filename)
    
    # 3. Cleaning text for better performance
    cleaned_text: str = await remove_stop_words(raw_text=raw_text)
    
    # 4. Chunking text before summarization 
    docs: list[str] = await chunk_document(cleaned_text=cleaned_text)
    
    # 5. Summarizing transcribe
    summary_text = await summarize_document(docs=docs, total_lines=total_lines)
    
    # 6. Evaluating summary result
    score: float = await similarity(raw_text=raw_text, summary=summary_text)
    print(f"\033[96mSummary score: {score}\033[00m")
    
    # 7. Upload the result to the bucket
    await upload_doc_to_bucket(
        filename=absolute_filename, 
        summary=summary_text, 
        output_folder_prefix=output_folder,
        gcs_client=client
    )


async def main(video_folders: list[str], output_folders: list[str]):
    
    client = initialize_gcs_client()
    
    for i in range(len(video_folders)):
        print(f"\033[97mStart with => {video_folders[i]}\033[00m")
        # 1. Listing all wavs in the bucket
        uris: list[str] = list_blobs_in_bucket(
            video_folder_prefix=video_folders[i],
            output_folder_prefix=output_folders[i]
        )
        
        if len(uris) == 0:
            print(f"\033[91m'{video_folders[i]}' is empty, maybe it is already processed. \nPlease check!\033[00m")
        else:
          
            coros = [run_task(uri=uri, output_folder=output_folders[i], client=client) for uri in uris]
            await asyncio.gather(*coros)
        
        print("\n\033[94mMoving to the next folder.\033[00m")
            
    print("\033[94mNo leftovers, Process is done!\033[00m")
    
if __name__ == "__main__":
    video_folders: list[str] = [
        "bronze/videos/inputs/Green Industrial/MEE (โรงไฟฟ้า)/3.Learning Course/หลักสูตร KM & Problem Solving for Chronic problem",
        "bronze/videos/inputs/Green Industrial/MEE (โรงไฟฟ้า)/3.Learning Course/หลักสูตร Operator Furnace, Waste และการเผาไหม้ที่เหมาะสม",
        "bronze/videos/inputs/Green Industrial/MEE (โรงไฟฟ้า)/3.Learning Course/หลักสูตร Turbine & Boiler Control",
        "bronze/videos/inputs/Green Industrial/MEE (โรงไฟฟ้า)/3.Learning Course/หลักสูตร Waste ที่ยังไม่สามารถรับได้"
    ]
    output_folders = [p.replace("bronze/videos/inputs/", "silver/videos/outputs/") for p in video_folders]
    
    asyncio.run(main(video_folders=video_folders, output_folders=output_folders))