from typing import TypedDict, List
from google.cloud.storage.client import Client
class SummaryState(TypedDict):
    gcs_client: Client
    filename: str
    input_uris: List[str]
    audio_uri: str
    gcs_output_path: str
    raw_text: str
    total_lines: int
    cleaned_text: str
    contents: List[str]
    summary: str
    eval_score: float
    time_taken: float
    index: int
    
class EtlState(TypedDict):
    input_files: List[str]
    output_file: str
    

# class RefineState(TypedDict):
#     raw_text: str
#     audio_uri: str
#     gcs_output_path: str
#     contents: List[str]
#     index: int
#     summary: str