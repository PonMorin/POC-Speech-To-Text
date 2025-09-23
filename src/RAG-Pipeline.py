import os
from Config.GCP import load_credentials_base64
from dotenv import load_dotenv
load_dotenv()

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
import json
import logging
from uuid import uuid4

from pythainlp.tokenize import word_tokenize

import json

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="storeData2.log",  # เพิ่มตรงนี้
    filemode='a'
)

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
        # contextualized_chunks = _generate_contextualized_chunks(document, chunks)
        # print("Generate Context Chuncks Successful")
        # translate_chunks = _translate_contextualized_chunks(chunks)
        # print("Translate Context Chuncks Successful")
        return chunks

def _generate_contextualized_chunks(document: str, chunks: List[Document]) -> List[Document]:
    """
    Generate contextualized chunks for a document.
    """
    contextualized_chunks = []
    count = 1
    for chunk in chunks:
        context = _generate_context(document, chunk.page_content)
        contextualized_content = f"{context}\n\n{chunk.page_content}"
        contextualized_chunks.append(Document(page_content=contextualized_content, metadata=chunk.metadata))
        print(f"Chunck {count} Complete!")
        count += 1
    return contextualized_chunks

def _translate_contextualized_chunks(chunks: List[Document]) -> List[Document]:
    """
    Generate contextualized chunks for a document.
    """
    translate_chunks = []
    count = 1
    for chunk in chunks:
        context = _translate_context(chunk.page_content)
        translate_content = f"{context}"
        translate_chunks.append(Document(page_content=translate_content, metadata=chunk.metadata))
        print(f"Chunck {count} Complete!")
        count += 1
    return translate_chunks

def _generate_context(document:str, chunks: str) -> str:
    """
    Generate context for a specific chunk using the language model.
    """
    model = init_chat_model("gemini-2.0-flash", model_provider="google_vertexai", temperature= 0)

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
    model = init_chat_model("gemini-2.5-flash", model_provider="google_vertexai", temperature= 0)

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

def main(vector_index:str, json_file_path: str, id_counters: int = 1, id_prefix: str = "test", namespace: str = "thai-namespace", profession_type: str = "promotion_profession"):
    logging.info("🔐 Initializing credentials and vector DB...")
    load_credentials_base64()
    vector_db, index = init_vector_store(vector_index)
    logging.info("✅ Vector store initialized.")

    try:
        with open(json_file_path, "r") as f:
            data = json.load(f)
        logging.info("📄 Loaded document index JSON.")
    except Exception as e:
        logging.error(f"❌ Failed to load JSON file: {e}")
        exit(1)

    files = data.get(profession_type, {})

    id_counter = id_counters  # เริ่ม id ที่ 1
    for filename, info in files.items():
        source_name = filename
        source_link = info.get("link")
        tarPath = info.get("tarpath")

        if not source_link or not tarPath:
            logging.warning(f"⚠️ Missing link or path for {source_name}, skipping...")
            continue

        logging.info(f"📥 Processing file: {source_name}")
        logging.info(f"📁 Path: {tarPath}")
        logging.info(f"🔗 Link: {source_link}")

        try:
            documents = load_document(tarPath)
            logging.info(f"📄 Loaded {len(documents)} documents from: {tarPath}")
        except Exception as e:
            logging.error(f"❌ Failed to load documents for {source_name}: {e}")
            continue

        raw_metadata = [doc.metadata.get("source", "UNKNOWN_SOURCE") for doc in documents]

        # เพิ่ม metadata
        for i, doc in enumerate(documents):
            doc.metadata["file"] = f"{source_name}"
            doc.metadata["source"] = f"[{source_name}]({source_link})"

        # แปลงเป็น chunks และส่งเข้า vector DB
        for idx, (doc, raw) in enumerate(zip(documents, raw_metadata), start=1):
            try:
                page = doc.metadata.get("page", "N/A")
                logging.info(f"📑 Processing doc {idx} --> {raw} | Page: {page}")

                original_chunks = process_document(doc, chunk_size=450, chunk_overlap=150)

                # สร้าง id แบบเลขเรียงลำดับ (ต่อจาก id_counter)
                uuids = [f"{id_prefix}-{str(i)}" for i in range(id_counter, id_counter + len(original_chunks))]
                id_counter += len(original_chunks)  # เพิ่มค่าต่อไปสำหรับรอบถัดไป
                logging.info(f"✂️ Split into {len(original_chunks)} chunks. Adding to vector DB...")

                # vector_db.add_documents(original_chunks, ids=uuids, namespace="thai-namespace")
                vector_db.add_documents(original_chunks, ids=uuids, namespace=namespace)
                logging.info(f"✅ Successfully added {len(original_chunks)} chunks to vector DB.")

            except Exception as e:
                logging.error(f"❌ Error processing document {idx} --> {raw} in {source_name}: {e}")
                continue


    logging.info("🎉 All files processed.")

if __name__ == "__main__":
    json_file_path = "/Users/ponmorin/Documents/SCG_KM_ChatBot/SCG-RAG-StoreData/json/ci_doc.json"
    vector_index = "ci-profession"
    id_counters = 1  # เริ่ม id ที่ 280
    id_prefix = "cip"  # Prefix สำหรับ id
    namespace = "eng-namespace"  # Namespace สำหรับ Pinecone
    profession_type = "ci"  # ประเภทวิชาชีพที่ต้องการประมวลผล
    logging.info("🚀 Starting document processing...")
    main(vector_index, json_file_path, id_counters, id_prefix, namespace, profession_type)
    print("All files processed successfully.")
    

