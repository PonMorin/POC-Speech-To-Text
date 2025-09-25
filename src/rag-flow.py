# ENV
from dotenv import load_dotenv
from config.GCP import load_credentials_base64

load_dotenv()
load_credentials_base64()

# LangGraph Stuff
from langgraph.graph import END, StateGraph
from state import GraphState

# Nodes
from node.rag_node import (
    connect_pinecone,
    init_vector_store,
    load_document,
    process_document,
    summarize_document

)

from node.speech_to_text import batch_recognize_gcs

    
# Create a graph
workflow= StateGraph(GraphState)

# Create Nodes

def dummy(state: GraphState) :
    ''
    

# Add Node to the flow
workflow.add_node('SpeechToText', batch_recognize_gcs)
workflow.add_node('SUMMARIZE', summarize_document)

# Add Edge to the flow
workflow.set_entry_point('SpeechToText')
workflow.add_edge('SpeechToText', 'SUMMARIZE')

# Compile
app= workflow.compile()

# Create Visual
app.get_graph().draw_mermaid_png(output_file_path="graph.png")

# Run
# print(app.invoke({'original_question' : 'อยากได้ File การซ่อมของวันที่ 10'})['result_summarize'])