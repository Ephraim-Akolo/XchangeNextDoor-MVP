import uvicorn
from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from ..dbconnect import get_session
from .. import database
from ..settings import settings
from ..networks.tron import trx
from .browser import process_blocks, send_transactions2backend
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

@app.on_event('startup')
@repeat_every(seconds= 15)
def blockchain_browser():
    try:
        db_session = next(get_session())
        print("UPDATING DATABASE FROM THE BLOCKCHAIN")
        req = db_session.query(database.Utility).filter(database.Utility.key == settings.utility_lastblock_keyname)
        last_block_number = req.first()
        # last_block_number.value = 48676766 ########################################33
        client_addresses = db_session.query(database.Users.public_key).all()
        client_addresses = [i[0] for i in client_addresses]
        # client_addresses = client_addresses + ["TB9j7UcCCU24j56Rs1nzcFd33Rvs6666K6", "TP7uqKBqbD7DivmzacvbxMGpx7VXwc1k5A", "TGrHAULgQnJhV5ysnS7a46J3HsqmnipMdN", "THQyejdxnUNYEsDjhy4KmAEs35Paqh4rBF"]
        newest_block_number = trx.get_latest_block() - 20
        # newest_block_number = 48676772 ###########################3
        prop = database.Utility(key=settings.utility_lastblock_keyname, value = str(newest_block_number))
        if last_block_number is None:
            db_session.add(prop)
            last_block_number = newest_block_number-1
        else:
            last_block_number = int(last_block_number.value)
            req.update({'value': prop.value}, synchronize_session=False)

        inter = 5
        _mul = ((newest_block_number - last_block_number)//inter)
        for i in range(_mul):
            from_block = last_block_number + (inter*i)
            to_block = last_block_number + (inter*(i+1))
            process_blocks(from_block, to_block, client_addresses)
        else:
            from_block = (last_block_number + (inter * _mul))
            to_block = newest_block_number
            if to_block > from_block:
                process_blocks(from_block, to_block, client_addresses)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        logger.error(['blockchain_browser logger', e])
    db_session = None

@app.on_event('startup')
@repeat_every(seconds=30)
def redirect_token():
    db_session = next(get_session())
    try:
        print("UPDATING DATABASE FROM THE BLOCKCHAIN")  
        pending_transactions = db_session.query(database.Fundings).filter(database.Fundings.success == 0).filter(database.Fundings.status == "SUCCESS").all()
        if pending_transactions is not None:
            send_transactions2backend(pending_transactions)
        del db_session
    except Exception as e:
        db_session.rollback()
        logger.error(['redirect_token logger', e])
    db_session = None

@app.get("/")
def index():
    return {"status": "running"}
        

if __name__ == "__main__":
    uvicorn.run("app.main:app", host='0.0.0.0', port=8000, reload=True)

