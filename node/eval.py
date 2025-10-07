import numpy as np
from state import SummaryState
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from utils.const import EMBEDDING_MODEL
from utils.text import clean_md
from pythainlp.tokenize import word_tokenize

def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def chunk_text_by_tokens(text, max_tokens=500):
    """
    Split text into chunks of max_tokens using Thai word tokenizer.
    """
    tokens = word_tokenize(text, engine="newmm")
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk = "".join(tokens[i:i+max_tokens])  # join back into string
        chunks.append(chunk)
    return chunks

def similarity(state: SummaryState) -> SummaryState:
    """
    Evaluate source text with summary
    """
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)

    # Extract inputs
    transcript = state["raw_text"]
    summary = clean_md(state["summary"])

    # Embed summary
    summary_vector = embeddings.embed_query(summary)

    # Token-based chunking
    transcript_chunks = chunk_text_by_tokens(transcript, max_tokens=500)

    # Embed chunks
    transcript_vectors = [embeddings.embed_query(chunk) for chunk in transcript_chunks]

    # Compute similarities
    similarities = [cosine_similarity(vec, summary_vector) for vec in transcript_vectors]

    # Aggregate similarity (average here, but could be max/weighted)
    avg_similarity = float(np.mean(similarities))

    return {
        "eval_score": avg_similarity,
    }