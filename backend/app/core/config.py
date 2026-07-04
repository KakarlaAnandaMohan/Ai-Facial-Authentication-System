import base64
try:
    from pydantic_settings import BaseSettings
    from pydantic import Field
except ImportError:
    try:
        from pydantic.v1 import BaseSettings, Field
    except ImportError:
        from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    APP_NAME: str = "AI-Based Facial Authentication System"
    DEBUG: bool = True
    DATABASE_URL: str = Field("sqlite+aiosqlite:///./test.db", env="DATABASE_URL")
    JWT_SECRET_KEY: str = Field("dev_super_secret_jwt_key_32bytes!!", env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    AES_KEY: str = Field("default_32byte_aes_secret_key_base64", env="AES_KEY")
    ENCRYPTION_KEY: str = Field("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=", env="ENCRYPTION_KEY")
    FACE_THRESHOLD: float = 0.6
    ADMIN_PASSWORD: str = Field("admin123", env="ADMIN_PASSWORD")
    REDIS_URL: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    AI_MODEL_PATH: str = Field("./models", env="AI_MODEL_PATH")
    FORCE_SYNTHETIC: bool = Field(True, env="FORCE_SYNTHETIC")

    @property
    def ENCRYPTION_KEY_BYTES(self) -> bytes:
        try:
            key = base64.b64decode(self.ENCRYPTION_KEY)
            if len(key) in (16, 24, 32):
                return key
        except Exception:
            pass
        # Fallback to a valid 32-byte key derived from AES_KEY or padded
        padded = (self.AES_KEY.encode("utf-8") + b"0"*32)[:32]
        return padded

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

