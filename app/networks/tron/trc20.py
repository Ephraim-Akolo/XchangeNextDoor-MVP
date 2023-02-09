from .provider import web3, create_account
from ...settings import settings
from tronpy.keys import PrivateKey
from tronpy.exceptions import TransactionError

address = settings.trc20_contract_address
contract = web3.get_contract(address)
token_decimal = contract.functions.decimals()


def get_total_supply():
    return contract.functions.totalSupply()/(10**token_decimal)

def get_name():
    return contract.functions.name()

def get_symbol():
    return contract.functions.symbol()

def get_acct_balance(public_key:str, as_trc20=False): # can fail!
    if as_trc20:
        return contract.functions.balanceOf(public_key)/10**token_decimal
    else:
        return contract.functions.balanceOf(public_key)

def send_erc20(from_address:str, to_address:str, private_key:str, amount:float, fee_limit=5_000_000):
    amount *= (10**token_decimal)
    if not web3.is_address(to_address):
        raise TransactionError('invalid trc20 address!')
    balance = get_acct_balance(from_address, False)
    if balance < amount:
        raise TransactionError("insufficient trc20 tokens!")
    private_key = PrivateKey(bytes.fromhex(private_key))
    tx = contract.functions.transfer(to_address, amount).with_owner(from_address).fee_limit(fee_limit).build().sign(private_key)
    return tx.wait()
    

