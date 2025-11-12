from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str
    ADMIN_NAME: str
    ADMIN_PASSWORD: str
    ADMIN_ROLE: str

    model_config = SettingsConfigDict(
        env_file="./.env",
        env_file_encoding="utf-8"
    )

settings = Settings()
