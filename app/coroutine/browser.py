from threading import Thread
from sqlalchemy.orm import Session
from time import sleep
from datetime import datetime
from .. import database
from ..networks.tron import trc20
from ..dbconnect import get_session
from ..settings import settings
# from ..oauth2 import aes_decode_data
# from ..networks.tron import provider# from ..settings import settings
# from ..oauth2 import aes_decode_data
from ..networks.tron import provider


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
        print(['process_blocks', e])
    db_session = None

def process_a_block(blck_num, addresses, db_session:Session):
    try:
        transactions = trc20.search_block_chain(blck_num, blck_num, to_address=addresses, as_trc20=True)
    except:
        sleep(2)
        print("RETRYING...................")
        transactions = trc20.search_block_chain(blck_num, blck_num, to_address=addresses, as_trc20=True)
    for trans in transactions:
        if trans['ret'].lower() == "success":
            db_session.query(database.Users).filter(database.Users.public_key == trans['to_address']).update({"balance": database.Users.balance+trans['amount']}, synchronize_session=False)
        db_session.add(database.Fundings(
            from_address=trans['owner_address'],
            to_address = trans['to_address'],
            amount = trans['amount'],
            block_number = trans['block_number'],
            status = trans['ret'],
            timestamp = datetime.fromtimestamp(trans['timestamp']/1000.0)
            ))

# def send_transactions2backend(transactions:list[database.Fundings]):
#     for t in transactions:
#         CustomThread(
#             name=f'send_transactions2backend: id {t.id}',
#             target= send_token,
#             args= (t,)
#         ).start()

# def send_token(transaction:database.Fundings):
#     try:
#         db_session = next(get_session())
#         user = db_session.query(database.Users).filter(database.Users.public_key == transaction.to_address).first()
#         if user is None:
#             print(f"{transaction.to_address} has no private key!")
#             raise Exception("")
#         _, _private_key = provider.get_HD_account(settings.xchangenextdoor_mnemonic, settings.xchangenextdoor_passphrase, user.id-1, user.address_index)
#         _amount = user.balance
#         print(_private_key, "private key kdjfjkljfojjp[p[]]")
#         t = trc20.send_trc20(transaction.to_address, settings.central_wallet_address, _private_key, transaction.amount)
#     except Exception as e:
#         print(e)
#         db_session.rollback()
#         del db_session
#     else:
#         db_session.query(database.Fundings).filter(database.Fundings.id == transaction.id).update({"success": 1}, synchronize_session=False)
#         db_session.query(database.Users).filter(database.Users.public_key == transaction.to_address).update({"balance": _amount+transaction.amount}, synchronize_session=False)
#         db_session.commit()
#     db_session = None