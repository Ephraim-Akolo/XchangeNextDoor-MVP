from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .settings import settings

engine = create_engine(f"mysql+pymysql://{settings.xchangenextdoor_db_user}:{settings.xchangenextdoor_db_password}@{settings.xchangenextdoor_db_server}/{settings.xchangenextdoor_db_name}")

Session = sessionmaker(bind=engine, autoflush=False)

Base = declarative_base()


def get_session():
    local_session = Session()
    try:
        yield local_session
    finally:
        local_session.close()
