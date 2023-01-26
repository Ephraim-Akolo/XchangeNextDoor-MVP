from web3 import Web3
from ...settings import settings

provider = Web3.HTTPProvider(settings.eth_web3_provider_uri)

web3 = Web3(provider)

if web3.isConnected():
    print("connected to the etherium network successfully!")
else:
    raise Exception("Cannot connect to node provider!")
