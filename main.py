from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health():
    return {"ok": True}

@app.get("/")
async def index():
    return {"message": "Hello from Luminiteq!"}
