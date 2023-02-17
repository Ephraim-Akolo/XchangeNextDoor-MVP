from fastapi import APIRouter, Depends, HTTPException, status
from ..oauth2 import get_user_from_token
from .. import schemas

router = APIRouter(
    prefix='/api/v1/users',
    tags=['Users']
)

@router.get('/profile', response_model=schemas.UserProfile)
def get_user_profile(token_user:schemas.UserComplete = Depends(get_user_from_token)):
    if token_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Aunthenticate": "Bearer"})
    return token_user