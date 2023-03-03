from tronpy import Tron, AsyncTron
from tronpy.providers import HTTPProvider, AsyncHTTPProvider
from tronpy.keys import PrivateKey
from ...settings import settings
from .. import from_mnemonic, create_with_mnemonic

ENERGY_PRICE = 420

_provider = HTTPProvider(settings.trn_web3_provider_uri, api_key=settings.trn_provider_api_key, jw_token=settings.trn_jwt_token)

web3 = Tron(provider=_provider)

def test_network():
    if web3.get_latest_block_number():
        print("connected to the tron network successfully!")
    else:
        raise Exception("Cannot connect to tron node provider!")

def create_account():
    r = web3.generate_address()
    print(dir(r))
    return r['base58check_address'], r['private_key']

def create_HD_account(passphrase:str='', num_of_words:int=12):
    key, mnemonic = create_with_mnemonic(passphrase=passphrase, num_words=num_of_words, account_type='trx')
    r = web3.generate_address(PrivateKey(bytes.fromhex(key)))
    return r['base58check_address'], r['private_key'], mnemonic

def get_HD_account(mnemonic: str, passphrase: str = "", account_number: int = 0, account_index: int = 0):
    key = from_mnemonic(mnemonic=mnemonic, passphrase=passphrase, account_number=account_number, account_index=account_index, account_type='trx')
    r = web3.generate_address(PrivateKey(bytes.fromhex(key)))
    return r['base58check_address'], r['private_key']

def tron_provider():
    return AsyncTron(provider=AsyncHTTPProvider(settings.trn_web3_provider_uri, api_key=settings.trn_provider_api_key, jw_token=settings.trn_jwt_token))
        