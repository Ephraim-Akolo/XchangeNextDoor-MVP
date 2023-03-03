from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..oauth2 import get_vendor_from_token
from ..dbconnect import get_session
from .. import database
from .. import schemas
from ..networks.tron import provider
from ..settings import settings

router = APIRouter(
    prefix='/api/v1/vendors',
    tags=['Vendors']
)

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

