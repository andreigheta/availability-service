from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "availability-service"
    app_host: str = "0.0.0.0"
    app_port: int = 8200
    database_service_url: str = "http://localhost:8000"
    request_timeout_seconds: float = 10.0
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3001"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)


settings = Settings()
