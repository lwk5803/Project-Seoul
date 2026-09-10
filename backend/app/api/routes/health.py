"""
헬스체크(서버 생존 확인) 라우터.
"서버야, 살아있니?"라고 물어보면 "응, 살아있어"라고 답해주는 창구.
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok"}
