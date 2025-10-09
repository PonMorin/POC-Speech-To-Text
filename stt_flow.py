import asyncio
from dotenv import load_dotenv
load_dotenv()
from langgraph.graph import START, END, StateGraph
from langchain_core.runnables.graph import MermaidDrawMethod
from state import SummaryState
from node.lister import list_blobs_in_bucket
from node.speech_to_text import batch_recognize_gcs, summarize_document, get_existing_raw
from node.uploader import upload_doc_to_bucket
from node.preprocess import remove_stop_words, chunk_document
from node.eval import similarity
from config.GCP import initialize_gcs_client
from edge.summary import should_continue, is_empty

async def main():
    # Nodes
    workflow = StateGraph(SummaryState)
    workflow.add_node("SETUP AUDIO LIST", list_blobs_in_bucket)
    workflow.add_node("SPEECH TO TEXT", batch_recognize_gcs)
    # workflow.add_node("GET RAW TEXT", get_existing_raw)
    workflow.add_node("PREPROCESSING", remove_stop_words)
    workflow.add_node("CHUNKING TEXT", chunk_document)
    workflow.add_node("SUMMARIZING", summarize_document)
    workflow.add_node("EVALUATING", similarity)
    workflow.add_node("UPLOADING DOC", upload_doc_to_bucket)

    # Edges
    workflow.add_edge(START, "SETUP AUDIO LIST")
    workflow.add_edge("SETUP AUDIO LIST", "SPEECH TO TEXT")
    # workflow.add_edge("SPEECH TO TEXT", "PREPROCESSING")
    workflow.add_edge("PREPROCESSING", "CHUNKING TEXT")
    workflow.add_edge("CHUNKING TEXT", "SUMMARIZING")
    workflow.add_edge("SUMMARIZING", "EVALUATING")
    workflow.add_edge("EVALUATING", "UPLOADING DOC")
    
    # Conditional Edges
    # Check is text from audio is empty?
    workflow.add_conditional_edges(
    "SPEECH TO TEXT",
    is_empty,
        {
            "NOT EMPTY": "PREPROCESSING",
            "HAVE LEFTOVERS": "SPEECH TO TEXT",
            END: END
        }
    )
    # Check is there available input uris
    workflow.add_conditional_edges(
    "UPLOADING DOC",
    should_continue,
        {
            "HAVE LEFTOVERS": "SPEECH TO TEXT",
            END : END,
        }
    )
    
    # Compile the graph
    app = workflow.compile()

    # Create a visual of the graph
    # app.get_graph().draw_mermaid_png(output_file_path="assets/summary_graph.png")

    client = initialize_gcs_client()
    initial_state = {
        "gcs_client": client,
        "index": 0,
    }
    
    _ = await app.ainvoke(initial_state)
    print("\n\033[94mProcess is done!\033[00m")

if __name__ == "__main__":
    asyncio.run(main())