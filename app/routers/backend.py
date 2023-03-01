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
    elif token.lower() == 'trc20':
        return {"trx balance": trc20.get_acct_balance(settings.central_wallet_address, as_trc20=True)}

@router.post('/centralwallet/transfer')
def send_token(token:str, amount:float, address:str):
    try:
        tx = None
        if token.lower() == 'trx':
            tx = trx.send_trx(settings.central_wallet_address, address, settings.central_wallet_key, amount)
        elif token.lower() == 'trc20':
            tx = trc20.send_trc20(settings.central_wallet_address, address, settings.central_wallet_key, amount)
    except:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail=f"Failed to send token!")
    return tx
