from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from Crypto.Cipher import AES
from .settings import settings
from .dbconnect import get_session
from . import database, schemas

oauth2_scheme_users = OAuth2PasswordBearer(tokenUrl="/api/v1/login/users", scheme_name='User Login')
oauth2_scheme_vendors = OAuth2PasswordBearer(tokenUrl="/api/v1/login/vendors", scheme_name='Vendor Login')


def aes_encode_data(data:str):
    cipher = AES.new(bytes.fromhex(settings.aes_secret_key), AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(data.encode())
    return (tag.hex() + cipher.nonce.hex() + ciphertext.hex())

def aes_decode_data(cipher_token:str):
    tag = bytes.fromhex(cipher_token[:32])
    nonce = bytes.fromhex(cipher_token[32:64])
    ciphertext = bytes.fromhex(cipher_token[64:])
    cipher = AES.new(bytes.fromhex(settings.aes_secret_key), AES.MODE_GCM, nonce=nonce)
    data = cipher.decrypt_and_verify(ciphertext, tag)
    return data.decode()

def create_access_token(data:dict):
    to_encode = data.copy()
    exp = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode['exp'] = exp
    return jwt.encode(to_encode, settings.jwt_secret_key, settings.jwt_algorithm)

def verify_token(token:str):
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, settings.jwt_algorithm)
        if payload['id'] is None:
            raise JWTError
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Aunthenticate": "Bearer"})

def get_user_from_token(token = Depends(oauth2_scheme_users), db_session:Session = Depends(get_session)):
    payload =  verify_token(token)
    user = db_session.query(database.Users).filter(database.Users.id == payload['id']).first()
    return schemas.UserComplete(id=user.id, email=user.email, password=user.password, public_key=user.public_key, balance=user.balance)


def get_vendor_from_token(token = Depends(oauth2_scheme_vendors), db_session:Session = Depends(get_session)):
    payload =  verify_token(token)
    vendor = db_session.query(database.Vendors).filter(database.Vendors.id == payload['id']).first()
    return schemas.Vendor(id=vendor.id, email=vendor.email, password=vendor.password, balance=vendor.balance)

