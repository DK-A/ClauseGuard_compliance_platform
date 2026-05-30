import os
import logging
from backend.hardware.registry import ModelRegistry

# Set logging level
log_level_str = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level_str, logging.INFO))
logger = logging.getLogger("ClauseGuardConfig")

# Global variables and environment configuration
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
LLAMACPP_BASE_URL = os.environ.get("LLAMACPP_BASE_URL", "http://localhost:8080")
CHROMA_PATH = os.environ.get("CHROMA_PATH", "chroma_db")
DB_PATH = os.environ.get("DB_PATH", "clauseguard.db")
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")

# Create Model Registry singleton
_registry = ModelRegistry()

logger.info(f"Initialized ClauseGuard hardware profile: {_registry.profile.value}")

def get_llm():
    return _registry.get_llm()

def get_embedding_model():
    return _registry.get_embedding_model()

def get_reasoning_config():
    return _registry.get_reasoning_config()

def get_registry() -> ModelRegistry:
    return _registry

def get_profile():
    return _registry.profile
