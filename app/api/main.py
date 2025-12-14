from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from datetime import datetime
from typing import Dict
from app.api.routes import router
from app.config import get_settings
from app.utils.logger import setup_logger, get_logger

setup_logger()
logger = get_logger(__name__)

app = FastAPI(
    title="Agente Regulatório - RAG Pix e Open Finance",
    description="Sistema RAG especializado em regulação do Banco Central do Brasil",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting simples (em memória)
rate_limit_store: Dict[str, list] = {}


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting básico"""
    settings = get_settings()
    client_ip = request.client.host if request.client else "unknown"
    
    now = time.time()
    if client_ip not in rate_limit_store:
        rate_limit_store[client_ip] = []
    
    # Limpar requisições antigas
    rate_limit_store[client_ip] = [
        t for t in rate_limit_store[client_ip]
        if now - t < 60
    ]
    
    # Verificar limite
    if len(rate_limit_store[client_ip]) >= settings.rate_limit_per_minute:
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded"}
        )
    
    # Registrar requisição
    rate_limit_store[client_ip].append(now)
    
    response = await call_next(request)
    return response


@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    """Timeout middleware"""
    settings = get_settings()
    start_time = time.time()
    
    try:
        response = await call_next(request)
        elapsed = time.time() - start_time
        
        if elapsed > settings.api_timeout:
            logger.warning("Request excedeu timeout", elapsed=elapsed, path=request.url.path)
        
        return response
    except Exception as e:
        logger.error("Erro no middleware", error=str(e), exc_info=True)
        raise


# Incluir rotas
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Inicialização da aplicação"""
    logger.info("Aplicação iniciada", timestamp=datetime.now().isoformat())


@app.on_event("shutdown")
async def shutdown_event():
    """Finalização da aplicação"""
    logger.info("Aplicação finalizada", timestamp=datetime.now().isoformat())

