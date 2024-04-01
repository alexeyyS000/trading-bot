from datetime import date, datetime
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, String, JSON
from db.base import Base
from sqlalchemy.dialects.postgresql import ARRAY
from typing import List
from sqlalchemy import Column, String, Integer, Float, DateTime


class Future(Base):
    __tablename__ = "futures"
    id = Column(Integer, primary_key=True)
    symbol = Column(String(9), nullable=False)# сделать его primary 
    dayly_volume = Column(Integer, nullable=True)
    history_correlation = Column(Float, nullable=True)
    current_correlation = Column(Float, nullable=True)
    created = Column(DateTime, default=date.today)
    updated = Column(DateTime, onupdate=date.today)


class Kline(Base):
    __tablename__ = "klines"
    id = Column(Integer, primary_key=True)
    symbol = Column(Integer, ForeignKey(Future.id))
    open = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    open_time = Column(DateTime, nullable=False)
    close_time = Column(DateTime, nullable=False)
    qouto_asset_vol = Column(Integer, nullable=False)
    created = Column(DateTime, default=datetime.utcnow)


class Corellation(Base):
    __tablename__ = "corellations"
    id = Column(Integer, primary_key=True)
    master_symbol = Column(Integer, ForeignKey(Future.id))
    slave_symbol = Column(Integer, ForeignKey(Future.id))
    created = Column(DateTime, default=datetime.utcnow)
