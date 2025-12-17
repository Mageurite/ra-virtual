"""
LLM Service Configuration
Centralized configuration management for LLM service
"""
import os
from typing import Optional


class LLMConfig:
    """LLM Service Configuration"""
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "300"))
    
    # Default Models
    DEFAULT_MODEL: str = os.getenv("LLM_DEFAULT_MODEL", "mistral-nemo:12b-instruct-2407-fp16")
    FALLBACK_MODEL: str = os.getenv("LLM_FALLBACK_MODEL", "llama3.1:8b-instruct-q4_K_M")
    
    # LLM Parameters
    TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.4"))
    MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "2048"))
    
    # RAG Configuration (optional - if not using RAG, set to None)
    RAG_ENABLED: bool = os.getenv("RAG_ENABLED", "false").lower() == "true"
    RAG_SERVICE_URL: str = os.getenv("RAG_SERVICE_URL", "http://localhost:8602")
    RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "5"))
    
    # Tavily Search (optional)
    TAVILY_ENABLED: bool = os.getenv("TAVILY_ENABLED", "false").lower() == "true"
    TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY")
    
    # Conversation History
    MAX_HISTORY_TURNS: int = int(os.getenv("MAX_HISTORY_TURNS", "5"))
    
    # Guardrail Settings
    GUARDRAIL_ENABLED: bool = os.getenv("GUARDRAIL_ENABLED", "true").lower() == "true"
    
    # Streaming
    ENABLE_STREAMING: bool = os.getenv("ENABLE_STREAMING", "true").lower() == "true"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        try:
            import httpx
            response = httpx.get(f"{cls.OLLAMA_BASE_URL}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Ollama validation failed: {e}")
            return False
    
    @classmethod
    def get_available_models(cls) -> list:
        """Get list of available models from Ollama"""
        try:
            import httpx
            response = httpx.get(f"{cls.OLLAMA_BASE_URL}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
            return [cls.DEFAULT_MODEL, cls.FALLBACK_MODEL]
        except Exception as e:
            print(f"Failed to get models: {e}")
            return False
    
    @classmethod
    def get_available_models(cls) -> list[str]:
        """Get list of available models from Ollama"""
        try:
            import httpx
            response = httpx.get(f"{cls.OLLAMA_BASE_URL}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [m["name"] for m in models]
            return []
        except Exception:
            return []


# Global config instance
config = LLMConfig()
