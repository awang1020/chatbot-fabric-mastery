"""Centralized, env-driven configuration for Chatbot Fabric Mastery."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Azure OpenAI -------------------------------------------------------
    azure_openai_endpoint: str = Field(..., min_length=1)
    azure_openai_api_key: str | None = None
    azure_openai_api_version: str = "2024-10-21"
    azure_openai_chat_deployment: str = Field(..., min_length=1)
    azure_openai_chat_model: str = "gpt-4o-mini"
    azure_openai_embedding_deployment: str = Field(..., min_length=1)
    azure_openai_embedding_model: str = "text-embedding-3-small"

    # --- Paths --------------------------------------------------------------
    data_dir: Path = Path("./data/newsletters")
    storage_dir: Path = Path("./storage/chroma")
    collection_name: str = "fabric_mastery"

    # --- Indexing -----------------------------------------------------------
    chunk_size: int = Field(512, ge=128, le=8192)
    chunk_overlap: int = Field(128, ge=0, le=2048)

    # --- Retrieval & generation --------------------------------------------
    top_k: int = Field(12, ge=1, le=50)
    similarity_cutoff: float = Field(0.22, ge=0.0, le=1.0)
    temperature: float = Field(0.1, ge=0.0, le=2.0)
    max_tokens: int = Field(1024, ge=64, le=16384)

    # --- Citation display (stricter than retrieval; drives what the UI shows).
    max_citations: int = Field(3, ge=1, le=10)
    citation_similarity_cutoff: float = Field(0.35, ge=0.0, le=1.0)

    # --- Reranking (LLM call per query; big precision boost, +1-2s latency).
    use_llm_rerank: bool = True
    rerank_top_n: int = Field(6, ge=1, le=20)

    # --- UI -----------------------------------------------------------------
    default_language: str = "en"

    @field_validator("azure_openai_endpoint")
    @classmethod
    def _strip_trailing_slash(cls, v: str) -> str:
        return v.rstrip("/")

    @model_validator(mode="after")
    def _ensure_dirs(self) -> "Settings":
        self.data_dir = self.data_dir.expanduser().resolve()
        self.storage_dir = self.storage_dir.expanduser().resolve()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("CHUNK_OVERLAP must be smaller than CHUNK_SIZE")
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load and cache settings. Raises if required env vars are missing."""
    return Settings()  # type: ignore[call-arg]


def reset_settings_cache() -> None:
    get_settings.cache_clear()
