from pydantic import BaseSettings

class Settings(BaseSettings):
    eth_web3_provider_uri:str = 'https://goerli.infura.io/v3/0bd85e959eec41069cebf1c502e93168'
    eth_provider_api_key:str = ''
    erc20_contract_address:str = '0x45843aF56Aa1057eD1730cA5Ba3F709833900E77'
    trn_web3_provider_uri:str = 'https://api.shasta.trongrid.io/'
    trn_provider_api_key:str = ''
    trc20_contract_address:str = ""
    trn_jwt_token:str = ''
    xchangenextdoor_db_user:str = 'root'
    xchangenextdoor_db_password:str = 'akolo000'
    xchangenextdoor_db_server:str = 'localhost'
    xchangenextdoor_db_name:str = 'XChangeNextDoor'
    class Config:
        env_file = "./.env"


settings = Settings()