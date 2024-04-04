from sqlalchemy import func, select
from db.models.binance_futures import Future, Kline, HistoryCorrelation, Position
from utils.sql.dal import SqlAlchemyRepository


class FutureDAL(SqlAlchemyRepository):
    class Config:
        model = Future


class KlineDAL(SqlAlchemyRepository):
    class Config:
        model = Kline

    def get_corellation(self, master_symbol_id, slave_symbol_id):
        subquery1 = (
            select(
                self.Config.model.close,
                func.row_number()
                .over(order_by=self.Config.model.id)
                .label("row_number"),
            )
            .filter(self.Config.model.symbol == master_symbol_id)
            .subquery()
        )

        subquery2 = (
            select(  
                self.Config.model.close,
                func.row_number()
                .over(order_by=self.Config.model.id)
                .label("row_number"),
            )
            .filter(self.Config.model.symbol == slave_symbol_id)
            .subquery()
        )

        correlation = (
            select(
                func.corr(subquery1.c.close, subquery2.c.close).label("correlation")
            )
            .select_from(
                subquery1.join(
                    subquery2, subquery1.c.row_number == subquery2.c.row_number
                )
            )
        )

        result = self.session_factory.execute(correlation)
        correlation_value = result.scalar_one_or_none()

        return correlation_value

    def get_last_record(self, **kwargs):
        stmt = (
            select(self.Config.model)
            .filter_by(**kwargs)
            .order_by(self.Config.model.open_time.desc())
            .limit(1)
        )
        result = self.session_factory.execute(stmt)
        result = result.scalar_one_or_none()
        return result


class HistoryCorrelationDAL(SqlAlchemyRepository):
    class Config:
        model = HistoryCorrelation


class PositionDAL(SqlAlchemyRepository):
    class Config:
        model = Position