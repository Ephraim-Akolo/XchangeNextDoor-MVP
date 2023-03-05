from .dbconnect import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Float, Boolean, TIMESTAMP, text

SHORT_STR = 20

LONG_STR = 100

LONGER_STR = 250

DESCRIPTION = 1000


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String(LONG_STR), unique=True, nullable=False)
    password = Column(String(LONG_STR), nullable=False)
    public_key = Column(String(LONG_STR), nullable= True, unique=True)
    balance = Column(Float, nullable=False, default=0)
    created = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))


class Vendors(Base):
    __tablename__ = "vendors"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String(LONG_STR), unique=True, nullable=False)
    password = Column(String(LONG_STR), nullable=False)
    balance = Column(Float, nullable=False, default=0)
    created = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))


class VendorsTransfers(Base): # should have transaction id to be able to cluster batch transactions.
    __tablename__ = 'vendors_transfers'
    id = Column(Integer, primary_key=True, nullable=False)
    from_address = Column(String(LONG_STR), nullable= False, unique=False)
    to_address = Column(String(LONG_STR), nullable= False, unique=False)
    amount = Column(Float, nullable=False)
    status = Column(String(SHORT_STR), nullable=False)
    fee = Column(Float, nullable=False)
    created = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))


class UsersTransfers(Base): 
    # make from_address foriegn key and you will not be able to transfer for wallets outside the 
    # platform because it does not exist in the platform
    __tablename__ = 'users_transfers'
    id = Column(Integer, primary_key=True, nullable=False)
    from_address = Column(String(LONG_STR), nullable= False, unique=False)
    to_address = Column(String(LONG_STR), nullable= False, unique=False)
    amount = Column(Float, nullable=False)
    status = Column(String(SHORT_STR), nullable=False)
    fee = Column(Float, nullable=False)
    created = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))


class Fundings(Base): # make from_address foriegn key
    __tablename__ = 'fundings'
    id = Column(Integer, primary_key=True, nullable=False)
    from_address = Column(String(LONG_STR), nullable= False, unique=False)
    to_address = Column(String(LONG_STR), nullable= False, unique=False)
    amount = Column(Float, nullable=False)
    block_number = Column(Integer, nullable=False)
    status = Column(String(SHORT_STR), nullable=False)
    timestamp = Column(TIMESTAMP)


class Escrow(Base):
    __tablename__ = 'escrow'
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    vendor_id = Column(Integer, ForeignKey('vendors.id', ondelete="CASCADE"), nullable=False)
    amount = Column(Float, nullable=False)
    fee = Column(Float, nullable=False)
    completed = Column(Boolean, default=False)
    created = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))


class EscrowChats(Base):
    __tablename__ = 'escrow_chats'
    id = Column(Integer, primary_key=True, nullable=False)
    escrow_id = Column(Integer, ForeignKey('escrow.id', ondelete="CASCADE"), nullable=False)
    vendors_chat = Column(Boolean, nullable=False)
    message = Column(String(LONGER_STR), nullable=False)
    created = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))


class BlockChainBalances(Base):#merge the BlockChainBalances with the users table by just providing a new column that will keep track of real wallet balance
    __tablename__ = "wallet_balances"
    address = Column(String(LONG_STR), primary_key=True)
    balance = Column(Float, nullable=False, server_default='0.')
    

class Utility(Base): # make key primary and remove id
    __tablename__ = "utility"
    id = Column(Integer, primary_key=True, nullable=False)
    key = Column(String(LONG_STR), nullable= False, unique=True)
    value = Column(String(LONGER_STR), nullable= False)
