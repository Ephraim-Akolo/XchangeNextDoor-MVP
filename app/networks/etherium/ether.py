from web3.exceptions import ValidationError
from .provider import web3, create_account


def get_latest_block():
    return web3.eth.block_number

def get_acct_balance(public_key:str, as_eth=False):
    if as_eth:
        return web3.fromWei(web3.eth.get_balance(public_key), 'ether')
    else:
        return web3.eth.get_balance(public_key)

def send_ether(from_address:str, to_address:str, private_key:str, amount:float, max_gas_gwei:float=250, gas_fee_gwei:float=3.0, chainid=5, verify_balance=False):
    to_address = web3.toChecksumAddress(to_address)
    if verify_balance:
        balance = get_acct_balance(from_address, False)
        if balance < (web3.toWei(amount, 'ether') + web3.toWei(max_gas_gwei, "gwei")):
            raise ValidationError("insufficient ether!")
    tx = {
        'type': "0x2",
        'nonce': web3.eth.get_transaction_count(from_address),
        'from': from_address,
        'to': to_address,
        'value': web3.toWei(amount, 'ether'),
        'maxFeePerGas': web3.toWei(max_gas_gwei, "gwei"),
        'maxPriorityFeePerGas': web3.toWei(gas_fee_gwei, "gwei"),
        'chainId': chainid
    }
    print(tx["nonce"])
    tx['gas'] = web3.eth.estimate_gas(tx)
    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    web3.eth.wait_for_transaction_receipt(tx_hash)
    return web3.toHex(tx_hash)
