from .dbconnect import Base
from sqlalchemy import Column, Integer, String

SHORT_STR = 20

LONG_STR = 100

DESCRIPTION = 1000

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String(LONG_STR), unique=True, nullable=False)
    password = Column(String(LONG_STR), unique=True, nullable=False)
