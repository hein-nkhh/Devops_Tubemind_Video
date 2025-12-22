import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # =========================
    # App
    # =========================
    APP_NAME = os.getenv("APP_NAME")
    APP_ENV = os.getenv("APP_ENV")

    # =========================
    # Whisper / Transcriber
    # =========================
    LANGUAGE = os.getenv("LANGUAGE")
    WHISPER_MODEL = os.getenv("WHISPER_MODEL")

    VIDEO_DIR = os.getenv("VIDEO_DIR")
    AUDIO_DIR = os.getenv("AUDIO_DIR")
    TRANSCRIPT_DIR = os.getenv("TRANSCRIPT_DIR")

    # =========================
    # Database
    # =========================
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    DATABASE_URL = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # =========================
    # Logging
    # =========================
    LOG_FILE = os.getenv("LOG_FILE", "logging.txt")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
