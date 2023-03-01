from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..oauth2 import get_user_from_token
from ..dbconnect import get_session
from .. import database
from .. import schemas
from ..networks.tron import provider
from ..settings import settings

router = APIRouter(
    prefix='/api/v1/users',
    tags=['Users']
)

@router.get('/profile', response_model=schemas.UserProfile)
def get_user_profile(token_user:schemas.UserComplete = Depends(get_user_from_token)):
    if token_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Aunthenticate": "Bearer"})
    return token_user

@router.get('/profile/private-key')
def get_private_key(token_user:schemas.UserComplete = Depends(get_user_from_token)):
    address, private_key = provider.get_HD_account(settings.xchangenextdoor_mnemonic, settings.xchangenextdoor_passphrase, token_user.id-1, token_user.address_index)
    return {"address": address, "private key": private_key}

@router.get('/profile/allocated')
def get_all_allocated_addresses(token_user:schemas.UserComplete = Depends(get_user_from_token)):
    history = []
    for i in range(token_user.address_index+1):
        address, private_key = provider.get_HD_account(settings.xchangenextdoor_mnemonic, settings.xchangenextdoor_passphrase, token_user.id-1, i)
        history.append({"address": address, "private key": private_key})
    return {'address history': history}

@router.put('/profile/generate/address', response_model=schemas.UserProfile)
def generate_a_new_address(token_user:schemas.UserComplete = Depends(get_user_from_token), db_session:Session = Depends(get_session)):
    new_index = token_user.address_index + 1
    address, private_key = provider.get_HD_account(settings.xchangenextdoor_mnemonic, settings.xchangenextdoor_passphrase, token_user.id-1, new_index)
    db_session.query(database.Users).filter(database.Users.id == token_user.id).update({"public_key": address, "address_index": new_index})
    db_session.commit()
    token_user.public_key = address
    return token_user
