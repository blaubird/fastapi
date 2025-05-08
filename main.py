from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health():
    return {"ok": True}

# временный корневой маршрут, чтобы увидеть «Hello»
@app.get("/")
async def index():
    return {"message": "Hello from Luminiteq!"}
