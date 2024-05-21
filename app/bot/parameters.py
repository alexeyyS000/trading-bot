from pydantic_settings import BaseSettings, SettingsConfigDict


class StrategySettings(BaseSettings):
    master_symbol: str = "BTCUSDT"
    master_bar_limit: int = 1000
    slave_bar_limit: int = 15
    min_dayly_volume_dollar: int = 200000000
    klines_in_one_query: int = 500
    position_volume_in_usd: int = 10

    model_config = SettingsConfigDict(env_file=(".env", ".env.local"), extra="allow")
