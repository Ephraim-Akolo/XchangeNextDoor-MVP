from fastapi import APIRouter, Depends, HTTPException, status
from ..oauth2 import get_user_from_token
from .. import schemas
from ..networks.tron import trx, trc20
from ..settings import settings

router = APIRouter(
    prefix='/api/v1/backend',
    tags=['BACKEND']
)

@router.get('/centralwallet/balance/{token}')
def get_central_wallet_balance(token:str):
    if token.lower() == 'trx':
        return {"trx balance": trx.get_acct_balance(settings.central_wallet_address, as_trx=True)}
    elif token.lower() == 'trx':
        return {"trx balance": trc20.get_acct_balance(settings.central_wallet_address, as_trx=True)}

@router.post('/centralwallet/transfer')
def send_token(amount:int, address:str):
    try:
        tx = trc20.send_erc20(settings.central_wallet_address, address, settings.central_wallet_key, amount)
    except:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail=f"Failed to send token!")
    return tx
