from dotenv import load_dotenv
load_dotenv()
from config.GCP import initialize_gcs_client
initialize_gcs_client()
import asyncio
from langgraph.graph import START, END, StateGraph
from state import RefineState
from node.refine import generate_initial_summary, refine_summary
from node.speech_to_text import batch_recognize_gcs, chunk_document
from edge.summary import should_refine

async def main():
    
    graph = StateGraph(RefineState)
    graph.add_node("speech_to_text", batch_recognize_gcs)
    graph.add_node("chunk_document", chunk_document)
    graph.add_node("generate_initial_summary", generate_initial_summary)
    graph.add_node("refine_summary", refine_summary)

    graph.add_edge(START, "speech_to_text")
    graph.add_edge("speech_to_text", "chunk_document")
    graph.add_edge("chunk_document", "generate_initial_summary")
    graph.add_conditional_edges("generate_initial_summary", should_refine)
    graph.add_conditional_edges("refine_summary", should_refine)
    graph.add_edge("generate_initial_summary", END)
    graph.add_edge("refine_summary", END)
    app = graph.compile()
    
    async for step in app.astream(
        {
            "audio_uri": "gs://cbm-cgs-acb-km-assets/km-video/standard_output.wav",
            "gcs_output_path": "gs://cbm-cgs-acb-km-assets/km-video/results/"
        },
        stream_mode="values",
    ):
        if summary := step.get("summary"):
            print("\n-----> ", summary)

if __name__ == "__main__":
    
    asyncio.run(main())