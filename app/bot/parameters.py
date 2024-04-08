from pydantic_settings import BaseSettings, SettingsConfigDict


class StrategySettings(BaseSettings):
    master_symbol: str = "BTCUSDT"
    master_bar_limit: int = 9000
    slave_bar_limit: int = 15
    min_dayly_volume_dollar: int = 1000000000
    klines_in_one_query: int = 500
    position_volume_in_usd: int = 10
    leverage: int = 1

    model_config = SettingsConfigDict(env_file=(".env", ".env.local"), extra="allow")
