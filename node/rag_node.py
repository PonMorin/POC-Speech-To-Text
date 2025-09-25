from pinecone import Pinecone
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredPowerPointLoader
from langchain.schema import Document
from typing import List, Tuple
from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import ChatPromptTemplate
from pythainlp.tokenize import word_tokenize
from utils.const import CHUNK_SIZE, CHUNK_OVERLAP
import os
from dotenv import load_dotenv
load_dotenv()
from utils.splitter import text_splitter

def connect_pinecone(index_name:str):
    pc = Pinecone(
        # api_key=os.getenv("PINECONE_API_KEY")
    )
    index = pc.Index(index_name)
    return index

def init_vector_store(index_names:str):
    index_name = index_names
    index = connect_pinecone(index_name)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vector_store = PineconeVectorStore(index=index, embedding=embeddings)
    return vector_store, index_name

def load_document(tarPath):
    documents = []
    for root, dirs, files in os.walk(tarPath):
        for file in files:
            if file.endswith(".md"):
                loader = TextLoader(os.path.join(root, file), encoding="utf-8")
                documents.extend(loader.load())
            elif file.endswith(".pdf"):
                loader = PyPDFLoader(os.path.join(root, file))
                documents.extend(loader.load())
            elif file.endswith(".pptx") or file.endswith(".ppt"):
                loader = UnstructuredPowerPointLoader(os.path.join(root, file))
                documents.extend(loader.load())
    return documents

def process_document(document:str) -> Tuple[List[Document], List[Document]]:
        """
        Process a document by splitting it into chunks and generating context for each chunk.
        """
        splitter = text_splitter(CHUNK_SIZE, CHUNK_OVERLAP)
        chunks = splitter.split_documents([document])
        print(f"Split {len(chunks)} Chunks Successful.")
        return chunks

def _generate_context(document:str, chunks: str) -> str:
    """
    Generate context for a specific chunk using the language model.
    """
    model = ChatVertexAI(
        model="gemini-2.5-flash",
        temperature=0
    )

    prompt = ChatPromptTemplate.from_template("""
<document>
{document}
</document>

Here is the chunk we want to situate within the organizational knowledge base:
<chunk>
{chunk}
</chunk>

Please provide a concise context that includes:
1. The knowledge category/type (e.g., policy, procedure, technical guide, best practice, FAQ)
2. The specific department, team, or function this relates to
3. The main topic or subject area being addressed
4. Any relevant version, date, or approval status if mentioned
5. Key prerequisites or related information needed to understand this chunk

Provide only the contextual description in 50-100 words, focusing on what would help someone quickly understand where this information fits within the organization's knowledge system. 
""")
    messages = prompt.format_messages(document=document, chunk=chunks)
    response = model.invoke(messages)
    return response.content

def _translate_context(chunks: str) -> str:
    """
    Generate context for a specific chunk using the language model.
    """
    model = ChatVertexAI(
        model="gemini-2.5-flash",
        temperature=0
    )

    prompt = ChatPromptTemplate.from_template("""
As an expert professional translator, your task is to provide a high-quality, accurate, and natural translation of the provided text. Your primary goal is to ensure the translated text perfectly mirrors the original's meaning, tone, and exact formatting, while reading fluently and idiomatically in the target language.

**Translation Requirements:**

*   **Accuracy & Fidelity:** Translate all content precisely, ensuring no information is added, omitted, or misinterpreted. Every nuance and factual detail must be preserved.
*   **Naturalness & Fluency:** The translation must read as if it were originally written in the target language, using appropriate idiomatic expressions, natural phrasing, and a native-like flow. Avoid literal translations that sound awkward or unnatural.
*   **Tone & Register Preservation:** Maintain the original tone (e.g., formal, informal, humorous, serious, persuasive, technical, academic) and register consistently throughout the translated text.
*   **Format & Structure Replication:** Replicate the exact formatting of the source text, including but not limited to:
    *   Headings and subheadings
    *   Bullet points and numbered lists
    *   Bold, italics, underlines, and other text styling
    *   Paragraph breaks and line breaks
    *   Tables, charts, and code blocks (if applicable)
    *   Any other structural or visual elements.
*   **Contextual Understanding:** Demonstrate a deep understanding of the source text's subject matter and context to select the most appropriate vocabulary and phrasing.
*   **Handling Ambiguity/Unknowns:** If the meaning of a specific term or phrase is genuinely unknown or ambiguous, translate it as literally as possible without inventing meaning. If it's a proper noun or a term conventionally untranslatable, retain the original term.

Your output should *only* be the translated text, preserving all original formatting.

---

**Source Text:** 
{input}

**Target Language:** English
""")
    messages = prompt.format_messages(input=chunks)
    response = model.invoke(messages)
    return response.content
