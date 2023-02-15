from pydantic import BaseModel, EmailStr
from datetime import date, datetime

class Browser(BaseModel):
    block_number:int
    to_block:int
    to_address:str|list = None
    from_address:str|list = None
    strict:bool = False

class Users(BaseModel):
    email: EmailStr
    password: str
    confirm_password:str