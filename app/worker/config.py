from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkerSettings(BaseSettings):
    celery_broker_url: str
    celery_result_backend: str

    model_config = SettingsConfigDict(
        env_prefix="db_", env_file=(".env", ".env.local"), extra="allow"
    )
