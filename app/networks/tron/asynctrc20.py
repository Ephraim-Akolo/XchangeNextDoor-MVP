from tronpy import AsyncTron
from tronpy.exceptions import TransactionError
from tronpy.keys import PrivateKey
from .provider import async_provider, create_account
from ...settings import settings

address = settings.trc20_contract_address

async def get_total_supply():
    async with AsyncTron(provider=async_provider) as web3:
        contract = await web3.get_contract(address)
        token_decimal = await contract.functions.decimals()
        return await contract.functions.totalSupply()/(10**token_decimal)

async def get_name():
    async with AsyncTron(provider=async_provider) as web3:
        contract = await web3.get_contract(address)
        return contract.functions.name()

async def get_symbol():
    async with AsyncTron(provider=async_provider) as web3:
        contract = await web3.get_contract(address)
        return contract.functions.symbol()

async def get_acct_balance(public_key:str, as_trc20=False):
    async with AsyncTron(provider=async_provider) as web3:
        contract = await web3.get_contract(address)
        token_decimal = await contract.functions.decimals()
        if as_trc20:
            return await contract.functions.balanceOf(public_key)/10**token_decimal
        else:
            return await contract.functions.balanceOf(public_key)

async def send_erc20(from_address:str, to_address:str, private_key:str, amount:float, fee_limit=5_000_000):
    async with AsyncTron(provider=async_provider) as web3:
        contract = await web3.get_contract(address)
        token_decimal = await contract.functions.decimals()
        amount *= (10**token_decimal)
        if not web3.is_address(to_address):
            raise TransactionError('invalid trc20 address!')
        balance = await get_acct_balance(from_address, False)
        if balance < amount:
            raise TransactionError("insufficient trc20 tokens!")
        private_key = PrivateKey(bytes.fromhex(private_key))
        tx = await contract.functions.transfer(to_address, amount).with_owner(from_address).fee_limit(fee_limit).build().sign(private_key)
        return await tx.wait()
    

