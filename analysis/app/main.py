# app/main.py
from fastapi import FastAPI
from app.api.endpoints import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 환경에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router 등록
app.include_router(router, prefix="/api/v1", tags=["Analysis"])

@app.get("/")
async def root():
    return {"message": "LLM Analysis Server is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)