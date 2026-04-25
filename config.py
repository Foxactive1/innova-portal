from __future__ import annotations

import os
import warnings
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv
load_dotenv('.env')  # ← ADICIONE ESTA LINHA

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"


class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # ← ADICIONE
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")  # ← ADICIONE
    SECRET_KEY = (
        os.getenv("FLASK_SECRET_KEY")
        or os.getenv("SECRET_KEY")
        or "dev-only-insecure-key-change-me"
    )

    if SECRET_KEY == "dev-only-insecure-key-change-me":
        warnings.warn(
            "[InNovaIdeia] SECRET_KEY nao configurada. Defina FLASK_SECRET_KEY "
            "antes de publicar em producao.",
            RuntimeWarning,
        )

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or (
        f"sqlite:///{INSTANCE_DIR / 'database.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_SECURE = False
    PERMANENT_SESSION_LIFETIME = timedelta(
        hours=int(os.getenv("SESSION_DURATION_HOURS", "8"))
    )

    WTF_CSRF_TIME_LIMIT = int(os.getenv("CSRF_TIME_LIMIT_SECONDS", "3600"))
    RATELIMIT_HEADERS_ENABLED = True

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    MAX_CONTACT_MESSAGE_LENGTH = int(os.getenv("MAX_CONTACT_MESSAGE_LENGTH", "1000"))
    MAX_CHAT_MESSAGE_LENGTH = int(os.getenv("MAX_CHAT_MESSAGE_LENGTH", "500"))
    MAX_TITLE_LENGTH = int(os.getenv("MAX_TITLE_LENGTH", "100"))
    MAX_DESCRIPTION_LENGTH = int(os.getenv("MAX_DESCRIPTION_LENGTH", "500"))
    MAX_NAME_LENGTH = int(os.getenv("MAX_NAME_LENGTH", "100"))
    MAX_SUMMARY_LEADS = int(os.getenv("MAX_SUMMARY_LEADS", "25"))

    LOGIN_RATE_LIMIT = os.getenv("LOGIN_RATE_LIMIT", "5 per minute")
    REGISTER_RATE_LIMIT = os.getenv("REGISTER_RATE_LIMIT", "3 per minute")
    CONTACT_RATE_LIMIT = os.getenv("CONTACT_RATE_LIMIT", "5 per minute")
    CHAT_RATE_LIMIT = os.getenv("CHAT_RATE_LIMIT", "15 per minute")
    AI_RATE_LIMIT = os.getenv("AI_RATE_LIMIT", "10 per minute")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = "https"


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config():
    env = os.getenv("FLASK_ENV", "development")
    return config_map.get(env, DevelopmentConfig)
