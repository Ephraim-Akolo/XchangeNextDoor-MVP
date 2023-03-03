from pydantic import BaseModel, EmailStr
from datetime import datetime


class Browser(BaseModel): # only used by test nodes currently.
    block_number:int
    to_block:int
    to_address:str|list = None
    from_address:str|list = None
    strict:bool = False


class UserSignup(BaseModel):
    email: EmailStr
    password: str
    confirm_password:str

class VendorSignup(UserSignup):
    pass


class UserResponse(BaseModel):
    id:int
    email: EmailStr
    # password: str
    class Config:
        orm_mode = True


class UserProfile(BaseModel):
    id: int
    email: EmailStr
    public_key: str
    balance: float
    class Config:
        orm_mode = True


class UserComplete(BaseModel):
    id: int
    email: EmailStr
    password: str
    public_key: str
    balance: float


class Vendor(BaseModel):
    id: int
    email: EmailStr
    password: str
    balance: float


class VendorProfile(BaseModel):
    id: int
    email: EmailStr
    balance: float
    class Config:
        orm_mode = True


class TransferToken(BaseModel):
    address:str
    amount:float

class SellToken(BaseModel):
    email:str
    amount:float


class EscrowChatsReturned(BaseModel):
    vendors_chat:bool
    message:str
    created:datetime
    class Config:
        orm_mode = True
    

