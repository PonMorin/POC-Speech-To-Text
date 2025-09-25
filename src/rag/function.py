from pinecone import Pinecone

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader, UnstructuredPowerPointLoader
from langchain.schema import Document, SystemMessage
import duckdb
from typing import List, Tuple
from glob import glob
# Not implement yet
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from uuid import uuid4

from pythainlp.tokenize import word_tokenize

import os

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

def process_document(document:str, chunk_size:int, chunk_overlap:int) -> Tuple[List[Document], List[Document]]:
        """
        Process a document by splitting it into chunks and generating context for each chunk.
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size= chunk_size, 
            chunk_overlap= chunk_overlap,
            length_function=lambda text: len(word_tokenize(text, engine='newmm')),
            separators=[
                "\n\n",
                "\n",
                " ",
                ".",
                ",",
                "\u200b",  # Zero-width space
                "\uff0c",  # Fullwidth comma
                "\u3001",  # Ideographic comma
                "\uff0e",  # Fullwidth full stop
                "\u3002",  # Ideographic full stop
                "",
            ],
        )
        chunks = text_splitter.split_documents([document])
        print(f"Split {len(chunks)} Chunks Successful.")
        return chunks

def summarize_document(document: str) -> str:
    """
    Summarize the content of a document using the language model.
    """
    model = init_chat_model("gemini-2.5-flash", model_provider="google_vertexai", temperature= 0)

    prompt = ChatPromptTemplate.from_template("""
<document>
{document}
</document>

Please provide a concise summary of the document, focusing on the main points and key information. 
""")
    messages = prompt.format_messages(document=document)
    response = model.invoke(messages)
    return response.content
