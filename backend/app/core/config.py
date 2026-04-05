from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Senior AI Agent System"
    DEBUG: bool = False
    
    # LLM Settings
    LLM_MODEL: str = "gemma4"
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    
    # Embedding Settings
    EMBED_MODEL: str = "nomic-embed-text"
    
    # Vector Database Settings
    MILVUS_URL: str = "http://127.0.0.1:19530"
    COLLECTION_NAME: str = "ai_knowledge_base"

    # Langfuse Settings
    LANGFUSE_SECRET_KEY: Optional[str] = None
    LANGFUSE_PUBLIC_KEY: Optional[str] = None
    LANGFUSE_HOST: str = "http://localhost:3002"

    # Environment file configuration
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
