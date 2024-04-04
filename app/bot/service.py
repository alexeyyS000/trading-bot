from typing import List, Optional
from binance.client import Client
import pandas
from db.dal.future import FutureDAL, KlineDAL, HistoryCorrelationDAL, PositionDAL
import numpy
import datetime
import contextlib
from db.client import get_session


@contextlib.contextmanager
def get_user_service(binance_client):
    with get_session() as session:
        future_dal = FutureDAL(session)#передавать при вызове
        kline_dal = KlineDAL(session)
        history_correlation_dal = HistoryCorrelationDAL(session)
        position_dal = PositionDAL(session)
        yield FutureService(binance_client, future_dal, kline_dal, history_correlation_dal, position_dal)


class FutureService:
    def __init__(
        self,
        binance_client: Client,
        future_dal: FutureDAL,
        kline_dal: KlineDAL,
        history_correlation_dal: HistoryCorrelationDAL,
        position_dal: PositionDAL
    ):
        self.binance_client = binance_client
        self.future_dal = future_dal
        self.kline_dal = kline_dal
        self.history_correlation_dal = history_correlation_dal,
        self.position_dal = position_dal

    def save_klines(self, klines, symbol: str):
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

    def get_symbol(self, **kwargs):
        self.future_dal.get_one_or_none(**kwargs)

    def save_symbol(self, **kwargs):
        self.future_dal.create_one(**kwargs)

    def get_or_create_pair(self, symbol, **kwargs):
        return self.future_dal.get_or_create(kwargs, symbol = symbol)

    def get_last_kline(self, symbol: str):
        return self.kline_dal.get_last_record(symbol=symbol)


    def update_pair(self, symbol, **kwargs):
        return self.future_dal.update_one(kwargs, symbol = symbol)
    
    def get_all_pairs(self):
        return self.future_dal.all()

    def save_corellation(self, master_symbol, slave_symbol):
        old_corr = self.history_correlation_dal.get_one_or_none(master_symbol = master_symbol, slave_symbol = slave_symbol) #(self.kline_dal.get_corellation(master_symbol, slave_symbol))
        if not old_corr:
            new_correlation = self.kline_dal.get_corellation(master_symbol, slave_symbol)
            self.history_correlation_dal.create_one(master_symbol = master_symbol, slave_symbol = slave_symbol, corellation_coef = new_correlation)
        else:
            self.history_correlation_dal.update_one({'corellation_coef':new_correlation}, master_symbol = master_symbol, slave_symbol = slave_symbol)
    def get_all_usdt_futures_tickers(self):
        exchange_info = self.binance_client.futures_exchange_info()

        for symbol in exchange_info["symbols"]:
            if "USDT" in symbol["symbol"]:
                yield symbol["symbol"]

    def get_corrcoef(self, master_symbol_id, slave_symbol_id):
        self.kline_dal.get_corellation(master_symbol_id, slave_symbol_id)

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
        df["close"] = df["close"].astype(float)
        df["qouto_asset_vol"] = df["qouto_asset_vol"].astype(float).astype(int)
        df["volume"] = df["volume"].astype(float).astype(int)
        return df

    def select_liquid_pairs(self, minimum_volume: int):
        for symbol in self.get_all_usdt_futures_tickers():
            klines = self.get_klines(symbol=symbol, interval=self.binance_client.KLINE_INTERVAL_1HOUR, limit = 24)  # обработать ошибку
            dayly_asset_volume = 0.0
            for i in klines:
                dayly_asset_volume += float(i[7])
            dayly_asset_volume = int(dayly_asset_volume)
            if dayly_asset_volume > minimum_volume:
                yield (symbol, dayly_asset_volume)

    def get_klines(
        self,
        symbol: str,
        interval = '1m',
        **kwargs
    ):
        return self.binance_client.futures_klines(
            symbol=symbol,
            interval=interval,
            **kwargs
        )

    def get_closes_time(self, klines: List[list]):
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
        return df["close"].astype(float)

    def calculate_correlation(self, klines: list):
        return numpy.corrcoef(self.master_symbol_closes, self.get_closes_time(klines))[
            0, 1
        ]


# with get_session() as session:
#     print(KlineDAL(session).get_corellation())


# x = numpy.corrcoef([69000, 61000, 59000], [12, 35, 22])[0,1]

# print(x)

# with get_session() as session:
#     #print(KlineDAL(session).create_one(symbol = 1, timestamp = '5m', open = 3213, close = 3424, qouto_asset_vol = 2, close_time = datetime.datetime(2022, 12, 28, 23, 58, 59, 342380)))
#     g= KlineDAL(session).get_last_record(1)
#     print(g.id)
