from typing import TypedDict
from pandas import DataFrame

# Create State
class GraphState(TypedDict):
    raw_text: str
    result_summarize: str
    audio_uri: str
    gcs_output_path: str