from utils.parser import parse_yaml

EMBEDDING_MODEL = "models/gemini-embedding-001" 

OUTPUT_LANGS: list[str] = ["th-TH"]
SPEECH_TO_TEXT_MODEL: str = "long"
LOCATION: str = "global"

CHUNK_SIZE: int = 1250
CHUNK_OVERLAP: int = 500

MAX_LINE: int = 200

PROMPTS: dict = parse_yaml('prompt/summarization.yaml')