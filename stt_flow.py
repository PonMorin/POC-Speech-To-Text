from langgraph.graph import START, END, StateGraph
from state import SummaryState
from node.speech_to_text import batch_recognize_gcs, summarize_document, get_existing_raw
from node.bucket import upload_doc_to_bucket
from node.preprocess import remove_stop_words, chunk_document
from node.eval import similarity
import asyncio
from dotenv import load_dotenv
from config.GCP import initialize_gcs_client
load_dotenv()
from edge.summary import should_continue

async def main():
    workflow = StateGraph(SummaryState)
    workflow.add_node("SPEECH TO TEXT", batch_recognize_gcs)
    # workflow.add_node("GET RAW TEXT", get_existing_raw)
    workflow.add_node("PREPROCESSING", remove_stop_words)
    workflow.add_node("CHUNKING TEXT", chunk_document)
    workflow.add_node("SUMMARIZING", summarize_document)
    workflow.add_node("EVALUATING", similarity)
    workflow.add_node("UPLOADING DOC", upload_doc_to_bucket)

    # Set the entry point and edges
    workflow.add_edge(START, "SPEECH TO TEXT")
    workflow.add_edge("SPEECH TO TEXT", "PREPROCESSING")
    workflow.add_edge("PREPROCESSING", "CHUNKING TEXT")
    workflow.add_edge("CHUNKING TEXT", "SUMMARIZING")
    workflow.add_edge("SUMMARIZING", "EVALUATING")
    workflow.add_edge("EVALUATING", "UPLOADING DOC")
    
    workflow.add_conditional_edges(
    "UPLOADING DOC",
    should_continue,
        {
            "HAVE LEFTOVERS": "SPEECH TO TEXT",
            "NO LEFTOVERS" : END,
        }
    )
    # workflow.add_edge("UPLOADING DOC", END)

    # Compile the graph
    app = workflow.compile()

    # Create a visual of the graph
    app.get_graph().draw_mermaid_png(output_file_path="graph.png")

    # initial_state = {
    #     "input_uris": [
    #         "gs://cbm-cgs-acb-km-assets/km-video/อบรม Burner Design & Operation (TP Training_วชช.ผลิต)-20241028_083859-Meeting Recording.wav"
    #     ],
    #     "gcs_output_path": "gs://cbm-cgs-acb-km-assets/km-video/results/"
    # }
    
    # _ = await app.ainvoke(initial_state)
    # print("\n\033[94mProcess is done!\033[00m")

if __name__ == "__main__":
    initialize_gcs_client()
    asyncio.run(main())