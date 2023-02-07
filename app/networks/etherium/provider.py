from web3 import Web3
from ...settings import settings

c = settings.eth_web3_provider_uri[0]
if c.lower() == 'w':
    _provider = Web3.WebsocketProvider(f"{settings.eth_web3_provider_uri[:6]}:{settings.eth_provider_api_key}@{settings.eth_web3_provider_uri[6:]}")
else:
    _provider = Web3.HTTPProvider(f"{settings.eth_web3_provider_uri[:8]}:{settings.eth_provider_api_key}@{settings.eth_web3_provider_uri[8:]}")

web3 = Web3(_provider)

if web3.isConnected():
    print("connected to the etherium network successfully!")
else:
    raise Exception("Cannot connect to etherium node provider!")

def create_account(random_string:str="wHATS UP"):
    r = web3.eth.account.create(random_string)
    return r.address, r.key.hex()
