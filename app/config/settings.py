from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str = ""  # Será validado quando necessário
    
    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: str = ""  # Opcional, para Qdrant Cloud
    
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
        # Qdrant Cloud requer HTTPS e NÃO usa porta na URL
        # Se o host contém "cloud.qdrant.io" ou "gcp.cloud.qdrant.io", usar HTTPS sem porta
        if "cloud.qdrant.io" in self.qdrant_host or "gcp.cloud.qdrant.io" in self.qdrant_host:
            # Se já tem protocolo, remover porta se houver
            if self.qdrant_host.startswith(("http://", "https://")):
                url = self.qdrant_host
            else:
                url = f"https://{self.qdrant_host}"
            # Remover porta da URL (Qdrant Cloud não usa porta na URL)
            url = url.replace(":6333", "").replace(":6334", "")
            return url
        
        # Para Qdrant local, usar HTTP com porta
        if self.qdrant_host.startswith(("http://", "https://")):
            return f"{self.qdrant_host}:{self.qdrant_port}"
        return f"http://{self.qdrant_host}:{self.qdrant_port}"

