import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .networks.etherium import ether, erc20

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

app.on_event("startup")
def on_startup():
    pass

@app.get("/")
def index():
    return {"latest eth block": ether.get_latest_block(), "erc20 total supply":erc20.get_total_supply(), "token_name": erc20.get_name(), "token_symbol": erc20.get_symbol()}

@app.get("/eth/{public_key}")
def get_eth_balance(public_key:str):
    return { "balance" : ether.get_acct_balance(public_key, True)}

@app.post("/create/eth")
def create_eth_account():
    return { "created" : ether.create_account()}

@app.get("/ecr20/{public_key}")
def get_ecr20_balance(public_key:str):
    return { "balance" : erc20.get_acct_balance(public_key, True)}

@app.post("/eth/send")
def send_eth(from_address:str, to_address:str, private_key:str, amount:float):
    return {"transaction hash": ether.send_ether(from_address, to_address, private_key, amount)}

@app.post("/ec20/send")
def send_eth(from_address:str, to_address:str, private_key:str, amount:float):
    return {"transaction hash": erc20.send_erc20(from_address, to_address, private_key, amount)}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host='0.0.0.0', port=8000, reload=True)