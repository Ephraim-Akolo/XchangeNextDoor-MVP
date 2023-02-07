from tronpy import Tron
from tronpy.providers import HTTPProvider, AsyncHTTPProvider
from ...settings import settings

_provider = HTTPProvider(settings.trn_web3_provider_uri, api_key=settings.trn_provider_api_key)

web3 = Tron(provider=_provider)

if web3.get_latest_block_number():
    print("connected to the tron network successfully!")
else:
    raise Exception("Cannot connect to tron node provider!")

async_provider = AsyncHTTPProvider(settings.trn_web3_provider_uri, api_key=settings.trn_provider_api_key)

def create_account():
    r = web3.generate_address()
    print(dir(r))
    return r['base58check_address'], r['private_key']