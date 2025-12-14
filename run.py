#!/usr/bin/env python3
"""
Script principal para executar a aplicação.
"""
import os
import uvicorn
from app.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.app_env == "development"
    )

