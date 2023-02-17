from threading import Thread
from time import sleep
from datetime import datetime
from .. import database
from .tron import trc20
from ..dbconnect import get_session
from ..settings import settings
from ..oauth2 import aes_decode_data


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
    del db_session

def process_a_block(blck_num, addresses, db_session):
    try:
        transactions = trc20.search_block_chain(blck_num, blck_num, to_address=addresses, as_trc20=True)
    except:
        sleep(2)
        transactions = trc20.search_block_chain(blck_num, blck_num, to_address=addresses, as_trc20=True)
    for trans in transactions:
        db_session.add(database.Fundings(
            from_address=trans['owner_address'],
            to_address = trans['to_address'],
            amount = trans['amount'],
            block_number = trans['block_number'],
            status = trans['ret'],
            timestamp = datetime.fromtimestamp(trans['timestamp']/1000.0)
            ))

def send_transactions2backend(transactions:list[database.Fundings]):
    for t in transactions:
        CustomThread(
            name=f'send_transactions2backend: id {t.id}',
            target= send_token,
            args= (t,)
        ).start()

def send_token(transaction:database.Fundings):
    try:
        db_session = next(get_session())
        en_private_key = db_session.query(database.Users).filter(database.Users.public_key == transaction.to_address).first()
        if en_private_key is None:
            print(f"{transaction.to_address} has no private key!")
            raise Exception("")
        _private_key = aes_decode_data(en_private_key.private_key)
        _amount = en_private_key.balance
        print(_private_key, "private key kdjfjkljfojjp[p[]]")
        t = trc20.send_erc20(transaction.to_address, settings.central_wallet_address, _private_key, int(transaction.amount))
    except Exception as e:
        print(e)
        db_session.rollback()
        del db_session
    else:
        db_session.query(database.Fundings).filter(database.Fundings.id == transaction.id).update({"success": 1}, synchronize_session=False)
        db_session.query(database.Users).filter(database.Users.public_key == transaction.to_address).update({"balance": _amount+transaction.amount}, synchronize_session=False)
        db_session.commit()
        del db_session