from langgraph.graph import END
from state import SummaryState

# def should_refine(state: RefineState):
#     if state["index"] >= len(state["contents"]):
#         return END
#     else:
#         return "refine_summary"

def is_empty(state: SummaryState):
    raw_text = state.get("raw_text", None)
    if not raw_text:
        print("\033[91mText is empty, skip this audio\033[00m")
        if state["index"] == len(state["input_uris"]):
            print("\033[91mNo leftovers\033[00m")
            return "NO LEFTOVERS"
        return "EMPTY"
    else:
        return "NOT EMPTY"
    
def should_continue(state: SummaryState):
    if state["index"] < len(state["input_uris"]):
        return "HAVE LEFTOVERS"
    else:
        print("\033[91mNo leftovers\033[00m")
        return "NO LEFTOVERS"