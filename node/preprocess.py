from pythainlp.tokenize import word_tokenize
from pythainlp.corpus import thai_stopwords
from state import SummaryState
from langchain.schema import Document
from utils.text import text_splitter
from utils.const import CHUNK_SIZE, CHUNK_OVERLAP

def chunk_document(state: SummaryState) -> SummaryState:
    """
    Chunk the document into smaller pieces for summarization.
    """
    print("\033[92m--- Chunking Documents ---\033[00m")
    
    raw_text = state["cleaned_text"]
    if not raw_text:
        print("No text to summarize.")
        return {"summary": "ไม่มีข้อความสำหรับสรุป"}

    splitter = text_splitter(CHUNK_SIZE, CHUNK_OVERLAP)
    
    doc = Document(page_content=raw_text)
    docs = splitter.split_documents([doc])
    
    return {
        "contents": docs
    }

def remove_stop_words(state: SummaryState) -> SummaryState:
    raw_text = state["raw_text"]

    # 1. Tokenize
    list_words = word_tokenize(raw_text, engine="newmm")

    # 2. Get default stopwords from PyThaiNLP
    stopwords = set(thai_stopwords())

    # 3. Add my own stopwords
    custom_stopwords = {"ครับ", "ค่ะ", "นะ", "ฮะ", "พี่"}
    stopwords = stopwords.union(custom_stopwords)

    # 4. Remove stopwords (keep only words not in stopwords)
    clean_tokens = [w for w in list_words if w not in stopwords]

    # 4. Join back cleaned text
    cleaned_text = "".join(clean_tokens)
    
    return {
        "cleaned_text": cleaned_text
    }