#!/usr/bin/env python3
"""
Script principal para executar a aplicação.
"""
import uvicorn
from app.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.app_env == "development"
    )

