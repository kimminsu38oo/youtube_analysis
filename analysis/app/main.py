# app/main.py
from fastapi import FastAPI
from app.api.endpoints import router

app = FastAPI()

# Router 등록
app.include_router(router, prefix="/api/v1", tags=["Analysis"])

@app.get("/")
async def root():
    return {"message": "LLM Analysis Server is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)