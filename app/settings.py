from pydantic import BaseSettings

class Settings(BaseSettings):
    eth_web3_provider_uri:str = 'https://goerli.infura.io/v3/0bd85e959eec41069cebf1c502e93168'
    trn_web3_provider_uri:str = ''
    erc20_contract_address:str = '0x45843aF56Aa1057eD1730cA5Ba3F709833900E77'
    class Config:
        env_file = "./.env"


settings = Settings()