import os
import logging
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from opentelemetry import trace
from app.db.milvus import get_vector_store
from app.core.config import settings

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

class AgentState(TypedDict):
    question: str
    documents: List[str]
    generation: str

# --- KHỞI TẠO LLM DỰA TRÊN CẤU HÌNH ---
def get_llm():
    if settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        logger.info("Using OpenAI GPT Engine")
        return ChatOpenAI(model=settings.LLM_MODEL, api_key=settings.OPENAI_API_KEY)
    elif settings.LLM_PROVIDER == "groq" and settings.GROQ_API_KEY:
        logger.info(f"Using Groq Engine with model: {settings.LLM_MODEL}")
        return ChatGroq(model=settings.LLM_MODEL, api_key=settings.GROQ_API_KEY)
    else:
        logger.info(f"Using Local Ollama Engine: {settings.LLM_MODEL}")
        return ChatOllama(model=settings.LLM_MODEL, base_url=settings.OLLAMA_BASE_URL)

llm = get_llm()

from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder

# Global variable to cache the heavy Re-ranker model
_compression_retriever = None

def get_compression_retriever():
    global _compression_retriever
    if _compression_retriever is None:
        logger.info("Initializing HuggingFace Re-ranker model (BAAI/bge-reranker-base)...")
        # Initialize the cross-encoder model
        model = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-base")
        compressor = CrossEncoderReranker(model=model, top_n=3)
        
        # Get the base Milvus retriever, fetching 15 docs instead of 3
        vector_store = get_vector_store()
        base_retriever = vector_store.as_retriever(search_kwargs={"k": 15})
        
        # Wrap it
        _compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=base_retriever
        )
    return _compression_retriever

async def retrieve(state: AgentState):
    """
    Query the Vector Store for documents using Two-Stage Retrieval (Vector Search + Re-ranking).
    """
    with tracer.start_as_current_span("retrieve_documents") as span:
        logger.info(f"Retrieving and re-ranking documents for question: {state['question']}")
        span.set_attribute("question", state["question"])
        
        # Use the advanced two-stage retriever
        retriever = get_compression_retriever()
        docs = await retriever.ainvoke(state["question"])
        
        span.set_attribute("docs_count", len(docs))
        return {"documents": [d.page_content for d in docs]}

async def generate(state: AgentState):
    """
    Generate an answer based on the retrieved documents.
    """
    with tracer.start_as_current_span("generate_answer") as span:
        logger.info(f"Generating answer for question: {state['question']}")
        context = "\n\n".join(state['documents'])
        
        prompt = f"""You are a smart virtual assistant for the system.
        Based on the following reference materials:
        ---
        {context}
        ---

        Please answer the user's question as accurately and honestly as possible: {state['question']}
        Please keep your answer concise and to the point.
        """
        
        response = await llm.ainvoke(prompt)
        return {"generation": response.content}

# Xây dựng Workflow
workflow = StateGraph(AgentState)

workflow.add_node("retrieve", retrieve)
workflow.add_node("generate", generate)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

# Biên dịch Agent
app_agent = workflow.compile()