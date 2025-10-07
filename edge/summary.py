from langgraph.graph import END
from state import SummaryState

# def should_refine(state: RefineState):
#     if state["index"] >= len(state["contents"]):
#         return END
#     else:
#         return "refine_summary"
    
def should_continue(state: SummaryState):
    if state["index"] < len(state["contents"]):
        return "HAVE LEFTOVERS"
    else:
        return "NO LEFTOVERS"