from sqlalchemy import func, select
from db.models.future import Future, Kline
from utils.sql.dal import SqlAlchemyRepository


class FutureDAL(SqlAlchemyRepository):
    class Config:
        model = Future


class KlineDAL(SqlAlchemyRepository):
    class Config:
        model = Kline

    def get_corellation(self, master_symbol_id, slave_symbol_id):
        subquery1 = (
            self.session_factory.query(  # переписать на новый синтаксис
                self.Config.model.close,
                func.row_number()
                .over(order_by=self.Config.model.id)
                .label("row_number"),
            )
            .filter(self.Config.model.symbol == master_symbol_id)
            .subquery()
        )

        subquery2 = (
            self.session_factory.query(  
                self.Config.model.close,
                func.row_number()
                .over(order_by=self.Config.model.id)
                .label("row_number"),
            )
            .filter(self.Config.model.symbol == slave_symbol_id)
            .subquery()
        )

        correlation = (
            self.session_factory.query(
                func.corr(subquery1.c.close, subquery2.c.close).label("correlation")
            )
            .select_from(
                subquery1.join(
                    subquery2, subquery1.c.row_number == subquery2.c.row_number
                )
            )
            .one()
        )

        return correlation.correlation

    def get_last_record(self, **kwargs):
        # self.session_factory.query(self.Config.model).order_by(self.Config.model.id.desc()).first() # может так лучше?
        stmt = (
            select(self.Config.model)
            .filter_by(**kwargs)
            .order_by(self.Config.model.open_time.desc())
            .limit(1)
        )  # можно ли добавить first сюда чтобы не выгружать весть список в сразу выгрузить первый
        result = self.session_factory.execute(stmt)
        result = result.scalar_one_or_none()
        return result
