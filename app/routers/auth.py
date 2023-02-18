from fastapi import APIRouter, HTTPException,status, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import schemas, database, utils, oauth2
from ..dbconnect import get_session
from ..networks.tron import provider, trx
from ..settings import settings

router = APIRouter(
    prefix="/api/v1",
    tags=['Authentication']
)

@router.post('/signup/users',status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def signup_users(users:schemas.UserSignup, db_session:Session = Depends(get_session)):
    users.email = users.email.lower()
    if users.password != users.confirm_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unmatched passwords!")
    existing_user = db_session.query(database.Users).filter(database.Users.email==users.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_302_FOUND, detail=f'A user with the email "{users.email}" already exists!')
    users.password = utils.hash_password(users.password)
    d_users = users.dict()
    d_users.pop('confirm_password')
    _pub_key, _priv_key = provider.create_account()
    d_users['private_key'] = oauth2.aes_encode_data(_priv_key)
    d_users['public_key'] = _pub_key
    new_user = database.Users(**d_users)
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)
    # activate account
    try:
        trx.send_trx(settings.central_wallet_address, _pub_key, settings.central_wallet_key, 30)
    except:
        print("account acctivation failed!")
    return new_user

@router.post('/login/users')
def login_users(user_cred:OAuth2PasswordRequestForm = Depends(), db_session:Session = Depends(get_session)):
    user = db_session.query(database.Users).filter(database.Users.email == user_cred.username.lower()).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials!")
    if not utils.verify_password(user_cred.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials!")
    data = {'id': user.id}
    return {"access_token": oauth2.create_access_token(data), "token_type": "bearer"}

