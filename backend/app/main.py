import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.core.config import settings
from app.api.routers import chat
from app.core.tracing import setup_tracing

# Basic logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage the application lifecycle.
    """
    logger.info(f"Starting {settings.APP_NAME}...")
    
    # Initialize Prometheus Info
    from app.core.monitoring import AGENT_INFO
    AGENT_INFO.labels(app_name=settings.APP_NAME, model=settings.LLM_MODEL).set(1)

    # Initialize Vector Store Singleton on startup
    from app.db.milvus import get_vector_store
    get_vector_store()
    yield
    logger.info(f"Shutting down {settings.APP_NAME}...")

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Start Tracing
setup_tracing(app, service_name=settings.APP_NAME)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach Prometheus endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Include Routers
app.include_router(chat.router, tags=["chat"])

@app.get("/")
async def root():
    return {
        "status": "online", 
        "app_name": settings.APP_NAME,
        "message": "Senior AI Agent System Backend is running"
    }