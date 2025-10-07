from langchain.chains.summarize import load_summarize_chain
from langchain.chains.summarize.chain import BaseCombineDocumentsChain
from langchain.prompts import PromptTemplate
from langchain_google_vertexai import ChatVertexAI
from utils.const import PROMPTS
from typing import List, Literal

async def summarizer(docs: List[str], method: Literal["refine", "map_reduce"] = "refine"):
    
    llm = ChatVertexAI(
        model="gemini-2.5-flash",
        temperature=0
    )
    
    chain: BaseCombineDocumentsChain
    
    if method == "refine":
        question_prompt = PromptTemplate(
            template=PROMPTS["INIT_SUMMARY_PROMPT"], 
            input_variables=["text"]
        )
        
        refine_prompt = PromptTemplate(
            template=PROMPTS["REFINE_SUMMARY_PROMPT"],
            input_variables=["existing_answer", "text"],
        )
        
        chain = load_summarize_chain(
            llm,
            chain_type="refine",
            question_prompt=question_prompt,
            refine_prompt=refine_prompt,
        )

    elif method == "map_reduce":
        map_prompt = PromptTemplate(
            input_variables=["text"],
            template=PROMPTS["MAP_PROMPT"]
        )

        reduce_prompt = PromptTemplate(
            input_variables=["text"],
            template=PROMPTS["REDUCE_PROMPT"]
        )
        
        chain = load_summarize_chain(
            llm,
            chain_type="map_reduce",
            map_prompt=map_prompt,
            combine_prompt=reduce_prompt,
            return_intermediate_steps=True
        )
        
    else:
        raise "This type of summarizer is not supported"
    
    response = await chain.ainvoke({"input_documents": docs})
    summary_text = response['output_text']
    
    print("\033[93m✅ Summarization complete\033[00m")
    
    return summary_text
    