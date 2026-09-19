"""
HTML 페이지 뷰 라우터
"""
import os
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.services.kbo_service import get_kbo_data
from app.services.kleague_service import get_kleague_data
from app.services.overseas_soccer_service import get_overseas_soccer_data
from app.services.mlb_service import get_mlb_data

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

router = APIRouter(tags=["Page Views"])


@router.get("/")
def home_view(request: Request):
    """메인 통합 스포츠 대시보드 뷰"""
    # 기본 데이터 준비
    kbo_data = get_kbo_data()
    kleague_data = get_kleague_data()
    overseas_data = get_overseas_soccer_data()
    mlb_data = get_mlb_data()

    context = {
        "request": request,
        "active_tab": "kbo",
        "kbo": kbo_data,
        "kleague": kleague_data,
        "overseas": overseas_data,
        "mlb": mlb_data
    }
    return templates.TemplateResponse(request=request, name="index.html", context=context)


@router.get("/{sport}")
def sport_direct_view(request: Request, sport: str):
    """스포츠 종목별 직링 뷰 (/kbo, /kleague, /overseas, /mlb)"""
    sport_key = sport.lower()
    if sport_key not in ["kbo", "kleague", "overseas", "mlb"]:
        sport_key = "kbo"

    kbo_data = get_kbo_data()
    kleague_data = get_kleague_data()
    overseas_data = get_overseas_soccer_data()
    mlb_data = get_mlb_data()

    context = {
        "request": request,
        "active_tab": sport_key,
        "kbo": kbo_data,
        "kleague": kleague_data,
        "overseas": overseas_data,
        "mlb": mlb_data
    }
    return templates.TemplateResponse(request=request, name="index.html", context=context)
