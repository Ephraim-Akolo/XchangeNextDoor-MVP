from pydantic import BaseSettings

class Settings(BaseSettings):
    web3_provider_uri:str


settings = Settings()