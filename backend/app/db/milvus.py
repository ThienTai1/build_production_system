import logging
from typing import Optional
from langchain_milvus import Milvus, BM25BuiltInFunction
from langchain_ollama import OllamaEmbeddings
from pymilvus import MilvusClient, connections
from app.core.config import settings

logger = logging.getLogger(__name__)

class VectorStoreManager:
    _instance: Optional[Milvus] = None
    _embeddings: Optional[OllamaEmbeddings] = None

    @classmethod
    def get_embeddings(cls) -> OllamaEmbeddings:
        if cls._embeddings is None:
            logger.info("Initializing Ollama Embeddings...")
            cls._embeddings = OllamaEmbeddings(
                model=settings.EMBED_MODEL,
                base_url=settings.OLLAMA_BASE_URL
            )
        return cls._embeddings

    @classmethod
    def connect_milvus(cls):
        """
        Ensures the Milvus connection is established and registered in the global pool.
        The 'has_connection' check prevents duplicate connection errors.
        """
        try:
            client = MilvusClient(uri=settings.MILVUS_URL)
            internal_alias = client._using
            
            # Parse host and port from the URL for the connection pool
            if "://" in settings.MILVUS_URL:
                host_port = settings.MILVUS_URL.split("://")[1]
            else:
                host_port = settings.MILVUS_URL

            host = host_port.split(":")[0]
            port = host_port.split(":")[1] if ":" in host_port else "19530"

            if not connections.has_connection(internal_alias):
                logger.info(f"Connecting to Milvus at {host}:{port} with alias {internal_alias}")
                connections.connect(alias=internal_alias, host=host, port=port)
            return internal_alias
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            raise

    @classmethod
    def get_vector_store(cls) -> Milvus:
        if cls._instance is None:
            logger.info("Initializing Milvus Vector Store...")
            # We call connect_milvus to sync the global connection pool
            cls.connect_milvus()
            
            cls._instance = Milvus(
                embedding_function=cls.get_embeddings(),
                builtin_function=BM25BuiltInFunction(),
                vector_field=["dense", "sparse"],
                collection_name=settings.COLLECTION_NAME,
                connection_args={"uri": settings.MILVUS_URL},
                auto_id=True,
                drop_old=False
            )
        return cls._instance

def get_vector_store() -> Milvus:
    """Helper function to maintain backward compatibility if needed."""
    return VectorStoreManager.get_vector_store()