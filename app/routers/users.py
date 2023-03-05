from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..oauth2 import get_user_from_token
from ..dbconnect import get_session
from .. import database
from .. import schemas
from ..networks.tron import provider
from ..networks.tron import trc20, trx
from ..settings import settings

INSUFFICENT_BALANCE = "INSUFFICIENT BALANCE"
SUCCESS = "SUCCESS"

router = APIRouter(
    prefix='/api/v1/users',
    tags=['Users']
)

@router.get('/profile', response_model=schemas.UserProfile)
def get_user_profile(token_user:schemas.UserComplete = Depends(get_user_from_token)):
    return token_user

@router.post("/transfer")
def transfer_trc20_token(transfer:schemas.TransferToken, db_session:Session = Depends(get_session), token_user:schemas.UserComplete = Depends(get_user_from_token)):
    client_addresses = db_session.query(database.Users.public_key).all()
    client_addresses = [i[0] for i in client_addresses]
    transfer.amount =  abs(transfer.amount)
    if transfer.address in client_addresses:
        if transfer.amount > token_user.balance:
            trans = database.UsersTransfers(
                amount=transfer.amount, 
                fee=0, 
                from_address=token_user.public_key,
                to_address = transfer.address,
                status = INSUFFICENT_BALANCE
                )
            db_session.add(trans)
            db_session.commit()
            db_session.refresh(trans)
            return trans
        else:
            db_session.query(database.Users).filter(database.Users.id == token_user.id).update({'balance': database.Users.balance-transfer.amount},synchronize_session=False)
            db_session.query(database.Users).filter(database.Users.public_key == transfer.address).update({'balance': database.Users.balance+transfer.amount},synchronize_session=False)
            trans = database.UsersTransfers(
                amount=transfer.amount, 
                fee=0, 
                from_address=token_user.public_key,
                to_address = transfer.address,
                status = SUCCESS
                )
            db_session.add(trans)
            db_session.commit()
            db_session.refresh(trans)
            return trans
    else:
        fee:database.Utility = db_session.query(database.Utility).filter(database.Utility.key == settings.utility_users_fee_keyname).first()
        fee = float(fee.value)
        if transfer.amount + fee > token_user.balance:
            trans = database.UsersTransfers(
                amount=transfer.amount, 
                fee=fee, 
                from_address=token_user.public_key,
                to_address = transfer.address,
                status = INSUFFICENT_BALANCE
                )
            db_session.add(trans)
            db_session.commit()
            db_session.refresh(trans)
            return trans
        else:
            _caddr, _ckey = provider.get_HD_account(settings.xchangenextdoor_mnemonic, settings.xchangenextdoor_passphrase, settings.users_hd_account_val, 0)
            ret = trx.send_trx(
                from_address=_caddr,
                to_address = token_user.public_key,
                private_key= _ckey,
                amount=28
            )
            ret2 = trc20.send_trc20(
                from_address=token_user.public_key,
                to_address = transfer.address,
                private_key= provider.get_HD_account(settings.xchangenextdoor_mnemonic, settings.xchangenextdoor_passphrase, settings.users_hd_account_val, token_user.id)[1],
                amount=transfer.amount
            )
            trans = database.UsersTransfers(
                amount=transfer.amount, 
                fee=fee, 
                from_address=token_user.public_key,
                to_address = transfer.address,
                status = SUCCESS
                )
            db_session.add(trans)
            db_session.commit()
            db_session.refresh(trans)
            return trans    

@router.get("/escrow")  
def get_active_escrows(db_session:Session = Depends(get_session), token_user:schemas.UserComplete = Depends(get_user_from_token)):
    escrows = db_session.query(database.Escrow).filter(database.Escrow.user_id == token_user.id).filter(database.Escrow.completed==False).all()   
    return escrows   

@router.post("/escrow/sell", status_code=201)
def sell_trc20_token(transfer:schemas.SellToken, db_session:Session = Depends(get_session), token_user:schemas.UserComplete = Depends(get_user_from_token)):
    fee:database.Utility = db_session.query(database.Utility).filter(database.Utility.key == settings.utility_escrow_fee_keyname).first()
    fee = float(fee.value)
    transfer.amount =  abs(transfer.amount)
    if transfer.amount + fee > token_user.balance:
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail="INSUFFICIENT BALANCE!")
    else:
        db_session.query(database.Users).filter(database.Users.id == token_user.id).update({'balance': database.Users.balance-(transfer.amount+fee)},synchronize_session=False)
        vendor:database.Vendors = db_session.query(database.Vendors).filter(database.Vendors.email == transfer.email.lower()).first()
        if vendor is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"no vendor with email {transfer.email}")
        trans = database.Escrow(
            user_id = token_user.id,
            vendor_id = vendor.id,
            amount = transfer.amount,
            fee= fee,
            )
        db_session.add(trans)
        db_session.commit()
        db_session.refresh(trans)
        return trans

@router.post("/escrow/chat", status_code=201, response_model=list[schemas.EscrowChatsReturned])
def chat_with_vendor(escrow_id:int, limit:int=5, message:str='', db_session:Session = Depends(get_session), token_user:schemas.UserComplete = Depends(get_user_from_token)):
    escrow:database.Escrow = db_session.query(database.Escrow).filter(database.Escrow.id == escrow_id).filter(database.Escrow.user_id==token_user.id).first()
    if escrow is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized")
    # if message and escrow.completed:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="ESCROW HAS BEEN COMPLETED SUCCESSFULLY")
    if message:
        db_session.add(database.EscrowChats(
            escrow_id = escrow_id,
            message = message,
            vendors_chat = False
        ))
        db_session.commit()
    return db_session.query(database.EscrowChats).filter(database.EscrowChats.escrow_id == escrow_id).order_by(database.EscrowChats.created.desc()).limit(limit).all()[::-1]

@router.put("/escrow/verify")
def verify_escrow_transaction(escrow_id:int, db_session:Session = Depends(get_session), token_user:schemas.UserComplete = Depends(get_user_from_token)):
    escrow = db_session.query(database.Escrow).filter(database.Escrow.id == escrow_id).filter(database.Escrow.user_id==token_user.id)
    trans:database.Escrow = escrow.first()
    if trans is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized!")
    escrow.update({'completed': True}, synchronize_session=False)
    db_session.query(database.Vendors).filter(database.Vendors.id == trans.vendor_id).update({"balance": database.Vendors.balance+trans.amount}, synchronize_session=False)
    db_session.commit()
    db_session.refresh(trans)
    return trans

# @router.get('/profile/private-key')
# def get_private_key(token_user:schemas.UserComplete = Depends(get_user_from_token)):
#     address, private_key = provider.get_HD_account(settings.xchangenextdoor_mnemonic, settings.xchangenextdoor_passphrase, token_user.id-1, token_user.address_index)
#     return {"address": address, "private key": private_key}

# @router.get('/profile/allocated')
# def get_all_allocated_addresses(token_user:schemas.UserComplete = Depends(get_user_from_token)):
#     history = []
#     for i in range(token_user.address_index+1):
#         address, private_key = provider.get_HD_account(settings.xchangenextdoor_mnemonic, settings.xchangenextdoor_passphrase, token_user.id-1, i)
#         history.append({"address": address, "private key": private_key})
#     return {'address history': history}

# @router.put('/profile/generate/address', response_model=schemas.UserProfile)
# def generate_a_new_address(token_user:schemas.UserComplete = Depends(get_user_from_token), db_session:Session = Depends(get_session)):
#     new_index = token_user.address_index + 1
#     address, private_key = provider.get_HD_account(settings.xchangenextdoor_mnemonic, settings.xchangenextdoor_passphrase, token_user.id-1, new_index)
#     db_session.query(database.Users).filter(database.Users.id == token_user.id).update({"public_key": address, "address_index": new_index})
#     db_session.commit()
#     token_user.public_key = address
#     return token_user
