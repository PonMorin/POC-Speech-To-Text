from langgraph.graph import START, END, StateGraph
from state import GraphState
from node.speech_to_text import batch_recognize_gcs, summarize_document
from node.bucket import upload_doc_to_bucket

from dotenv import load_dotenv
from config.GCP import initialize_gcs_client
load_dotenv()
initialize_gcs_client()


# --- Example of how to run the graph ---
if __name__ == "__main__":
    
    workflow = StateGraph(GraphState)
    workflow.add_node('SPEECH TO TEXT', batch_recognize_gcs)
    workflow.add_node('SUMMARIZE', summarize_document)
    workflow.add_node('UPLOAD DOC', upload_doc_to_bucket)

    # Set the entry point and edges
    workflow.add_edge(START, 'SPEECH TO TEXT')
    workflow.add_edge('SPEECH TO TEXT', 'SUMMARIZE')
    workflow.add_edge('SUMMARIZE', 'UPLOAD DOC')
    workflow.add_edge('UPLOAD DOC', END)

    # Compile the graph
    app = workflow.compile()

    # Create a visual of the graph
    # app.get_graph().draw_mermaid_png(output_file_path="graph.png")

    initial_state = {
        "audio_uri": "gs://cbm-cgs-acb-km-assets/km-video/อบรม Burner Design & Operation (TP Training_วชช.ผลิต)-20241028_083859-Meeting Recording.wav",
        "gcs_output_path": "gs://cbm-cgs-acb-km-assets/km-video/results/"
    }
    
    final_state = app.invoke(initial_state)