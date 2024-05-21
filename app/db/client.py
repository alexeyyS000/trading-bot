from sqlalchemy import create_engine

from .config import DatabaseSettings

from sqlalchemy.orm import sessionmaker


settings = DatabaseSettings()
session_factory = sessionmaker(bind=create_engine(settings.url), expire_on_commit=False)
