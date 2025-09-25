from dotenv import load_dotenv
load_dotenv()
from state import GraphState

def upload_doc_to_bucket(state: GraphState) -> GraphState:
    with open("final.md", "w") as f:
        f.write(state["result_summarize"])
    
    return state
    # ---- Uploading operation
    
    # ---- Delete operation