import time
from dotenv import load_dotenv
load_dotenv()
from state import GraphState

def upload_doc_to_bucket(state: GraphState) -> GraphState:
    """Upload doc to bucket"""
    print("\033[92m--- Uploading doc to bucket ---\033[00m")
    
    with open("final.md", "w") as f:
        f.write(state["result_summarize"])
    
    # Calculate time
    start_time = state.get("time_taken", None)
    if start_time:
        elapsed_time = time.time() - start_time
        print(f"\n\033[96m ===========> ⏱️ Speech To Text operation time taken: {elapsed_time/60:.2f} minutes <===========\n\033[00m")
    else:
        print("\nStart time not found")
    
    return state

    # ---- Uploading operation
    # ---- Delete operation