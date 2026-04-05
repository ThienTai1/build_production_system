import os
import sys
import logging
import traceback
from langchain_core.documents import Document

# Thêm đường dẫn để nhận diện module app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.db.milvus import VectorStoreManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_ingest():
    """
    Perform sample data ingestion into the Milvus Vector Database.
    """
    logger.info("🚀 Starting sample data ingestion process...")
    
    try:
        # 1. Sample Data (Knowledge Base)
        docs = [
            Document(
                page_content="The Agent system is running on Mac M4 with Gemma 2.", 
                metadata={"category": "tech"}
            ),
            Document(
                page_content="Milvus is a high-performance vector database purpose-built for AI.", 
                metadata={"category": "db"}
            ),
            Document(
                page_content="LangGraph helps orchestrate the reasoning workflows of AI Agents.", 
                metadata={"category": "ai"}
            ),
            Document(
                page_content="Ollama provides local serving for large language models like Llama 3 and Gemma 2.", 
                metadata={"category": "llm"}
            )
        ]

        # 2. Initialize Vector Store via Manager (Singleton)
        logger.info(f"🔗 Connecting to Milvus at: {settings.MILVUS_URL}")
        vector_db = VectorStoreManager.get_vector_store()
        
        # 3. Ingest Data
        logger.info(f"📥 Ingesting {len(docs)} documents into collection '{settings.COLLECTION_NAME}'...")
        vector_db.add_documents(docs)
        
        logger.info("✅ SUCCESS! Data has been ingested into Milvus.")
        
    except Exception as e:
        logger.error(f"❌ Lỗi trong quá trình Ingest: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    run_ingest()