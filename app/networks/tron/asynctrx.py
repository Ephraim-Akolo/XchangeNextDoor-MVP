from tronpy import AsyncTron
from tronpy.keys import PrivateKey
from .provider import async_provider, create_account

token_decimal = 6

async def get_latest_block():
    async with AsyncTron(provider=async_provider) as web3:
        return await web3.get_latest_block_number()

async def get_acct_balance(public_key:str, as_trx=False):
    async with AsyncTron(provider=async_provider) as web3:
        if as_trx:
            return await web3.get_account_balance(public_key)
        else:
            return await web3.get_account_balance(public_key) * 10**token_decimal

async def send_trx(from_address:str, to_address:str, private_key:str, amount:int):
    async with AsyncTron(provider=async_provider) as web3:
        amount *= (10**token_decimal)
        if not web3.is_address(to_address):
            return 'invalid address!'
        balance = await get_acct_balance(from_address, False)
        if balance < amount:
            return "insufficient trx!"
        private_key = PrivateKey(bytes.fromhex(private_key))
        tx = await web3.trx.transfer(from_address, to_address, amount).memo("first transaction").build().inspect().sign(private_key).broadcast()
        return await tx.wait()
    

