import os
from Config.GCP import load_credentials_base64
from dotenv import load_dotenv
load_dotenv()
from RagFunc.function import load_document, process_document, init_vector_store

import json
import logging


import json

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="storeData2.log",  # เพิ่มตรงนี้
    filemode='a'
)


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
    

