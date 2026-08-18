import os

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "my-fastapi-base"
    database_url: str
    secret_key: str = Field(default="")
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    email_otp_length: int = 6
    email_otp_expire_minutes: int = 10
    email_otp_resend_cooldown_seconds: int = 60
    email_otp_daily_send_limit: int = 5
    email_otp_max_attempts: int = 5
    smtp_host: str
    smtp_port: int = 587
    smtp_username: str
    smtp_password: str
    smtp_from: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        if not value:
            env_name = os.getenv("APP_ENV", "development").lower()
            if env_name in {"prod", "production"}:
                raise ValueError("SECRET_KEY must be set in production")
            return "dev-secret-key-change-me"

        placeholder_values = {"change-me-in-production", "changeme", "secret", "dev-secret-key"}
        env_name = os.getenv("APP_ENV", "development").lower()
        if env_name in {"prod", "production"}:
            if len(value) < 32 or value.lower() in placeholder_values:
                raise ValueError("SECRET_KEY must be a strong random value in production")
        return value


settings = Settings()