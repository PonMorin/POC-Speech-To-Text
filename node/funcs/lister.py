import os
from gcp.bucket import list_blobs_in_folder
from dotenv import load_dotenv
load_dotenv()

def list_blobs_in_bucket(video_folder_prefix: str, output_folder_prefix: str) -> list[str]:
    """List docs in bucket"""
    print("\033[92m--- Listing blobs in bucket ---\033[00m")
    
    bucket_name = os.getenv("BUCKET_NAME")
    
    blobs_list: list = list_blobs_in_folder(
        bucket_name=bucket_name, 
        folder_prefix=video_folder_prefix,
        file_type=".wav")
    
    
    existings_list: list = list_blobs_in_folder(
        bucket_name=bucket_name, 
        folder_prefix=output_folder_prefix,
        file_type=".md")

    # Extract just the base names (without folder or extension)
    existing_basenames = {
        os.path.splitext(os.path.basename(e))[0] for e in existings_list
    }

    # Filter out .wav that already have .md output
    new_wavs = [
        b for b in blobs_list
        if os.path.splitext(os.path.basename(b))[0] not in existing_basenames
    ]
    
    if len(new_wavs) > 0:
        return new_wavs
        
    else:
        return []