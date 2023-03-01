import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from .networks.etherium import ether, erc20
import logging
from .routers import tests, auth, users, backend
from .dbconnect import Base, engine

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

Base.metadata.create_all(engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(backend.router)
app.include_router(tests.router)

@app.get("/")
def index():
    return {"status": "running!"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host='0.0.0.0', port=8000, reload=True)

