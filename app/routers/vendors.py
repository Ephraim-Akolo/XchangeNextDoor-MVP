import numpy as np
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..oauth2 import get_vendor_from_token
from ..dbconnect import get_session
from .. import database
from .. import schemas
from ..networks.tron import provider, trx, trc20
from ..settings import settings

router = APIRouter(
    prefix='/api/v1/vendors',
    tags=['Vendors']
)

def get_payment_account(amount:float, accounts:list[tuple]):
    _ = np.array(accounts)
    addresses, balances = _[:, 0], _[:, 1].astype(np.float64)
    addr_amount, l = [], [i for i in range(np.size(balances))]
    if amount > balances.sum():
        return
    while True:
        arg =np.abs(balances[l]-amount).argmin()
        rem = balances[arg] - amount
        if rem < 0:
            addr_amount.append((str(addresses[arg]), float(balances[arg])))
            amount -= balances[arg]
            l.pop(arg)
        else:
            addr_amount.append((str(addresses[arg]), float(amount)))
            break
    return addr_amount

@router.get('/profile', response_model=schemas.VendorProfile)
def get_vendor_profile(token_user:schemas.Vendor = Depends(get_vendor_from_token)):
    return token_user

@router.get("/escrow")  
def get_active_escrows(db_session:Session = Depends(get_session), token_user:schemas.UserComplete = Depends(get_vendor_from_token)):
    escrows = db_session.query(database.Escrow).filter(database.Escrow.vendor_id == token_user.id).filter(database.Escrow.completed==False).all()   
    return escrows

@router.post("/escrow/chat", status_code=201, response_model=list[schemas.EscrowChatsReturned])
def chat_with_user(escrow_id:int, limit:int=5, message:str='', db_session:Session = Depends(get_session), token_user:schemas.UserComplete = Depends(get_vendor_from_token)):
    escrow = db_session.query(database.Escrow).filter(database.Escrow.id == escrow_id).filter(database.Escrow.vendor_id==token_user.id).first()
    if escrow is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized")
    # if message and escrow.completed:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="ESCROW HAS BEEN COMPLETED SUCCESSFULLY")
    if message:
        db_session.add(database.EscrowChats(
            escrow_id = escrow_id,
            message = message,
            vendors_chat = True
        ))
        db_session.commit()
    return db_session.query(database.EscrowChats).filter(database.EscrowChats.escrow_id == escrow_id).order_by(database.EscrowChats.created.desc()).limit(limit).all()[::-1]

@router.post("/transfer")
def transfer_trc20_token(transfer:schemas.TransferToken, db_session:Session = Depends(get_session), token_vendor:schemas.Vendor = Depends(get_vendor_from_token)):
    fee = db_session.query(database.Utility.value).filter(database.Utility.key==settings.utility_vendor_tf_keyname).first()[0]
    if transfer.amount + fee > token_vendor.balance:
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail=f'insufficient balance for transaction: amount={transfer.amount}, fee={fee} !')
    accounts = db_session.query(database.BlockChainBalances.address, database.BlockChainBalances.balance).all()
    transf = get_payment_account(transfer.amount, accounts)
    ret = {}
    for address, _ in transf:
        _caddr, _ckey = provider.get_HD_account(settings.xchangenextdoor_mnemonic, settings.xchangenextdoor_passphrase, settings.users_hd_account_val, 0)
        ret = trx.send_trx(
            from_address=_caddr,
            to_address = address,
            private_key= _ckey,
            amount=28
        )
        #merge the BlockChainBalances with the users table by just providing a new column that will keep track of real wallet balance
        user_id = db_session.query(database.Users.id).filter(database.Users.public_key==address).first()[0]
        ret2 = trc20.send_trc20(
            from_address=address,
            to_address = transfer.address,
            private_key= provider.get_HD_account(settings.xchangenextdoor_mnemonic, settings.xchangenextdoor_passphrase, settings.users_hd_account_val, user_id[1]),
            amount=transfer.amount
        )

        d = database.VendorsTransfers(
            from_address = address,
            to_address = transfer.address,
            amount = transfer.amount,
            status = "SUCCESS",
            fee = fee,
        )
        db_session.add(d)
        ret[address] = d
    db_session.commit()
    return ret


