from pydantic_settings import BaseSettings, SettingsConfigDict


class BinanceSettings(BaseSettings):
    api_key: str
    api_secret: str

    model_config = SettingsConfigDict(env_file=(".env", ".env.local"), extra="allow")
