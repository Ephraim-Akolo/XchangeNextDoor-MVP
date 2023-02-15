from fastapi import APIRouter, HTTPException,status, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import schemas, database, utils, oauth2
from ..dbconnect import get_session

router = APIRouter(
    prefix="/api/v1/",
    tags=['Authentication']
)

@router.post('/signup/users',status_code=status.HTTP_201_CREATED, response_model=schemas.Users)
def signup_users(users:schemas.Users, db_session:Session = Depends(get_session)):
    if users.password != users.confirm_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unmatched passwords!")
    existing_user = db_session.query(database.Users).filter(database.Users.email==users.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_302_FOUND, detail=f'A user with the email "{users.email}" already exists!')
    users.password = utils.hash_password(users.password)
    d_users = users.dict()
    d_users.pop('confirm_password')
    new_user = database.Users(**d_users)
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)
    return new_user

@router.post('/login/users')
def login_users(user_cred:OAuth2PasswordRequestForm = Depends(), db_session:Session = Depends(get_session)):
    user = db_session.query(database.Users).filter(database.Users.email == user_cred.username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials!")
    if utils.verify_password(user_cred.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials!")
    data = {'user_id': user.id}
    return oauth2.create_access_token(data)

