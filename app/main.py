import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def index():
    return {"app": "running"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host='0.0.0.0', port=8000, reload=True)