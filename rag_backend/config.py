import json
import os
from pathlib import Path
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import BaseModel, Field

CONFIG_DIR = Path(__file__).parent.parent / "configs"

class Settings(BaseSettings):
    local_logging_enabled: bool = False  # or False in prod
    local_stream_enabled: bool = True    # or False in prod
    embedding_config_file: str = "embeddings.json"
    vectorstore_config_file: str = "vectorstore.json"
    llm_config_file: str = "llm.json"
    rag_config_file: str = "rag.json"
    class Config:
        env_file = ".env"

try:
    settings = Settings()
except Exception as e:
    print(f"Failed to load base settings from .env: {e}")
    raise

from rag_backend.utils.logger import get_logger
log = get_logger(__name__)

# ─────────────────────────────────────────────
# 📦 Component Config Loaders (from configs/*.json)

def load_json_config(file_name: str) -> dict:
    path = CONFIG_DIR / file_name
    try:
        with open(path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            log.info(f"Loaded config file: {file_name}")
            return cfg
    except FileNotFoundError:
        log.error(f"Config file not found: {file_name}")
        raise
    except json.JSONDecodeError as e:
        log.error(f"Invalid JSON in config '{file_name}': {e}")
        raise
    except Exception as e:
        log.error(f"Unknown error while loading config '{file_name}': {e}")
        raise

# ─────────────────────────────────────────────
# 🎯 Pydantic Models for Component Configs

class EmbeddingConfig(BaseModel):
    model_name: str
    provider: str  # "ollama", "openai", etc.
    chunk_size: int = 512
    chunk_overlap: int = 50
    device: Optional[str] = "cpu"

class VectorstoreConfig(BaseModel):
    type: str = "faiss"  # "faiss", "chromadb", etc.
    path: str
    embedding_model: str

class LLMConfig(BaseModel):
    provider: str  # "ollama", "openai", etc.
    model_name: str
    temperature: float = 0.0
    max_tokens: int = 1024

class RAGConfig(BaseModel):
    top_k: int = 5
    score_threshold: float = 5
    use_max_marginal_relevance: bool = True
    fetch_k: int = 20

# ─────────────────────────────────────────────
# 🔧 Config Accessors

def get_embedding_config() -> EmbeddingConfig:
    try:
        cfg_dict = load_json_config(settings.embedding_config_file)
        return EmbeddingConfig(**cfg_dict)
    except Exception as e:
        log.error(f"Failed to load embedding config: {e}")
        raise

def get_vectorstore_config() -> VectorstoreConfig:
    try:
        cfg_dict = load_json_config(settings.vectorstore_config_file)
        return VectorstoreConfig(**cfg_dict)
    except Exception as e:
        log.error(f"Failed to load vectorstore config: {e}")
        raise

def get_llm_config() -> LLMConfig:
    try:
        cfg_dict = load_json_config(settings.llm_config_file)
        return LLMConfig(**cfg_dict)
    except Exception as e:
        log.error(f"Failed to load LLM config: {e}")
        raise

def get_rag_config() -> RAGConfig:
    try:
        cfg_dict = load_json_config(settings.rag_config_file)
        return RAGConfig(**cfg_dict)
    except Exception as e:
        log.error(f"Failed to load RAG config: {e}")
        raise

# ─────────────────────────────────────────────
# 👇 Example usage (remove in production)
if __name__ == "__main__":
    print("Settings:")
    print(settings.dict())

    print("Embedding Config:")
    print(get_embedding_config())

    # print("Vectorstore Config:")
    # print(get_vectorstore_config())

    print("LLM Config:")
    print(get_llm_config())

    print("RAG Config:")
    print(get_rag_config())
