from threading import Thread
from datetime import datetime
from time import sleep
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from .networks.etherium import ether, erc20
import logging
from .networks.tron import trx, trc20, asynctrx, asynctrc20
from .routers import tests, auth, users
from .dbconnect import Base, engine, get_session
from . import database
from .settings import settings

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

Base.metadata.create_all(engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

@app.get("/")
def index():
    return {
        # "latest eth block": ether.get_latest_block(), 
        # 'latest trx block': trx.get_latest_block(),
        # "erc20 total supply":erc20.get_total_supply(), 
        # "erc20 token_name": erc20.get_name(), 
        # "erc20 token_symbol": erc20.get_symbol(),
        "trc20 total supply":trc20.get_total_supply(), 
        "trc20 token_name": trc20.get_name(), 
        "trc20 token_symbol": trc20.get_symbol(),
        }


app.include_router(auth.router)
app.include_router(users.router)

app.include_router(tests.router)


from fastapi_utils.tasks import repeat_every

class CustomThread(Thread):
    def run(self):
        self.exc = None
        try:
            if self._target is not None:
                self.ret = self._target(*self._args, **self._kwargs)
        except BaseException as e:
            self.exc = e
        finally:
            del self._target, self._args, self._kwargs

    def join(self, timeout=None):
        super(CustomThread, self).join(timeout)
        if self.exc:
            raise self.exc
        return self.ret


@app.on_event('startup')
@repeat_every(seconds= 15)
def blockchain_browser():
    db_session = next(get_session())
    print("Kdjfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff")
    try:
        req = db_session.query(database.Utility).filter(database.Utility.key == settings.utility_lastblock_keyname)
        last_block_number = req.first()
        # last_block_number.value = 48676766 ########################################33
        client_addresses = db_session.query(database.Users.public_key).all()
        client_addresses = [i[0] for i in client_addresses]
        client_addresses = client_addresses + ["TB9j7UcCCU24j56Rs1nzcFd33Rvs6666K6", "TP7uqKBqbD7DivmzacvbxMGpx7VXwc1k5A", "TGrHAULgQnJhV5ysnS7a46J3HsqmnipMdN", "THQyejdxnUNYEsDjhy4KmAEs35Paqh4rBF"]
        newest_block_number = trx.get_latest_block() - 20
        # newest_block_number = 48676772 ###########################3
        prop = database.Utility(key=settings.utility_lastblock_keyname, value = str(newest_block_number))
        if last_block_number is None:
            db_session.add(prop)
            last_block_number = newest_block_number-1
        else:
            last_block_number = int(last_block_number.value)
            req.update({'key': prop.key, 'value': prop.value}, synchronize_session=False)

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
        logger.error(e)
        del db_session
    
def process_blocks(from_address, to_address, addresses):
    try:
        _threads = []
        db_session = next(get_session())
        for blck_num in range(from_address, to_address):
            _x = CustomThread(
                name=f'BLOCK:{blck_num} - Thread',
                target= process_a_block,
                args=(blck_num, addresses,db_session),
                daemon=True
            )
            _threads.append(_x)
            _x.start()
        else:
            for obj in _threads:
                obj.join()
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        del db_session
        raise e

def process_a_block(blck_num, addresses, db_session):
    try:
        transactions = trx.search_block_chain(blck_num, blck_num, to_address=addresses, as_trx=True)
    except:
        sleep(2)
        transactions = trx.search_block_chain(blck_num, blck_num, to_address=addresses, as_trx=True)
    for trans in transactions:
        db_session.add(database.Fundings(
            from_address=trans['owner_address'],
            to_address = trans['to_address'],
            amount = trans['amount'],
            block_number = trans['block_number'],
            status = trans['ret'],
            timestamp = datetime.fromtimestamp(trans['timestamp']/1000.0)
            ))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host='0.0.0.0', port=8000, reload=True)

