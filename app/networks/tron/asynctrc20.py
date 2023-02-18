from tronpy.exceptions import TransactionError, BadAddress, BlockNotFound, AddressNotFound
from tronpy.keys import PrivateKey
from tronpy.abi import trx_abi
from .provider import tron_provider, create_account
from ...settings import settings

address = settings.trc20_contract_address

async def get_total_supply():
    async with tron_provider() as web3:
        contract = await web3.get_contract(address)
        token_decimal = await contract.functions.decimals()
        return await contract.functions.totalSupply()/(10**token_decimal)

async def get_name():
    async with tron_provider() as web3:
        contract = await web3.get_contract(address)
        return contract.functions.name()

async def get_symbol():
    async with tron_provider() as web3:
        contract = await web3.get_contract(address)
        return contract.functions.symbol()

async def get_acct_balance(public_key:str, as_trc20=False):
    async with tron_provider() as web3:
        contract = await web3.get_contract(address)
        token_decimal = await contract.functions.decimals()
        try:
            if as_trc20:
                return await contract.functions.balanceOf(public_key)/10**token_decimal
            else:
                return await contract.functions.balanceOf(public_key)
        except AddressNotFound as e:
            return "Address Not Found On Chain!"

async def search_block_chain(block_number:int, to_block:int, to_address:str|list = None, from_address:str|list = None, strict=False, as_trc20=False):
    async with tron_provider() as web3:
        contract = await web3.get_contract(address)
        token_decimal = await contract.functions.decimals()
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
        while True:
            try:
                block = await web3.get_block(block_number)
            except BlockNotFound:
                return ret
            except Exception as e:
                raise e
            try:
                transactions = block['transactions']
            except:
                return ret
            for trans in transactions:
                _type = trans['raw_data']['contract'][0]['type']
                if not (_type == "TriggerSmartContract" and 
                        trans['raw_data']['contract'][0]['parameter']['value']['contract_address'] == address):
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

async def send_trc20(from_address:str, to_address:str, private_key:str, amount:int, fee_limit=5_000_000, verify_balance=False):
    async with tron_provider() as web3:
        contract = await web3.get_contract(address)
        token_decimal = await contract.functions.decimals()
        amount *= (10**token_decimal)
        if not web3.is_address(to_address):
            raise BadAddress('invalid trc20 address!')
        if verify_balance:
            balance = await get_acct_balance(from_address, False)
            if balance < amount:
                raise TransactionError("insufficient trc20 tokens!")
        private_key = PrivateKey(bytes.fromhex(private_key))
        tx = await contract.functions.transfer(to_address, int(amount)).with_owner(from_address).fee_limit(fee_limit).build().sign(private_key).broadcast()
        return await tx.wait()
    

