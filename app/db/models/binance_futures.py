from datetime import datetime
from sqlalchemy import ForeignKey, String
from db.base import Base
from sqlalchemy import Column, String, Integer, Float, DateTime, BigInteger


class Future(Base):
    __tablename__ = "futures"
    symbol = Column(String, primary_key=True)
    daily_volume = Column(BigInteger, nullable=True)#daily
    history_correlation = Column(Float, nullable=True)
    current_correlation = Column(Float, nullable=True)
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, onupdate=datetime.utcnow)


class Kline(Base):
    __tablename__ = "klines"
    id = Column(Integer, primary_key=True)
    symbol = Column(String, ForeignKey(Future.symbol))
    open = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    open_time = Column(DateTime, nullable=False)
    close_time = Column(DateTime, nullable=False)
    qouto_asset_vol = Column(Integer, nullable=False)
    created = Column(DateTime, default=datetime.utcnow)


class HistoryCorrelation(Base):
    __tablename__ = "correlations"
    id = Column(Integer, primary_key=True)
    master_symbol = Column(String, ForeignKey(Future.symbol))
    slave_symbol = Column(String, ForeignKey(Future.symbol))
    corellation_coef = Column(Float, nullable=False)
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, onupdate=datetime.utcnow)


class Position(Base):
    __tablename__ = "positions"
    id = Column(Integer, primary_key=True)
    instrument = Column(String, ForeignKey(Future.symbol))
    last_short_term_corellations = Column(Integer)
    position_additions_number = Column(Integer, nullable=False)
    current_trade_volume = Column(Float, nullable=False)
    created = Column(DateTime, default=datetime.utcnow)
