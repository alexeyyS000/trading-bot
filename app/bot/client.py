from binance.client import Client

from .config import BinanceSettings


def get_client():
    return Client()
