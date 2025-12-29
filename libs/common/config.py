import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    REDIS_HOST: str
    REDIS_PORT: int = 6379

    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET_NAME: str = "tubemind-videos"
    MINIO_SECURE: bool = False

    SMTP_HOST: str
    SMTP_PORT: int = 1025
    EMAIL_FROM: str = "noreply@tubemind.local"

    SMTP_USER: str = ""      # Mặc định rỗng để không lỗi nếu chạy local
    SMTP_PASSWORD: str = ""  # Mặc định rỗng
    
    GEMINI_API_KEY: str = ""
    WHISPER_MODEL_SIZE: str = "base"
    TEMP_DIR: str = "/tmp/tubemind"

    @property
    def DATABASE_URL(self):
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    model_config = SettingsConfigDict(
        env_file = ('.env', '.env.local'),
        env_ignore_empty=True,
        extra='ignore'
    )
    

settings = Settings()

# ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# ENV_FILE = os.path.join(ROOT_DIR, ".env.local")
# settings = Settings(_env_file=ENV_FILE)

# print(">>> DATABASE_URL FROM CONFIG =", settings.DATABASE_URL)