import os
import asyncio
from dotenv import load_dotenv
load_dotenv()
from typing import List
from langgraph.graph import START, END, StateGraph
from state import EtlState
from node.wav_convertor import convert_to_wav_specific
from config.GCP import initialize_gcs_client
from edge.summary import should_continue, is_empty

async def main():
    # Nodes
    workflow = StateGraph(EtlState)
    workflow.add_node("CONVERT TO WAV", convert_to_wav_specific)

    # Edges
    workflow.add_edge(START, "CONVERT TO WAV")
    workflow.add_edge("CONVERT TO WAV", END)
    
    # Compile the graph
    app = workflow.compile()

    # Create a visual of the graph
    # app.get_graph().draw_mermaid_png(output_file_path="assets/etl_graph.png")

    data_path: str = "data"
    output_path: str = "data/wav"
    input_files: List[str] = os.listdir(data_path)
    initial_state = {
        "input_files": input_files,
        "output_file": output_path
    }
    
    _ = await app.ainvoke(initial_state)
    print("\n\033[94mProcess is done!\033[00m")

if __name__ == "__main__":
    initialize_gcs_client()
    asyncio.run(main())