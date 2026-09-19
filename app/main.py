"""
스포츠 올인원 웹 대시보드 - FastAPI 애플리케이션 진입점
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.routes.api import router as api_router
from app.routes.pages import router as pages_router
from app.services.kbo_service import get_kbo_data
from app.services.kleague_service import get_kleague_data
from app.services.overseas_soccer_service import get_overseas_soccer_data
from app.services.mlb_service import get_mlb_data

BASE_DIR = os.path.dirname(__file__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """서버 시작 시 데이터 캐시 상태 점검 및 사전 로드"""
    print("=" * 60)
    print("🚀 스포츠 올인원 대시보드 서버를 시작합니다.")
    print("📊 데이터 캐시 상태 확인 중...")
    try:
        get_kbo_data()
        get_kleague_data()
        get_overseas_soccer_data()
        get_mlb_data()
        print("✅ 모든 스포츠 데이터 캐시 준비 완료!")
    except Exception as e:
        print(f"⚠️ 초기 데이터 캐시 로드 중 알림: {e}")
    print("=" * 60)
    yield
    print("🛑 서버가 정상적으로 종료되었습니다.")


app = FastAPI(
    title="SPORTS HUB - 실시간 스포츠 종합 순위 & 기록 대시보드",
    description="K리그, 해외축구(EPL, 라리가 등), KBO 한국야구, MLB 메이저리그 종합 순위 및 개인기록 웹페이지",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙
static_dir = os.path.join(BASE_DIR, "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 라우터 등록
app.include_router(api_router)
app.include_router(pages_router)
