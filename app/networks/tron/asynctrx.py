from tronpy.exceptions import TransactionError, BadAddress, BlockNotFound, AddressNotFound
from tronpy.keys import PrivateKey
from .provider import create_account, tron_provider


token_decimal = 6

async def get_latest_block():
    async with tron_provider() as web3:
        return await web3.get_latest_block_number()

async def get_acct_balance(public_key:str, as_trx=False):
    async with tron_provider() as web3:
        try:
            if as_trx:
                return await web3.get_account_balance(public_key)
            else:
                return await web3.get_account_balance(public_key) * 10**token_decimal
        except AddressNotFound as e:
            return "Address Not Found On Chain!"

async def search_block_chain(block_number:int, to_block:int, to_address:str|list = None, from_address:str|list = None, strict=False, as_trx=False):
    async with tron_provider() as web3:
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
                if _type != "TransferContract":
                    continue
                _to_address = web3.to_base58check_address(trans['raw_data']['contract'][0]['parameter']['value']['to_address'])
                _from_address = web3.to_base58check_address(trans['raw_data']['contract'][0]['parameter']['value']['owner_address'])
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
                _amount = trans['raw_data']['contract'][0]['parameter']['value']['amount']
                ret_dict = {
                'block_number': block_number,
                'ret': trans['ret'][0]['contractRet'],
                'timestamp': trans['raw_data']['timestamp'],
                'amount': _amount/(10**token_decimal) if as_trx else _amount,
                'owner_address': _from_address,
                'to_address': _to_address
                } 
                ret.append(ret_dict)
            if block_number >= to_block:
                return ret
            block_number += 1

async def send_trx(from_address:str, to_address:str, private_key:str, amount:float, memo=""):
    async with tron_provider() as web3:
        amount *= (10**token_decimal)
        if not web3.is_address(to_address):
            raise BadAddress('invalid trx address!')
        private_key = PrivateKey(bytes.fromhex(private_key))
        tx = web3.trx.transfer(from_address, to_address, int(amount)).memo(memo).build().inspect().sign(private_key)
        tx = await tx.broadcast()
        return await tx.wait()
    

