import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from langchain_google_vertexai import ChatVertexAI
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from pythainlp.tokenize import word_tokenize
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from config.gcp import initialize_gcs_client

if __name__ == "__main__":
    
    initialize_gcs_client()
    
    transcript: str  
    with open("output/transcript_output.md") as f:
        transcript = f.read()
        
    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=450, 
        chunk_overlap=150,
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
    
    doc = Document(page_content=transcript)
    docs = text_splitter.split_documents([doc])

    llm = ChatVertexAI(
        model="gemini-2.5-flash",
        temperature=0
    )
    
    question_template = """
    Act as a professional technical meeting minutes writer. 
    Tone: formal
    Format: Technical meeting summary
    Tasks:
    - output as **Thai language**
    - highlight action items and owners
    - highlight the agreements
    - Use bullet points if needed
    {text}
    CONCISE SUMMARY IN THAI:
    """
    
    question_prompt = PromptTemplate(template=question_template, input_variables=["text"])
    
    refine_template = """
    Your job is to produce a final summary
    We have provided an existing summary up to a certain point: {existing_answer}
    We have the opportunity to refine the existing summary
    (only if needed) with some more context below.
    ------------
    {text}
    ------------
    """
    
    refine_prompt = PromptTemplate(
        template=refine_template,
        input_variables=["existing_answer", "text"],
    )
    
    chain = load_summarize_chain(
        llm,
        chain_type="refine",
        return_intermediate_steps=True,
        question_prompt=question_prompt,
        refine_prompt=refine_prompt,
    )
    
    resp = chain.invoke({"input_documents": docs}, return_only_outputs=True)
    
    print("\n")
    print(resp)