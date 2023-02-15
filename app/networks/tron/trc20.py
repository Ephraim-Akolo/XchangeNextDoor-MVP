from .provider import web3, create_account
from ...settings import settings
from tronpy.keys import PrivateKey
from tronpy.exceptions import TransactionError, BadAddress, BlockNotFound
from tronpy.abi import trx_abi

address = settings.trc20_contract_address
contract = web3.get_contract(address)
token_decimal = contract.functions.decimals()


def get_total_supply():
    return contract.functions.totalSupply()/(10**token_decimal)

def get_name():
    return contract.functions.name()

def get_symbol():
    return contract.functions.symbol()

def get_acct_balance(public_key:str, as_trc20=False):
    if as_trc20:
        return contract.functions.balanceOf(public_key)/10**token_decimal
    else:
        return contract.functions.balanceOf(public_key)

def search_block_chain(block_number:int, to_block:int, to_address:str|list = None, from_address:str|list = None, strict=False, as_trc20=False):
    if strict and (to_address is None or from_address is None):
        raise Exception("Both to_address and from_address parameter must be provided when strict is True!")
    if to_address is not None:
        if isinstance(to_address, str):
            to_address = [web3.to_base58check_address(to_address)]
        else:
            to_address = [web3.to_base58check_address(addr) for addr in to_address]
    if from_address is not None:
        if isinstance(from_address,str):
            from_address = [web3.to_base58check_address(from_address)]
        else:
            from_address = [web3.to_base58check_address(addr) for addr in from_address]
    ret = []
    contract_address = settings.trc20_contract_address
    while True:
        try:
            block = web3.get_block(block_number)
        except BlockNotFound:
            return ret
        except Exception as e:
            raise e
        for trans in block['transactions']:
            _type = trans['raw_data']['contract'][0]['type']
            if not (_type == "TriggerSmartContract" and 
                    trans['raw_data']['contract'][0]['parameter']['value']['contract_address'] == contract_address):
                continue
            _from_address = web3.to_base58check_address(trans['raw_data']['contract'][0]['parameter']['value']['owner_address'])
            _to_address, _amount = trx_abi.decode(['address', 'uint256'], bytes.fromhex(trans['raw_data']['contract'][0]['parameter']['value']['data'][8:]))
            if strict:
                if _to_address not in to_address or _from_address not in from_address:
                    continue
            elif to_address is not None and from_address is not None:
                if _to_address not in to_address and _from_address not in from_address:
                    continue
            elif to_address is not None:
                if _to_address not in to_address:
                    continue
            elif from_address is not None:
                if _from_address not in from_address:
                    continue
            else:
                return
            ret_dict = {
            'block_number': block_number,
            'ret': trans['ret'][0]['contractRet'],
            'timestamp': trans['raw_data']['timestamp'],
            'amount': _amount/(10**token_decimal) if as_trc20 else _amount,
            'owner_address': _from_address,
            'to_address': _to_address
            } 
            ret.append(ret_dict)
        if block_number >= to_block:
            return ret
        block_number += 1

def send_erc20(from_address:str, to_address:str, private_key:str, amount:float, fee_limit=5_000_000, verify_balance=False):
    amount *= (10**token_decimal)
    if not web3.is_address(to_address):
        raise BadAddress('invalid trc20 address!')
    if verify_balance:
        balance = get_acct_balance(from_address, False)
        if balance < amount:
            raise TransactionError("insufficient trc20 tokens!")
    private_key = PrivateKey(bytes.fromhex(private_key))
    tx = contract.functions.transfer(to_address, amount).with_owner(from_address).fee_limit(fee_limit).build().sign(private_key)
    return tx.wait()
    

