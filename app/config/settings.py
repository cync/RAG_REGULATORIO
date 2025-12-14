from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str
    
    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    
    # Aplicação
    app_env: str = "production"
    log_level: str = "INFO"
    api_timeout: int = 30
    rate_limit_per_minute: int = 60
    
    # RAG Config
    top_k_results: int = 5
    min_similarity_score: float = 0.7
    max_tokens_response: int = 1000
    embedding_model: str = "text-embedding-3-large"
    llm_model: str = "gpt-4o-mini"  # GPT-4.1-mini não existe, usando gpt-4o-mini
    
    # Domínios
    domains: str = "pix,open_finance"
    
    # Paths
    data_raw_path: str = "data/raw"
    data_processed_path: str = "data/processed"
    logs_path: str = "logs"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def domain_list(self) -> List[str]:
        return [d.strip() for d in self.domains.split(",")]
    
    @property
    def qdrant_url(self) -> str:
        return f"http://{self.qdrant_host}:{self.qdrant_port}"

