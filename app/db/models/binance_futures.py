from datetime import datetime, timedelta

from sqlalchemy import (BigInteger, Column, DateTime, Float, ForeignKey,
                        Integer, String, case, func)
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.functions import concat

from db.base import Base


class Ticker(Base):
    __tablename__ = "tickers"
    symbol = Column(String, primary_key=True)
    daily_volume = Column(BigInteger, nullable=True)
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, onupdate=datetime.utcnow)

    @hybrid_property
    def is_actual(self):
        now = datetime.utcnow()
        if self.updated:
            return self.updated > now - timedelta(hours=24)
        else:
            return self.created > now - timedelta(hours=24)

    @is_actual.inplace.expression
    @classmethod
    def _is_actual_expression(cls):
        return case(
            (
                func.age(func.now(), func.coalesce(cls.updated, cls.created))
                < func.cast(concat(24, " HOURS"), INTERVAL),
                True,
            ),
            else_=False,
        )


class Kline(Base):
    __tablename__ = "klines"
    id = Column(Integer, primary_key=True)
    symbol = Column(String, ForeignKey(Ticker.symbol))
    open = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    open_time = Column(DateTime, nullable=False)
    close_time = Column(DateTime, nullable=False)
    qouto_asset_vol = Column(Integer, nullable=False)
    created = Column(DateTime, default=datetime.utcnow)


class HistoryCorrelation(Base):
    __tablename__ = "correlations"
    id = Column(Integer, primary_key=True)
    master_symbol = Column(String, ForeignKey(Ticker.symbol))
    slave_symbol = Column(String, ForeignKey(Ticker.symbol))
    corellation_coef = Column(Float, nullable=False)
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, onupdate=datetime.utcnow)


class Position(Base):
    __tablename__ = "positions"
    id = Column(Integer, primary_key=True)
    instrument = Column(String, ForeignKey(Ticker.symbol))
    last_short_term_corellation = Column(Integer)
    current_trade_volume = Column(Float, nullable=False)
    created = Column(DateTime, default=datetime.utcnow)
