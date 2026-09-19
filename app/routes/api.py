"""
RESTful API 라우터
스포츠 데이터 조회, 실시간 새로고침, 통합 검색
"""
from fastapi import APIRouter, Query
from app.services.kbo_service import get_kbo_data
from app.services.kleague_service import get_kleague_data
from app.services.overseas_soccer_service import get_overseas_soccer_data
from app.services.mlb_service import get_mlb_data

router = APIRouter(prefix="/api", tags=["Sports API"])


@router.get("/data")
def get_sports_data(sport: str = Query("kbo", description="kbo, kleague, overseas, mlb, all")):
    """선택한 종목의 최신 데이터 반환"""
    if sport == "kbo":
        return get_kbo_data()
    elif sport == "kleague":
        return get_kleague_data()
    elif sport == "overseas":
        return get_overseas_soccer_data()
    elif sport == "mlb":
        return get_mlb_data()
    elif sport == "all":
        return {
            "kbo": get_kbo_data(),
            "kleague": get_kleague_data(),
            "overseas": get_overseas_soccer_data(),
            "mlb": get_mlb_data()
        }
    return {"error": f"알 수 없는 스포츠 종목: {sport}"}


@router.post("/refresh")
def refresh_sports_data(sport: str = Query("all", description="새로고침할 종목")):
    """캐시를 즉시 무효화하고 최신 공식 데이터 크롤링/fetch 후 반환"""
    results = {}
    if sport in ["kbo", "all"]:
        results["kbo"] = get_kbo_data(force_refresh=True)
    if sport in ["kleague", "all"]:
        results["kleague"] = get_kleague_data(force_refresh=True)
    if sport in ["overseas", "all"]:
        results["overseas"] = get_overseas_soccer_data(force_refresh=True)
    if sport in ["mlb", "all"]:
        results["mlb"] = get_mlb_data(force_refresh=True)

    return {
        "success": True,
        "message": f"{sport.upper()} 데이터가 최신 정보로 갱신되었습니다.",
        "data": results.get(sport) if sport != "all" else results
    }


@router.get("/search")
def search_all_sports(q: str = Query(..., min_length=1, description="검색할 선수명 또는 팀명")):
    """4대 스포츠 통합 검색 엔드포인트"""
    query = q.strip().lower()
    matches = {
        "teams": [],
        "players": []
    }

    # 1. KBO 검색
    kbo = get_kbo_data()
    for t in kbo.get("teams", []):
        if query in t.get("team", "").lower() or query in t.get("fullName", "").lower():
            matches["teams"].append({
                "sport": "KBO",
                "sportKey": "kbo",
                "name": t.get("fullName"),
                "shortName": t.get("team"),
                "rank": f"{t.get('rank')}위",
                "info": f"{t.get('win')}승 {t.get('loss')}패 {t.get('draw')}무 (승률 {t.get('rate')})",
                "emblem": t.get("emblem", ""),
                "color": t.get("color")
            })

    for cat in kbo.get("hitters", []) + kbo.get("pitchers", []):
        for p in cat.get("ranks", []):
            if query in p.get("name", "").lower():
                matches["players"].append({
                    "sport": "KBO",
                    "sportKey": "kbo",
                    "category": cat.get("category"),
                    "name": p.get("name"),
                    "team": p.get("team"),
                    "rank": f"{p.get('rank')}위",
                    "value": p.get("value"),
                    "emblem": p.get("teamEmblem", "")
                })

    # 2. K리그 검색
    kl = get_kleague_data()
    for k_key in ["k1", "k2"]:
        k_data = kl.get(k_key, {})
        for t in k_data.get("teams", []):
            if query in t.get("team", "").lower() or query in t.get("fullName", "").lower():
                matches["teams"].append({
                    "sport": k_data.get("name", "K리그"),
                    "sportKey": "kleague",
                    "subKey": k_key,
                    "name": t.get("fullName"),
                    "shortName": t.get("team"),
                    "rank": f"{t.get('rank')}위",
                    "info": f"{t.get('win')}승 {t.get('draw')}무 {t.get('loss')}패 (승점 {t.get('points')})",
                    "emblem": t.get("emblem", ""),
                    "color": t.get("color")
                })
        for cat in k_data.get("players", []):
            for p in cat.get("ranks", []):
                if query in p.get("name", "").lower():
                    matches["players"].append({
                        "sport": k_data.get("name", "K리그"),
                        "sportKey": "kleague",
                        "subKey": k_key,
                        "category": cat.get("category"),
                        "name": p.get("name"),
                        "team": p.get("team"),
                        "rank": f"{p.get('rank')}위",
                        "value": p.get("value"),
                        "emblem": p.get("teamEmblem", "")
                    })

    # 3. 해외축구 검색
    soc = get_overseas_soccer_data()
    for l_key, l_data in soc.get("leagues", {}).items():
        for t in l_data.get("teams", []):
            if query in t.get("team", "").lower() or query in t.get("fullName", "").lower() or query in t.get("teamEng", "").lower():
                matches["teams"].append({
                    "sport": l_data.get("name"),
                    "sportKey": "overseas",
                    "subKey": l_key,
                    "name": t.get("team"),
                    "shortName": t.get("teamEng", t.get("team")),
                    "rank": f"{t.get('rank')}위",
                    "info": f"{t.get('win')}승 {t.get('draw')}무 {t.get('loss')}패 (승점 {t.get('points')})",
                    "emblem": t.get("emblem", ""),
                    "color": l_data.get("color")
                })
        for cat in l_data.get("players", []):
            for p in cat.get("ranks", []):
                if query in p.get("name", "").lower() or query in p.get("team", "").lower():
                    matches["players"].append({
                        "sport": l_data.get("shortName"),
                        "sportKey": "overseas",
                        "subKey": l_key,
                        "category": cat.get("category"),
                        "name": p.get("name"),
                        "team": p.get("team"),
                        "rank": f"{p.get('rank')}위",
                        "value": p.get("value"),
                        "emblem": p.get("teamEmblem", "")
                    })

    # 4. MLB 검색
    mlb = get_mlb_data()
    for t in mlb.get("all_teams", []):
        if query in t.get("team", "").lower() or query in t.get("teamEng", "").lower():
            matches["teams"].append({
                "sport": "MLB",
                "sportKey": "mlb",
                "name": t.get("team"),
                "shortName": t.get("teamEng"),
                "rank": f"{t.get('division')} {t.get('rank')}위",
                "info": f"{t.get('win')}승 {t.get('loss')}패 (승률 {t.get('rate')})",
                "emblem": t.get("emblem", ""),
                "color": t.get("color")
            })

    for cat in mlb.get("hitters", []) + mlb.get("pitchers", []):
        for p in cat.get("ranks", []):
            if query in p.get("name", "").lower():
                matches["players"].append({
                    "sport": "MLB",
                    "sportKey": "mlb",
                    "category": cat.get("category"),
                    "name": p.get("name"),
                    "team": p.get("team"),
                    "rank": f"{p.get('rank')}위",
                    "value": p.get("value"),
                    "emblem": p.get("teamEmblem", "")
                })

    return {
        "query": q,
        "teamCount": len(matches["teams"]),
        "playerCount": len(matches["players"]),
        "results": matches
    }
