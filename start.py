#!/usr/bin/env python3
"""
Startup script for Pennywise Backend
"""

import uvicorn

from app.config import settings

if __name__ == "__main__":
    print("🚀 Starting Pennywise Backend...")
    print(f"📱 App: {settings.app_name}")
    print(f"📦 Version: {settings.app_version}")
    print(f"🔧 Debug: {settings.debug}")
    print(f"🗄️  Database: {settings.mongodb_database}")
    print("=" * 50)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )
