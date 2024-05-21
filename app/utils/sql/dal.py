from typing import List

from sqlalchemy import select, update


class SqlAlchemyRepository:
    class Config:
        model = None

    def __init__(self, session_factory):
        self.session_factory = session_factory
        self._base_query = select(self.Config.model)

    def get_one_or_none(self, **kwargs):
        with self.session_factory() as session:
            stmt = select(self.Config.model).filter_by(**kwargs)
            result = session.execute(stmt)
            return result.scalar_one_or_none()

    def create_one(self, **kwargs):
        with self.session_factory() as session:
            instance = self.Config.model(**kwargs)
            session.add(instance)
            session.commit()
            return instance

    def create_some(self, elements: List[dict]):
        with self.session_factory() as session:
            objects = [self.Config.model(**element) for element in elements]
            session.bulk_save_objects(objects)
            session.commit()
            return objects

    def get_or_create(self, default: dict, **kwargs):
        instance = self.get_one_or_none(**kwargs)
        if instance is None:
            return (self.create_one(**(kwargs | default)), True)
        else:
            return (instance, False)

    def update_one(self, attrs: dict, **kwargs):
        with self.session_factory() as session:
            stmt = (
                update(self.Config.model)
                .filter_by(**kwargs)
                .values(**attrs)
                .returning(self.Config.model)
            )
            result = session.execute(stmt)
            session.commit()
            return result.scalar_one_or_none()

    def delete_one(self, **kwargs):
        with self.session_factory() as session:
            instance = self.get_one_or_none(**kwargs)
            if instance is None:
                return None
            session.delete(instance)
            session.commit()
            return instance

    def delete_several(self, **kwargs):
        with self.session_factory() as session:
            instance = self.filter(**kwargs)
            if instance is None:
                return None
            session.delete(instance)
            session.commit()
            return instance

    def filter(self, **kwargs):
        self._base_query = self._base_query.filter_by(**kwargs)
        return self

    def order_by(self, *args):
        self._base_query = self._base_query.order_by(*args)
        return self

    def join(self, *args):
        self._base_query = self._base_query.join(*args)
        return self

    def first(self):
        with self.session_factory() as session:
            result = session.execute(self._base_query)
            return result.scalar_one_or_none()

    def all(self):
        with self.session_factory() as session:
            result = session.execute(self._base_query)
            return result.scalars().all()

    def base(self, query):
        self._base_query = query
        return self

    def query(self):
        return self._base_query

    def delete_all(self):
        with self.session_factory() as session:
            session.query(self.Config.model).delete()
            session.commit()
