from pydantic import BaseModel, EmailStr
from datetime import date, datetime


class Browser(BaseModel):
    block_number:int
    to_block:int
    to_address:str|list = None
    from_address:str|list = None
    strict:bool = False


class UserSignup(BaseModel):
    email: EmailStr
    password: str
    confirm_password:str


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
    address_index:int
    password: str
    balance: float
    

