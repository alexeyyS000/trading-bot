from .config import BinanceSettings
from binance.client import Client


def get_client():
    return Client()
