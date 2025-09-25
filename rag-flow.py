from dotenv import load_dotenv
from config.GCP import load_credentials_base64

load_dotenv()
load_credentials_base64()

from langgraph.graph import END, StateGraph
from state import GraphState
from node.rag_node import summarize_document
from node.speech_to_text import batch_recognize_gcs


workflow = StateGraph(GraphState)


workflow.add_node('SpeechToText', batch_recognize_gcs)
workflow.add_node('SUMMARIZE', summarize_document)

# Set the entry point and edges
workflow.set_entry_point('SpeechToText')
workflow.add_edge('SpeechToText', 'SUMMARIZE')
workflow.add_edge('SUMMARIZE', END)

# Compile the graph
app = workflow.compile()

# Create a visual of the graph
# app.get_graph().draw_mermaid_png(output_file_path="graph.png")

# --- Example of how to run the graph ---
if __name__ == "__main__":
    # Define the initial state (inputs for the first node)
    initial_state = {
        "audio_uri": "gs://cbm-cgs-acb-km-assets/km-video/standard_output.wav",
        "gcs_output_path": "gs://cbm-cgs-acb-km-assets/km-video/results/"
    }
    
    print("Invoking graph...")
    
    final_state = app.invoke(initial_state)
    
    print("\n--- Final Result ---")
    print(final_state['result_summarize'])