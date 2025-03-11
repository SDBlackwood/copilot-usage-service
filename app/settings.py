from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    billing_period_endpoint: str

    model_config = SettingsConfigDict(env_file=".env")
