import os
from dotenv import load_dotenv
load_dotenv()
from gcp.bucket import upload_to_gcs, upload_to_gcs_async

bucket_name = os.getenv("BUCKET_NAME")

async def upload_doc_to_bucket(filename: str, summary: str, output_folder_prefix: str, gcs_client):
    """Upload doc to bucket"""
    print("\033[92m--- Uploading summary to bucket ---\033[00m")
    
    out_dir = f"output/{filename}"
    os.makedirs(out_dir, exist_ok=True)

    # Save raw text
    # with open(f"{out_dir}/raw.md", "w") as f:
    #     f.write(state["raw_text"])

    # Save summary
    output_file_path: str = f"{out_dir}/summary.md"
    with open(output_file_path, "w") as f:
        f.write(summary)

    _ = upload_to_gcs(
        client=gcs_client, 
        bucket_name=bucket_name, 
        file_obj=output_file_path, 
        destination_blob_name=f"{output_folder_prefix}/{filename}.md"
    )
    
def upload_wav_to_bucket(file_obj: str, gcs_client):
    """Upload doc to bucket"""
    filename = os.path.basename(file_obj)
    absolute_filename = os.path.splitext(filename)[0]
    
    print(f"\033[92m--- Uploading {absolute_filename} to bucket ---\033[00m")

    output_wav_prefix = os.getenv("OUTPUT_WAV_PREFIX")

    _ = upload_to_gcs(
        client=gcs_client, 
        bucket_name=bucket_name, 
        file_obj=file_obj, 
        destination_blob_name=f"{output_wav_prefix}/{absolute_filename}.wav"
    )