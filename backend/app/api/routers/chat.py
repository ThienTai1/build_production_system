import os
import time
import logging
from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse
from app.engine.graph import app_agent
from app.core.monitoring import (
    REQUEST_COUNT, 
    AGENT_LATENCY, 
    ERROR_COUNT, 
    RESPONSE_LENGTH, 
    RETRIEVED_DOCS_COUNT
)
from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Langfuse CallbackHandler using environment variables as recommended
langfuse_handler = None
if settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY:
    # Set environment variables so the SDK can pick them up automatically
    os.environ["LANGFUSE_PUBLIC_KEY"] = settings.LANGFUSE_PUBLIC_KEY
    os.environ["LANGFUSE_SECRET_KEY"] = settings.LANGFUSE_SECRET_KEY
    os.environ["LANGFUSE_HOST"] = settings.LANGFUSE_HOST
    
    try:
        from langfuse.langchain import CallbackHandler
        # Initialize without arguments as it relies on environment variables
        langfuse_handler = CallbackHandler()
        logger.info("Langfuse CallbackHandler initialized successfully from environment.")
    except Exception as e:
        # Now logger is defined, this will work correctly
        logger.error(f"Failed to initialize Langfuse CallbackHandler: {e}")

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main endpoint to process user questions via the AI Agent.
    """
    REQUEST_COUNT.inc()
    start_time = time.time()
    
    try:
        logger.info(f"Received chat request: {request.question}")
        
        # Execute Agent logic through LangGraph
        inputs = {"question": request.question}
        
        # Pass the handler in the 'callbacks' config
        callbacks = [langfuse_handler] if langfuse_handler else []
            
        result = await app_agent.ainvoke(inputs, config={"callbacks": callbacks})
        
        # Record metrics
        duration = time.time() - start_time
        AGENT_LATENCY.observe(duration)
        
        # Performance/Quality metrics
        if result.get("generation"):
            RESPONSE_LENGTH.observe(len(result["generation"]))
        if result.get("documents"):
            RETRIEVED_DOCS_COUNT.observe(len(result["documents"]))
        
        return ChatResponse(
            answer=result["generation"],
            latency=f"{duration:.2f}s",
            sources=result["documents"]
        )
    except Exception as e:
        ERROR_COUNT.inc()
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
