from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    billing_period_endpoint: str
    report_endpoint: str
    base_cost_per_message: Field(default=1)

    model_config = SettingsConfigDict(env_file=".env")
