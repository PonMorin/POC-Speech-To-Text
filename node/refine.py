from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from state import RefineState
from utils.const import PROMPTS
from langchain_google_vertexai import ChatVertexAI

async def generate_initial_summary(state: RefineState, config: RunnableConfig):
    llm = ChatVertexAI(
        model="gemini-2.5-flash",
        temperature=0
    )
    
    summarize_template = PROMPTS["INIT_SUMMARY_PROMPT"]
    summarize_prompt = ChatPromptTemplate(
        [
            ("human", summarize_template),
        ]
    )
    initial_summary_chain = summarize_prompt | llm | StrOutputParser()

    summary = await initial_summary_chain.ainvoke(
        state["contents"][0],
        config,
    )
    return {"summary": summary, "index": 1}


async def refine_summary(state: RefineState, config: RunnableConfig):
    llm = ChatVertexAI(
        model="gemini-2.5-flash",
        temperature=0
    )
    
    content = state["contents"][state["index"]]
    
    # Refining the summary with new docs
    refine_template = PROMPTS["REFINE_SUMMARY_PROMPT"]
    refine_prompt = ChatPromptTemplate([("human", refine_template)])

    refine_summary_chain = refine_prompt | llm | StrOutputParser()

    summary = await refine_summary_chain.ainvoke(
        {"existing_answer": state["summary"], "context": content},
        config,
    )

    return {"summary": summary, "index": state["index"] + 1}