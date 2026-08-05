from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "my-fastapi-base"
    database_url: str
    secret_key: str = "dev-secret-key"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()