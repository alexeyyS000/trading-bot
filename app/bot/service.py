import contextlib
import datetime
from typing import List, Optional

import numpy
import pandas
from binance.client import Client

from db.client import get_session
from db.dal.binance_futures import (HistoryCorrelationDAL, KlineDAL,
                                    PositionDAL, TickerDAL)


@contextlib.contextmanager
def get_future_service(binance_client: Client):
    with get_session() as session:
        ticker_dal = TickerDAL(session)  # передавать при вызове
        kline_dal = KlineDAL(session)
        history_correlation_dal = HistoryCorrelationDAL(session)
        position_dal = PositionDAL(session)
        yield FutureService(
            binance_client, ticker_dal, kline_dal, history_correlation_dal, position_dal
        )


class FutureService:
    def __init__(
        self,
        binance_client: Client,
        ticker_dal: TickerDAL,
        kline_dal: KlineDAL,
        history_correlation_dal: HistoryCorrelationDAL,
        position_dal: PositionDAL,
    ):
        self.binance_client = binance_client
        self.ticker_dal = ticker_dal
        self.kline_dal = kline_dal
        self.history_correlation_dal = history_correlation_dal
        self.position_dal = position_dal

    def save_klines(self, klines: List[list], symbol: str):
        for kline in klines:
            self.kline_dal.create_one(
                symbol=symbol,
                open=float(kline[1]),
                close=float(kline[4]),
                open_time=datetime.datetime.utcfromtimestamp(
                    int(kline[0]) / 1000
                ).strftime("%Y-%m-%d %H:%M:%S"),
                close_time=datetime.datetime.utcfromtimestamp(
                    int(kline[6]) / 1000
                ).strftime("%Y-%m-%d %H:%M:%S"),
                qouto_asset_vol=int(float(kline[7])),
            )

    def filter_actual_tickers(self):
        return self.history_correlation_dal.get_objects_by_slavesymbols(
            self.ticker_dal.select_active_symbols()
        )

    def get_position(self, symbol: str):
        return self.position_dal.filter(symbol=symbol)

    def get_symbol(self, **kwargs):
        return self.ticker_dal.get_one_or_none(**kwargs)

    def save_symbol(self, **kwargs):
        return self.ticker_dal.create_one(**kwargs)

    def get_or_create_pair(self, symbol: str, **kwargs):
        return self.ticker_dal.get_or_create(kwargs, symbol=symbol)

    def get_last_kline(self, symbol: str):
        return self.kline_dal.get_last_record(symbol=symbol)

    def update_pair(self, symbol: str, **kwargs):
        return self.ticker_dal.update_one(kwargs, symbol=symbol)

    def get_all_pairs(self):
        return self.ticker_dal.all()

    def recalculate_corellation(
        self, master_symbol: str, slave_symbol: str, bar_limit: int
    ):
        old_corr = self.history_correlation_dal.get_one_or_none(
            master_symbol=master_symbol, slave_symbol=slave_symbol
        )
        new_correlation = self.kline_dal.get_corellation(
            master_symbol, slave_symbol, bar_limit
        )
        if not old_corr:
            self.history_correlation_dal.create_one(
                master_symbol=master_symbol,
                slave_symbol=slave_symbol,
                corellation_coef=new_correlation,
            )
        else:
            self.history_correlation_dal.update_one(
                {"corellation_coef": new_correlation},
                master_symbol=master_symbol,
                slave_symbol=slave_symbol,
            )

    def get_all_usdt_futures_tickers(self):
        exchange_info = self.binance_client.futures_exchange_info()

        for symbol in exchange_info["symbols"]:
            if "USDT" in symbol["symbol"]:
                yield symbol["symbol"]

    def delete_tickers(self, **kwargs):
        return self.ticker_dal.delete_several(**kwargs)

    def get_dataframe(self, klines: List[list]):
        df = pandas.DataFrame(
            klines,
            columns=[
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "close_time",
                "qouto_asset_vol",
                "number_of_trades",
                "base-vol",
                "asset_vol",
                "ignored",
            ],
        )
        return df

    def select_liquid_pairs(self, minimum_volume: int):
        for symbol in self.get_all_usdt_futures_tickers():
            klines = self.get_klines(
                symbol=symbol,
                interval=self.binance_client.KLINE_INTERVAL_1HOUR,
                limit=24,
            )  # обработать ошибку
            dayly_asset_volume = 0.0
            for i in klines:
                dayly_asset_volume += float(i[7])
            dayly_asset_volume = int(dayly_asset_volume)
            if dayly_asset_volume > minimum_volume:
                yield (symbol, dayly_asset_volume)

    def get_klines(self, symbol: str, interval: Optional[str] = "1m", **kwargs):
        return self.binance_client.futures_klines(
            symbol=symbol, interval=interval, **kwargs
        )

    def calculate_short_term_correlation(
        self, master_closes_prices: list, slave_closes_prices: list
    ):
        return numpy.corrcoef(master_closes_prices, slave_closes_prices)[0, 1]

    def order_future(
        self, symbol: str, quantity: int, side: str, leverage: Optional[int] = 1
    ):
        order = self.binance_client.futures_create_order(
            symbol=symbol,
            side=side,
            type="MARKET",
            quantity=quantity,
            leverage=leverage,
        )
        return order

    def get_market_price(self, symbol: str):
        ticker = self.binance_client.get_symbol_ticker(symbol=symbol)
        return float(ticker["price"])

    def convert_dollar_to_quantity(self, usdt_amount: int, ticker_price: int):
        return usdt_amount / ticker_price

    def calculate_side(self, klines):
        if float(klines[0][4]) - float(klines[-1][4]) < 0:
            return "SELL"
        else:
            return "BUY"
