"""
FastAPI 진입점.
이 파일을 실행하면 실제로 웹 서버가 켜진다.
"""
from fastapi import FastAPI

from app.api.routes.health import router as health_router

app = FastAPI(title="Project-Seoul API")

app.include_router(health_router)


@app.get("/")
def root():
    return {"message": "Project-Seoul 백엔드가 실행 중입니다."}
