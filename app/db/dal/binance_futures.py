import pandas as pd
from sqlalchemy import func, select

from db.models import HistoryCorrelation, Kline, Position, Ticker
from utils.sql.dal import SqlAlchemyRepository


class TickerDAL(SqlAlchemyRepository):
    class Config:
        model = Ticker

    def select_active_symbols(self):
        return [i.symbol for i in self.filter(is_actual=True).all()]


class KlineDAL(SqlAlchemyRepository):
    class Config:
        model = Kline

    def get_dataframe(self, symbol):
        with self.session_factory() as session:
            return pd.read_sql(
                select(self.Config.model).filter(self.Config.model.symbol == symbol),
                session.bind,
            )

    def get_corellation(self, master_symbol: str, slave_symbol: str, limit: int):
        subquery1 = (
            select(
                self.Config.model.close,
                func.row_number()
                .over(order_by=self.Config.model.id)
                .label("row_number"),
            )
            .filter(self.Config.model.symbol == master_symbol)
            .limit(limit)
            .subquery()
        )

        subquery2 = (
            select(
                self.Config.model.close,
                func.row_number()
                .over(order_by=self.Config.model.id)
                .label("row_number"),
            )
            .filter(self.Config.model.symbol == slave_symbol)
            .limit(limit)
            .subquery()
        )

        correlation = select(
            func.corr(subquery1.c.close, subquery2.c.close).label("correlation")
        ).select_from(
            subquery1.join(subquery2, subquery1.c.row_number == subquery2.c.row_number)
        )
        with self.session_factory() as session:
            result = session.execute(correlation)
            correlation_value = result.scalar_one_or_none()
            return correlation_value

    def get_last_record(self, **kwargs):
        stmt = (
            select(self.Config.model)
            .filter_by(**kwargs)
            .order_by(self.Config.model.open_time.desc())
            .limit(1)
        )
        with self.session_factory() as session:
            result = session.execute(stmt)
            result = result.scalar_one_or_none()
            return result


class HistoryCorrelationDAL(SqlAlchemyRepository):
    class Config:
        model = HistoryCorrelation

    def get_objects_by_slavesymbols(self, symbols: list):
        stmt = select(self.Config.model).filter(
            self.Config.model.slave_symbol.in_(symbols)
        )
        with self.session_factory() as session:
            result = session.execute(stmt)
            return result.all()


class PositionDAL(SqlAlchemyRepository):
    class Config:
        model = Position
