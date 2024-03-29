from pydantic import BaseSettings

class Settings(BaseSettings):
    eth_web3_provider_uri:str = 'https://goerli.infura.io/v3/0bd85e959eec41069cebf1c502e93168'
    eth_provider_api_key:str
    erc20_contract_address:str = '0x45843aF56Aa1057eD1730cA5Ba3F709833900E77'
    trn_web3_provider_uri:str = 'https://nile.trongrid.io/'
    trn_provider_api_key:str
    trc20_contract_address:str
    trn_jwt_token:str
    xchangenextdoor_db_user:str = 'root'
    xchangenextdoor_db_password:str = 'akolo000'
    xchangenextdoor_db_server:str = 'localhost'
    xchangenextdoor_db_name:str = 'XChangeNextDoor'
    xchangenextdoor_mnemonic:str
    xchangenextdoor_passphrase:str
    utility_lastblock_keyname:str = "last_block_number"
    utility_users_fee_keyname:str = "users_fee"
    utility_escrow_vendor_fee:str = "escrow_vendor_fee"
    utility_escrow_user_fee:str = "escrow_user_fee"
    utility_vendor_tf_keyname:str = "vendor_withdrawal_fee"
    access_token_expire_minutes:int = 60
    jwt_algorithm:str = 'HS256'
    jwt_secret_key: str = 'd329748e4dce05b3fcf429da2bb8914f240ff0c288897f455ae792f82aee3cc0'
    aes_secret_key:str
    central_wallet_address:str
    central_wallet_key:str
    users_hd_account_val:int = 0
    class Config:
        env_file = "./.env"


settings = Settings()