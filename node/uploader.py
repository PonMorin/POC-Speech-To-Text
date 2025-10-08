import os
import json
from dotenv import load_dotenv
load_dotenv()
from state import SummaryState

def upload_doc_to_bucket(state: SummaryState) -> SummaryState:
    """Upload doc to bucket"""
    print("\033[92m--- Uploading doc to bucket ---\033[00m")
    filename = state["filename"].split('.')[0]
    
    out_dir = f"output/{filename}"
    os.makedirs(out_dir, exist_ok=True)

    # Save evaluation score
    with open(f"{out_dir}/score.json", "w") as f:
        json.dump(
            {
                "evaluation_score": state.get("eval_score", None),
                "process_time_taken": state.get("time_taken", None)
            },
            f,
            indent=2
        )

    # Save raw text
    with open(f"{out_dir}/raw.md", "w") as f:
        f.write(state["raw_text"])

    # Save summary
    with open(f"{out_dir}/summary.md", "w") as f:
        f.write(state["summary"])
        
    from gcp.bucket import upload_to_gcs
    
    bucket_name = os.getenv("BUCKET_NAME")
    output_folder_prefix = os.getenv("OUTPUT_FOLDER_PREFIX")

    _ = upload_to_gcs(
        client=state["gcs_client"], 
        bucket_name=bucket_name, 
        file_obj=f"output/{filename}/summary.md", 
        destination_blob_name=f"{output_folder_prefix}/{filename}.md")
    
    return state

    # ---- Uploading operation
    # ---- Delete operation