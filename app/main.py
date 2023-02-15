import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .networks.etherium import ether, erc20
from .networks.tron import trx, trc20, asynctrx, asynctrc20
from .routers import tests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

@app.get("/")
def index():
    return {
        "latest eth block": ether.get_latest_block(), 
        'latest trx block': trx.get_latest_block(),
        "erc20 total supply":erc20.get_total_supply(), 
        "erc20 token_name": erc20.get_name(), 
        "erc20 token_symbol": erc20.get_symbol(),
        "trc20 total supply":trc20.get_total_supply(), 
        "trc20 token_name": trc20.get_name(), 
        "trc20 token_symbol": trc20.get_symbol(),
        }

@app.get("/async")
async def asyncindex():
    return {
        'latest trx block': await asynctrx.get_latest_block()
        }

app.include_router(tests.router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host='0.0.0.0', port=8000, reload=True)

