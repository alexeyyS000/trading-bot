from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import DatabaseSettings

settings = DatabaseSettings()
session_factory = sessionmaker(bind=create_engine(settings.url), expire_on_commit=False)
