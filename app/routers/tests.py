from fastapi import APIRouter
from ..networks.etherium import ether, erc20
from ..networks.tron import trx, trc20, asynctrx, asynctrc20
from ..schemas import Browser

router = APIRouter(
    prefix="/api/v1/test",
    tags= ["Test Endpoints"]
)

@router.get("/eth/{public_key}")
def get_eth_balance(public_key:str):
    return { "balance" : ether.get_acct_balance(public_key, True)}

@router.get("/erc20/{public_key}")
def get_erc20_balance(public_key:str):
    return { "balance" : erc20.get_acct_balance(public_key, True)}

@router.get("/trx/{public_key}")
def get_trx_balance(public_key:str):
    return { "balance" : trx.get_acct_balance(public_key, True)}

@router.get("/async/trx/{public_key}")
async def asyncget_trx_balance(public_key:str):
    return { "balance" : await asynctrx.get_acct_balance(public_key, True)}

@router.get("/trc20/{public_key}")
def get_trc20_balance(public_key:str):
    return { "balance" : trc20.get_acct_balance(public_key, True)}

@router.get("/async/trc20/{public_key}")
async def asyncget_trc20_balance(public_key:str):
    return { "balance" : await asynctrc20.get_acct_balance(public_key, True)}

@router.post("/create/eth")
def create_eth_account():
    return { "created" : ether.create_account()}

@router.post("/create/trx")
def create_trx_account():
    return { "created" : trx.create_account()}

@router.post("/eth/send")
def send_eth(from_address:str, to_address:str, private_key:str, amount:float):
    return {"transaction hash": ether.send_ether(from_address, to_address, private_key, amount)}

@router.post("/erc20/send")
def send_erc20(from_address:str, to_address:str, private_key:str, amount:float):
    return {"transaction hash": erc20.send_erc20(from_address, to_address, private_key, amount)}

@router.post("/trx/send")
def send_trx(from_address:str, to_address:str, private_key:str, amount:int):
    return {"transaction hash": trx.send_trx(from_address, to_address, private_key, amount)}

@router.post("/async/trx/send")
async def asyncsend_trx(from_address:str, to_address:str, private_key:str, amount:int):
    return {"transaction hash": await asynctrx.send_trx(from_address, to_address, private_key, amount)}

@router.post("/trc20/send")
def send_trc20(from_address:str, to_address:str, private_key:str, amount:float):
    return {"transaction hash": trc20.send_erc20(from_address, to_address, private_key, amount)}

@router.post("/async/trc20/send")
async def asyncsend_trc20(from_address:str, to_address:str, private_key:str, amount:float):
    return {"transaction hash": await asynctrc20.send_erc20(from_address, to_address, private_key, amount)}

@router.post("/browse/sync/trx")
def search_sync_trx(r:Browser):
    return trx.search_block_chain(r.block_number, r.to_block, r.to_address, r.from_address, r.strict, True)

@router.post("/browse/sync/trc20")
def search_sync_trc20(r:Browser):
    return trc20.search_block_chain(r.block_number, r.to_block, r.to_address, r.from_address, r.strict, True)

@router.post("/browse/async/trx")
async def search_async_trx(r:Browser):
    return await asynctrx.search_block_chain(r.block_number, r.to_block, r.to_address, r.from_address, r.strict, True)

@router.post("/browse/async/trc20")
async def search_async_trc20(r:Browser):
    return await asynctrc20.search_block_chain(r.block_number, r.to_block, r.to_address, r.from_address, r.strict, True)

