from fastapi import APIRouter, Depends
from ..oauth2 import get_user_from_token
from .. import schemas

router = APIRouter(
    prefix='/api/v1/users',
    tags=['Users']
)

@router.get('/profile', response_model=schemas.UserProfile)
def get_user_profile(token_user:schemas.UserComplete = Depends(get_user_from_token)):
    return token_user