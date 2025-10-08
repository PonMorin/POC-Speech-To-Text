import os
from gcp.bucket import list_blobs_in_folder
from dotenv import load_dotenv
load_dotenv()
from state import SummaryState

def list_blobs_in_bucket(state: SummaryState) -> SummaryState:
    """Upload doc to bucket"""
    print("\033[92m--- Listing blobs in bucket ---\033[00m")
    
    bucket_name = os.getenv("BUCKET_NAME")
    video_folder_prefix = os.getenv("VIDEO_FOLDER_PREFIX")
    output_folder_prefix = os.getenv("OUTPUT_FOLDER_PREFIX")
    
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
        return {
            "input_uris": new_wavs,
            "gcs_output_path": "gs://cbm-cgs-acb-km-assets/km-video/results/"
        }
    else:
        raise ValueError("Input uris are empty, exit the process")