import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Firebase Configuration
    firebase_project_id: str = ""
    firebase_private_key_id: str = ""
    firebase_private_key: str = ""
    firebase_client_email: str = ""
    firebase_client_id: str = ""
    firebase_auth_uri: str = "https://accounts.google.com/o/oauth2/auth"
    firebase_token_uri: str = "https://oauth2.googleapis.com/token"
    firebase_auth_provider_x509_cert_url: str = "https://www.googleapis.com/oauth2/v1/certs"
    firebase_client_x509_cert_url: str = ""
    
    # MongoDB Configuration
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "pennywise"
    
    # Gemini API Configuration
    gemini_api_key: Optional[str] = None
    
    # Application Configuration
    app_name: str = "Pennywise Backend"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Security
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()

# Firebase credentials dictionary
FIREBASE_CREDENTIALS = {
    "type": "service_account",
    "project_id": settings.firebase_project_id,
    "private_key_id": settings.firebase_private_key_id,
    "private_key": settings.firebase_private_key.replace("\\n", "\n") if settings.firebase_private_key else "",
    "client_email": settings.firebase_client_email,
    "client_id": settings.firebase_client_id,
    "auth_uri": settings.firebase_auth_uri,
    "token_uri": settings.firebase_token_uri,
    "auth_provider_x509_cert_url": settings.firebase_auth_provider_x509_cert_url,
    "client_x509_cert_url": settings.firebase_client_x509_cert_url
}
