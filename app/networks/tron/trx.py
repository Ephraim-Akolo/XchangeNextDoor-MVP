from .provider import web3, create_account
from tronpy.keys import PrivateKey
from tronpy.exceptions import TransactionError, BadAddress

token_decimal = 6

def get_latest_block():
    return web3.get_latest_block_number()

def get_acct_balance(public_key:str, as_trx=False):
    if as_trx:
        return web3.get_account_balance(public_key)
    else:
        return web3.get_account_balance(public_key) * 10**token_decimal

def send_trx(from_address:str, to_address:str, private_key:str, amount:int, memo='sending trx tokens using sync method', verify_balance=False):
    amount *= (10**token_decimal)
    if not web3.is_address(to_address):
        raise BadAddress('invalid trx address!')
    if verify_balance:
        balance = get_acct_balance(from_address, False)
        if balance < amount:
            raise TransactionError("insufficient trx!")
    private_key = PrivateKey(bytes.fromhex(private_key))
    tx = web3.trx.transfer(from_address, to_address, amount).memo(memo).build().inspect().sign(private_key).broadcast()
    return tx.wait()
    