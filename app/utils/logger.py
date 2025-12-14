import structlog
import logging
import sys
from pathlib import Path
from datetime import datetime
from app.config import get_settings


def setup_logger():
    """Configura logger estruturado para auditoria"""
    try:
        settings = get_settings()
        log_level = settings.log_level
    except Exception:
        # Se não conseguir carregar settings, usa padrão
        log_level = "INFO"
    
    # Criar diretório de logs
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configurar structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configurar logging padrão
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper(), logging.INFO),
    )
    
    # File handler para auditoria
    file_handler = logging.FileHandler(
        log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    )
    file_handler.setFormatter(logging.Formatter("%(message)s"))
    
    logger = logging.getLogger()
    logger.addHandler(file_handler)


def get_logger(name: str = None):
    """Retorna logger configurado"""
    return structlog.get_logger(name)

