from binance.client import Client

from .config import BinanceSettings

settings = BinanceSettings()


def get_client():
    return Client(settings.api_key, settings.api_secret)
