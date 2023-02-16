from .dbconnect import Base
from sqlalchemy import Column, Integer, String, Float, Boolean

SHORT_STR = 20

LONG_STR = 100

LONGER_STR = 250

DESCRIPTION = 1000


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String(LONG_STR), unique=True, nullable=False)
    password = Column(String(LONG_STR), nullable=False)
    public_key = Column(String(LONG_STR), nullable= False, unique=True)
    private_key = Column(String(LONGER_STR), nullable= False)
    balance = Column(Float, nullable=False, default=0)


class Fundings(Base):
    __tablename__ = 'fundings'
    id = Column(Integer, primary_key=True, nullable=False)
    from_address = Column(String(LONG_STR), nullable= False, unique=False)
    to_address = Column(String(LONG_STR), nullable= False, unique=False)
    success = Column(Boolean, default=False)


class Utility(Base):
    __tablename__ = "utility"
    id = Column(Integer, primary_key=True, nullable=False)
    key = Column(String(LONG_STR), nullable= False, unique=True)
    value = Column(String(LONGER_STR), nullable= False, unique=True)
