"""
K리그 (K리그1, K리그2) 데이터 서비스 모듈
K리그 공식 데이터 포털 및 공식 사이트 연동
"""
import os
import json
import re
from datetime import datetime, timezone, timedelta
import requests
from bs4 import BeautifulSoup

KST = timezone(timedelta(hours=9))

def get_now_kst():
    """한국 표준시(KST, UTC+9) 기준 datetime 반환 (서버 타임존 무관)"""
    return datetime.now(timezone.utc).astimezone(KST).replace(tzinfo=None)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/json; charset=utf-8"
}

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)
CACHE_FILE = os.path.join(CACHE_DIR, "kleague_data.json")

# K리그 주요 구단 대표 컬러 및 엠블럼 (공식 CloudFront CDN 사용)
KLEAGUE_TEAMS = {
    "울산": {
        "teamId": "K01",
        "fullName": "울산 HD FC",
        "shortName": "울산",
        "color": "#002B49",
        "accent": "#F5A623",
        "emblem": "https://www.kleague.com/assets/images/emblem/emblem_K01.png"
    },
    "수원삼성": {
        "teamId": "K02",
        "fullName": "수원 삼성 블루윙즈",
        "shortName": "수원삼성",
        "color": "#0055A5",
        "accent": "#E31B23",
        "emblem": "https://www.kleague.com/assets/images/emblem/emblem_K02.png"
    },
    "수원": {
        "teamId": "K02",
        "fullName": "수원 삼성 블루윙즈",
        "shortName": "수원삼성",
        "color": "#0055A5",
        "accent": "#E31B23",
        "emblem": "https://www.kleague.com/assets/images/emblem/emblem_K02.png"
    },
    "포항": {
        "teamId": "K03",
        "fullName": "포항 스틸러스",
        "shortName": "포항",
        "color": "#E31B23",
        "accent": "#000000",
        "emblem": "https://www.kleague.com/assets/images/emblem/emblem_K03.png"
    },
    "제주": {
        "teamId": "K04",
        "fullName": "제주 SK FC",
        "shortName": "제주",
        "color": "#FF671F",
        "accent": "#C8102E",
        "emblem": "https://www.kleague.com/assets/images/emblem/emblem_K04.png"
    },
    "전북": {
        "teamId": "K05",
        "fullName": "전북 현대 모터스",
        "shortName": "전북",
        "color": "#00552E",
        "accent": "#A3D867",
        "emblem": "https://www.kleague.com/assets/images/emblem/emblem_K05.png"
    },
    "부산": {
        "teamId": "K06",
        "fullName": "부산 아이파크",
        "shortName": "부산",
        "color": "#C8102E",
        "accent": "#FFFFFF",
        "emblem": "https://www.kleague.com/assets/images/emblem/emblem_K06.png"
    },
    "전남": {
        "teamId": "K07",
        "fullName": "전남 드래곤즈",
        "shortName": "전남",
        "color": "#FFC72C",
        "accent": "#000000",
        "emblem": "https://www.kleague.com/assets/images/emblem/emblem_K07.png"
    },
    "성남": {
        "teamId": "K08",
        "fullName": "성남 FC",
        "shortName": "성남",
        "color": "#1C1C1C",
        "accent": "#A7A8AA",
        "emblem": "https://www.kleague.com/assets/images/emblem/emblem_K08.png"
    },
    "서울": {
        "teamId": "K09",
        "fullName": "FC 서울",
        "shortName": "서울",
        "color": "#C8102E",
        "accent": "#000000",
        "emblem": "https://www.kleague.com/assets/images/emblem/emblem_K09.png"
    },
    "대전": {
        "teamId": "K10",
        "fullName": "대전 하나 시티즌",
        "shortName": "대전",
        "color": "#006738",
        "accent": "#862633",
        "emblem": "https://www.kleague.com/assets/images/emblem/emblem_K10.png"
    },
    "대구": {
        "teamId": "K17",
        "fullName": "대구 FC",
        "shortName": "대구",
        "color": "#76C5EE",
        "accent": "#142548",
        "emblem": "https://www.kleague.com/assets/images/emblem/emblem_K17.png"
    },
    "인천": {
        "teamId": "K18",
        "fullName": "인천 유나이티드",
        "shortName": "인천",
        "color": "#0047AB",
        "accent": "#000000",
        "emblem": "https://www.kleague.com/assets/images/emblem/emblem_K18.png"
    },
    "경남": {
        "teamId": "K20",
        "fullName": "경남 FC",
        "shortName": "경남",
        "color": "#C8102E",
        "accent": "#FFFFFF",
        "emblem": "https://www.kleague.com/assets/images/emblem/emblem_K20.png"
    },
    "강원": {
        "teamId": "K21",
        "fullName": "강원 FC",
        "shortName": "강원",
        "color": "#E55C00",
        "accent": "#004534",
        "emblem": "https://www.kleague.com/assets/images/emblem/emblem_K21.png"
    },
    "광주": {
        "teamId": "K22",
        "fullName": "광주 FC",
        "shortName": "광주",
        "color": "#FDB913",
        "accent": "#C8102E",
        "emblem": "https://www.kleague.com/assets/images/emblem/emblem_K22.png"
    },
    "부천": {
        "teamId": "K26",
        "fullName": "부천 FC 1995",
        "shortName": "부천",
        "color": "#BA0C2F",
        "accent": "#000000",
        "emblem": "https://www.kleague.com/assets/images/emblem/emblem_K26.png"
    },
    "안양": {
        "teamId": "K27",
        "fullName": "FC 안양",
        "shortName": "안양",
        "color": "#532E85",
        "accent": "#E8AF27",
        "emblem": "https://www.kleague.com/assets/images/emblem/emblem_K27.png"
    },
    "수원FC": {
        "teamId": "K29",
        "fullName": "수원 FC",
        "shortName": "수원FC",
        "color": "#002B49",
        "accent": "#E31B23",
        "emblem": "https://www.kleague.com/assets/images/emblem/emblem_K29.png"
    },
    "서울E": {
        "teamId": "K31",
        "fullName": "서울 이랜드 FC",
        "shortName": "서울E",
        "color": "#00205B",
        "accent": "#A7A8AA",
        "emblem": "https://www.kleague.com/assets/images/emblem/emblem_K31.png"
    },
    "안산": {
        "teamId": "K32",
        "fullName": "안산 그리너스 FC",
        "shortName": "안산",
        "color": "#006738",
        "accent": "#FDB913",
        "emblem": "https://www.kleague.com/assets/images/emblem/emblem_K32.png"
    },
    "충남아산": {
        "teamId": "K34",
        "fullName": "충남 아산 FC",
        "shortName": "충남아산",
        "color": "#003A70",
        "accent": "#FDB913",
        "emblem": "https://www.kleague.com/assets/images/emblem/emblem_K34.png"
    },
    "김천": {
        "teamId": "K35",
        "fullName": "김천 상무 FC",
        "shortName": "김천",
        "color": "#BA0C2F",
        "accent": "#0C2340",
        "emblem": "https://www.kleague.com/assets/images/emblem/emblem_K35.png"
    },
    "김포": {
        "teamId": "K36",
        "fullName": "김포 FC",
        "shortName": "김포",
        "color": "#0047AB",
        "accent": "#FFC72C",
        "emblem": "https://www.kleague.com/assets/images/emblem/emblem_K36.png"
    },
    "충북청주": {
        "teamId": "K37",
        "fullName": "충북 청주 FC",
        "shortName": "충북청주",
        "color": "#002B49",
        "accent": "#C8102E",
        "emblem": "https://www.kleague.com/assets/images/emblem/emblem_K37.png"
    },
    "천안": {
        "teamId": "K38",
        "fullName": "천안 시티 FC",
        "shortName": "천안",
        "color": "#76C5EE",
        "accent": "#002B49",
        "emblem": "https://www.kleague.com/assets/images/emblem/emblem_K38.png"
    },
    "화성": {
        "teamId": "K39",
        "fullName": "화성 FC",
        "shortName": "화성",
        "color": "#E31B23",
        "accent": "#002B49",
        "emblem": "https://www.kleague.com/assets/images/emblem/emblem_K39.png"
    },
    "파주": {
        "teamId": "K40",
        "fullName": "파주 프런티어 FC",
        "shortName": "파주",
        "color": "#0047AB",
        "accent": "#FF671F",
        "emblem": "https://www.kleague.com/assets/images/emblem/emblem_K40.png"
    },
    "김해": {
        "teamId": "K41",
        "fullName": "김해시청 축구단",
        "shortName": "김해",
        "color": "#006738",
        "accent": "#FDB913",
        "emblem": "https://www.kleague.com/assets/images/emblem/emblem_K41.png"
    },
    "용인": {
        "teamId": "K42",
        "fullName": "용인 FC",
        "shortName": "용인",
        "color": "#002B49",
        "accent": "#E31B23",
        "emblem": "https://www.kleague.com/assets/images/emblem/emblem_K42.png"
    }
}


def get_team_meta(team_name, team_id=None):
    """구단 메타데이터(색상, 엠블럼 등) 조회 (공식 CDN 엠블럼 매핑)"""
    if not team_name:
        emblem = f"https://www.kleague.com/assets/images/emblem/emblem_{team_id}.png" if team_id else ""
        return {"fullName": "", "shortName": "", "color": "#334155", "accent": "#64748b", "emblem": emblem}
    
    # 1. team_id가 전달된 경우 해당 엠블럼 우선 확보
    official_emblem = f"https://www.kleague.com/assets/images/emblem/emblem_{team_id}.png" if team_id else None

    # 2. 수원삼성 / 수원FC 특수 매핑
    meta = None
    if team_name in ["수원삼성", "수원 삼성", "수원"]:
        meta = dict(KLEAGUE_TEAMS.get("수원삼성", KLEAGUE_TEAMS.get("수원")))
    elif "수원FC" in team_name or "수원 FC" in team_name:
        meta = dict(KLEAGUE_TEAMS.get("수원FC"))
    elif team_name in KLEAGUE_TEAMS:
        meta = dict(KLEAGUE_TEAMS[team_name])
    else:
        # 부분 일치 검사
        sorted_keys = sorted(KLEAGUE_TEAMS.keys(), key=len, reverse=True)
        for key in sorted_keys:
            if key in team_name:
                meta = dict(KLEAGUE_TEAMS[key])
                break
        if not meta:
            for key in sorted_keys:
                if team_name in key and len(team_name) >= 2:
                    meta = dict(KLEAGUE_TEAMS[key])
                    break

    if meta:
        if official_emblem:
            meta["emblem"] = official_emblem
        return meta

    return {
        "fullName": team_name,
        "shortName": team_name,
        "color": "#334155",
        "accent": "#64748b",
        "emblem": official_emblem or ""
    }


def fetch_kleague_standings(league_id=1, year=2026):
    """K리그 팀 순위 조회"""
    url = f"https://www.kleague.com/record/teamRank.do?leagueId={league_id}&year={year}&stadium=all&recordType=basic"
    resp = requests.post(url, headers=HEADERS, timeout=10)
    
    # 2026 데이터가 없으면 전년도 시도
    if resp.status_code == 200:
        data = resp.json()
        ranks = data.get("data", {}).get("teamRank", [])
        if ranks:
            return _format_kleague_ranks(ranks)
            
    # Fallback to previous year
    url_fallback = f"https://www.kleague.com/record/teamRank.do?leagueId={league_id}&year={year-1}&stadium=all&recordType=basic"
    resp = requests.post(url_fallback, headers=HEADERS, timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        ranks = data.get("data", {}).get("teamRank", [])
        return _format_kleague_ranks(ranks)
    return []


def _format_kleague_ranks(ranks):
    result = []
    for r in ranks:
        t_name = r.get("teamName", "")
        t_id = r.get("teamId")
        # '수원'으로 등록된 경우 팬들이 식별하기 쉽도록 '수원삼성'으로 통일
        display_team = "수원삼성" if t_name == "수원" else t_name
        meta = get_team_meta(t_name, team_id=t_id)
        
        recent_games = []
        for i in range(1, 7):
            g = r.get(f"game{i:02d}")
            if g:
                recent_games.append(g)
                
        result.append({
            "rank": r.get("rank"),
            "teamId": r.get("teamId"),
            "team": display_team,
            "fullName": meta["fullName"],
            "color": meta["color"],
            "accent": meta["accent"],
            "emblem": meta["emblem"],
            "games": r.get("gameCount", 0),
            "points": r.get("gainPoint", 0),
            "win": r.get("winCnt", 0),
            "draw": r.get("tieCnt", 0),
            "loss": r.get("lossCnt", 0),
            "goalsFor": r.get("gainGoal", 0),
            "goalsAgainst": r.get("lossGoal", 0),
            "goalDiff": r.get("gapCnt", 0),
            "recent": recent_games[-5:] if recent_games else [],
            "homepage": r.get("homepage", "")
        })
    return result


def fetch_kleague_player_rankings(league_id=1, year=2026):
    """K리그 주요 개인 순위 조회 (득점, 도움, 공격포인트)"""
    categories = [
        {"type": "GOAL", "title": "득점 순위 (Top Scorers)", "icon": "fa-futbol"},
        {"type": "ASSIST", "title": "도움 순위 (Top Assists)", "icon": "fa-hands-helping"},
        {"type": "AP", "title": "공격포인트 순위 (Attacking Points)", "icon": "fa-chart-line"},
        {"type": "CLEAN", "title": "무실점 경기 (Clean Sheets)", "icon": "fa-shield-halved"}
    ]
    
    results = []
    for cat in categories:
        records = []
        for y in [year, year - 1]:
            payload = {"year": str(y), "leagueId": str(league_id), "recordType": cat["type"]}
            try:
                resp = requests.post("https://www.kleague.com/record/rankSort.do", json=payload, headers=HEADERS, timeout=8)
                if resp.status_code == 200:
                    data = resp.json()
                    plist = data.get("data", {}).get("list", [])
                    if plist:
                        for p in plist[:10]:
                            t_name = p.get("teamName", "")
                            meta = get_team_meta(t_name)
                            
                            val = ""
                            if cat["type"] == "GOAL":
                                val = f"{p.get('goalQty', 0)}골 ({p.get('gameQty', 0)}경기)"
                            elif cat["type"] == "ASSIST":
                                val = f"{p.get('assistQty', 0)}도움 ({p.get('gameQty', 0)}경기)"
                            elif cat["type"] == "AP":
                                val = f"{p.get('apQty', 0)}P ({p.get('goalQty', 0)}골 {p.get('assistQty', 0)}도움)"
                            elif cat["type"] == "CLEAN":
                                val = f"{p.get('clQty', 0)}경기 무실점"

                            records.append({
                                "rank": p.get("rank"),
                                "name": p.get("name"),
                                "playerId": p.get("playerId"),
                                "team": t_name,
                                "teamColor": meta["color"],
                                "teamEmblem": meta["emblem"],
                                "backNo": p.get("backNo"),
                                "value": val,
                                "games": p.get("gameQty"),
                                "perGame": p.get("qtyPerGame")
                            })
                        break
            except Exception as e:
                print(f"K리그 선수 랭킹 에러 ({cat['type']}): {e}")

        results.append({
            "category": cat["title"],
            "type": cat["type"],
            "icon": cat["icon"],
            "first_player": records[0] if records else None,
            "ranks": records
        })
    return results


def build_kleague_team_hub(teams, player_categories):
    """K리그 구단별 순위 및 선수 몰아보기 데이터 생성"""
    hub = {}
    for t in teams:
        hub[t["team"]] = {
            "team": t,
            "players": []
        }

    for cat in player_categories:
        for p in cat["ranks"]:
            t_name = p["team"]
            if t_name in hub:
                hub[t_name]["players"].append({
                    "category": cat["category"],
                    "rank": p["rank"],
                    "name": p["name"],
                    "value": p["value"],
                    "backNo": p.get("backNo")
                })
    return hub


def find_kleague_team_info(team_name, team_id=None):
    """팀 이름으로 엠블럼 및 대표 색상 찾기"""
    if not team_name and not team_id:
        return {"color": "#1f2937", "emblem": ""}
    return get_team_meta(team_name, team_id=team_id)


def fetch_naver_kfootball_map():
    """네이버 스포츠 kfootball API를 통해 실시간 경기, 스코어, gameId 매핑 조회"""
    naver_map = {}
    try:
        now = get_now_kst()
        from_date = (now - timedelta(days=2)).strftime("%Y-%m-%d")
        to_date = (now + timedelta(days=2)).strftime("%Y-%m-%d")
        url = f"https://api-gw.sports.naver.com/schedule/games?fields=basic%2CsuperOrganId&fromDate={from_date}&toDate={to_date}&upperCategoryId=kfootball&size=100"
        r = requests.get(url, headers=HEADERS, timeout=6)
        if r.status_code == 200:
            games = r.json().get("result", {}).get("games", [])
            for g in games:
                home = g.get("homeTeamName", "").strip()
                away = g.get("awayTeamName", "").strip()
                if home and away:
                    naver_map[(home, away)] = g
                    # 앞 2글자 또는 단축명 매핑
                    h_short = home[:2] if len(home) >= 2 else home
                    a_short = away[:2] if len(away) >= 2 else away
                    naver_map[(h_short, a_short)] = g
    except Exception as e:
        print(f"네이버 K리그 API 조회 오류: {e}")
    return naver_map


def fetch_kleague_recent_matches(league_id=1):
    """K리그 공식 경기 일정/결과 (최근 종료 경기, 금주 예정 경기, 실시간 LIVE 스코어)"""
    try:
        # 네이버 실시간 K리그 경기 맵 조회
        naver_map = fetch_naver_kfootball_map()

        url = "https://www.kleague.com/getScheduleList.do"
        headers = {
            **HEADERS,
            "Referer": "https://www.kleague.com/schedule.do"
        }
        now = get_now_kst()
        year = now.year if now.year <= 2026 else 2026
        month = f"{now.month:02d}"

        payload = {
            "leagueId": league_id,
            "year": str(year),
            "month": month
        }
        r = requests.post(url, headers=headers, json=payload, timeout=8)
        data = r.json().get("data", {})
        sched_list = data.get("scheduleList", [])

        # 경기가 없으면 이전 달로 재시도
        if not sched_list:
            payload["month"] = "09"
            payload["year"] = "2026"
            r = requests.post(url, headers=headers, json=payload, timeout=8)
            data = r.json().get("data", {})
            sched_list = data.get("scheduleList", [])

        matches = []
        for s in sched_list:
            home_name = s.get("homeTeamName", "").strip()
            away_name = s.get("awayTeamName", "").strip()
            home_id = s.get("homeTeam")
            away_id = s.get("awayTeam")

            # K리그2에서 '수원'은 수원삼성 블루윙즈이므로 명확하게 표기
            if league_id == 2:
                if home_name == "수원":
                    home_name = "수원삼성"
                if away_name == "수원":
                    away_name = "수원삼성"

            home_goal = s.get("homeGoal")
            away_goal = s.get("awayGoal")
            end_yn = s.get("endYn") == "Y"
            game_status_code = str(s.get("gameStatus") or "").strip().upper()

            # 네이버 실시간 정보 매핑 확인
            naver_game = naver_map.get((home_name, away_name))
            if not naver_game:
                naver_game = naver_map.get((home_name[:2], away_name[:2]))

            naver_status = naver_game.get("statusCode", "") if naver_game else ""
            naver_info = naver_game.get("statusInfo", "") if naver_game else ""
            naver_game_id = naver_game.get("gameId", "") if naver_game else ""

            # 네이버 실시간 스코어 우선 반영
            if naver_game:
                if naver_game.get("homeTeamScore") is not None:
                    home_goal = naver_game.get("homeTeamScore")
                if naver_game.get("awayTeamScore") is not None:
                    away_goal = naver_game.get("awayTeamScore")

            # 상태 판별 (LIVE, 종료, 예정)
            # K리그 공식 사이트 상태코드: 1S xx (전반), 2S xx (후반), HT (하프타임), FE (경기종료)
            is_finished = end_yn or game_status_code.startswith("FE") or "종료" in game_status_code or naver_status in ["RESULT", "END"] or "종료" in naver_info
            
            # 라이브 판별
            is_live_code = any(code in game_status_code for code in ["1S", "2S", "HT", "ET", "PK", "1H", "2H", "ING", "LIVE", "PLAY", "1E", "2E"])
            is_naver_live = naver_status in ["STARTED", "ING", "PROGRESS", "PLAY"] or ("전반" in naver_info or "후반" in naver_info or "하프타임" in naver_info)
            is_live = not is_finished and (is_live_code or is_naver_live)

            # 방어 로직: 경기 날짜가 과거이거나 경기 시작 시간으로부터 3.5시간 이상 경과한 경기는 절대 LIVE로 남지 않도록 차단
            game_date_str = (s.get("gameDate") or "").replace(".", "-")[:10]
            game_time_str = s.get("gameTime") or ""
            if is_live:
                if game_date_str and game_date_str < now.strftime("%Y-%m-%d"):
                    is_live = False
                    is_finished = True
                elif game_date_str and game_time_str:
                    try:
                        g_datetime_obj = datetime.strptime(f"{game_date_str} {game_time_str[:5]}", "%Y-%m-%d %H:%M")
                        if (now - g_datetime_obj).total_seconds() > 3.5 * 3600:
                            is_live = False
                            is_finished = True
                    except Exception:
                        pass

            is_upcoming = not is_finished and not is_live

            if is_live:
                status_label = "LIVE"
                if naver_info and ("전반" in naver_info or "후반" in naver_info or "하프" in naver_info or "'" in naver_info):
                    status_info = naver_info
                elif "HT" in game_status_code:
                    status_info = "하프타임 (HT)"
                elif "1S" in game_status_code or "1H" in game_status_code:
                    parts = game_status_code.split()
                    min_str = parts[1] if len(parts) > 1 and parts[1].isdigit() else ""
                    status_info = f"전반 {min_str}분" if min_str else "전반 진행중"
                elif "2S" in game_status_code or "2H" in game_status_code:
                    parts = game_status_code.split()
                    min_str = parts[1] if len(parts) > 1 and parts[1].isdigit() else ""
                    status_info = f"후반 {min_str}분" if min_str else "후반 진행중"
                elif "ET" in game_status_code:
                    status_info = "연장 진행중"
                elif "PK" in game_status_code:
                    status_info = "승부차기"
                else:
                    status_info = naver_info or "LIVE 진행중"
            elif is_finished:
                status_label = "종료"
                status_info = "경기종료"
            else:
                status_label = "예정"
                weekday_str = s.get('weekdayShort', '')
                time_str = s.get('gameTime', '')
                status_info = f"금주 예정 ({time_str})" if time_str else "금주 예정"

            home_info = find_kleague_team_info(home_name, team_id=home_id)
            away_info = find_kleague_team_info(away_name, team_id=away_id)

            home_win = (home_goal is not None and away_goal is not None and home_goal > away_goal)
            away_win = (home_goal is not None and away_goal is not None and away_goal > home_goal)

            matches.append({
                "game_id": naver_game_id,
                "naver_relay_url": f"https://m.sports.naver.com/game/{naver_game_id}/relay" if naver_game_id else "https://m.sports.naver.com/kleague/schedule/index",
                "game_date": s.get("gameDate", ""),
                "game_time": s.get("gameTime", ""),
                "weekday": s.get("weekdayShort", ""),
                "round": f"{s.get('roundId', '')}R" if s.get('roundId') else "",
                "league_name": s.get("meetName", f"K리그 {league_id}"),
                "home_team": home_name,
                "home_emblem": home_info.get("emblem", ""),
                "home_color": home_info.get("color", "#1f2937"),
                "home_goal": home_goal if (is_finished or is_live) else "-",
                "home_win": home_win if is_finished else False,
                "away_team": away_name,
                "away_emblem": away_info.get("emblem", ""),
                "away_color": away_info.get("color", "#1f2937"),
                "away_goal": away_goal if (is_finished or is_live) else "-",
                "away_win": away_win if is_finished else False,
                "field_name": s.get("fieldName", "") or s.get("fieldNameFull", ""),
                "broadcast": s.get("broadcastName", "").replace("//", " / "),
                "status": status_label,
                "status_info": status_info,
                "is_live": is_live,
                "is_upcoming": is_upcoming,
                "is_finished": is_finished
            })

        # 금주 및 지난주 날짜 범위 계산
        this_week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        this_week_end = this_week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        last_week_start = this_week_start - timedelta(days=7)

        def parse_match_date(m):
            raw = (m.get("game_date") or "").replace(".", "-")[:10]
            try:
                return datetime.strptime(raw, "%Y-%m-%d")
            except Exception:
                return None

        # 1) 라이브 경기 (현재 진행 중)
        live_games = [m for m in matches if m["is_live"]]

        # 2) 예정 경기: 금주 일요일까지 예정된 경기만 (다음 주 경기 제외)
        upcoming_games = []
        for m in matches:
            if m["is_upcoming"]:
                dt = parse_match_date(m)
                if dt is None or dt <= this_week_end:
                    upcoming_games.append(m)
        upcoming_games.sort(key=lambda x: (x.get("game_date", ""), x.get("game_time", "")))

        # 3) 지난 경기 (종료 경기): 지난주 월요일 이후 종료된 경기만 (지지난주 이전 경기 제외)
        finished_games = []
        for m in matches:
            if m["is_finished"]:
                dt = parse_match_date(m)
                if dt is None or dt >= last_week_start:
                    finished_games.append(m)
        finished_games.sort(key=lambda x: (x.get("game_date", ""), x.get("game_time", "")), reverse=True)

        return live_games + upcoming_games + finished_games[:8]
    except Exception as e:
        print(f"K리그 {league_id} 경기 결과 조회 에러: {e}")
        return []


def fetch_kleague_highlights(league_id=None):
    """K리그 공식 하이라이트 영상 목록 크롤링 (K리그1, K리그2 분리 지원)"""
    default_k1_highlights = [
        {
            "title": "[30분 하이라이트] 하나은행 K리그1 2026 29R 전북 vs 서울 (2026-09-12)",
            "match": "전북 vs 서울",
            "score": "2 : 1",
            "date": "2026.09.12",
            "youtube_id": "8bYANXGyqQs",
            "embed_url": "https://www.youtube.com/embed/8bYANXGyqQs",
            "thumbnail": "https://i.ytimg.com/vi/8bYANXGyqQs/sddefault.jpg",
            "source": "K리그1 공식"
        },
        {
            "title": "[30분 하이라이트] 하나은행 K리그1 2026 29R 대전 vs 포항 (2026-09-12)",
            "match": "대전 vs 포항",
            "score": "1 : 0",
            "date": "2026.09.12",
            "youtube_id": "ITVOUqYZgiw",
            "embed_url": "https://www.youtube.com/embed/ITVOUqYZgiw",
            "thumbnail": "https://i.ytimg.com/vi/ITVOUqYZgiw/sddefault.jpg",
            "source": "K리그1 공식"
        },
        {
            "title": "[30분 하이라이트] 하나은행 K리그1 2026 29R 김천 vs 강원 (2026-09-13)",
            "match": "김천 vs 강원",
            "score": "2 : 2",
            "date": "2026.09.13",
            "youtube_id": "1dr7FH4YqBo",
            "embed_url": "https://www.youtube.com/embed/1dr7FH4YqBo",
            "thumbnail": "https://i.ytimg.com/vi/1dr7FH4YqBo/sddefault.jpg",
            "source": "K리그1 공식"
        },
        {
            "title": "[30분 하이라이트] 하나은행 K리그1 2026 29R 광주 vs 안양 (2026-09-13)",
            "match": "광주 vs 안양",
            "score": "1 : 1",
            "date": "2026.09.13",
            "youtube_id": "QHq4QJ_R0E0",
            "embed_url": "https://www.youtube.com/embed/QHq4QJ_R0E0",
            "thumbnail": "https://i.ytimg.com/vi/QHq4QJ_R0E0/sddefault.jpg",
            "source": "K리그1 공식"
        }
    ]

    default_k2_highlights = [
        {
            "title": "[30분 하이라이트] 하나은행 K리그2 2026 26R 수원삼성 vs 성남 FC (2026-09-07)",
            "match": "수원삼성 vs 성남",
            "score": "2 : 1",
            "date": "2026.09.07",
            "youtube_id": "HMDw7xoKcug",
            "embed_url": "https://www.youtube.com/embed/HMDw7xoKcug",
            "thumbnail": "https://i.ytimg.com/vi/HMDw7xoKcug/sddefault.jpg",
            "source": "K리그2 공식"
        },
        {
            "title": "[30분 하이라이트] 하나은행 K리그2 2026 26R 부산 vs 김해 (2026-09-13)",
            "match": "부산 vs 김해",
            "score": "2 : 0",
            "date": "2026.09.13",
            "youtube_id": "qwUW8Lop0Ws",
            "embed_url": "https://www.youtube.com/embed/qwUW8Lop0Ws",
            "thumbnail": "https://i.ytimg.com/vi/qwUW8Lop0Ws/sddefault.jpg",
            "source": "K리그2 공식"
        },
        {
            "title": "[30분 하이라이트] 하나은행 K리그2 2026 26R 전남 vs 김포 (2026-09-13)",
            "match": "전남 vs 김포",
            "score": "1 : 1",
            "date": "2026.09.13",
            "youtube_id": "QMquI2uWGiU",
            "embed_url": "https://www.youtube.com/embed/QMquI2uWGiU",
            "thumbnail": "https://i.ytimg.com/vi/QMquI2uWGiU/sddefault.jpg",
            "source": "K리그2 공식"
        },
        {
            "title": "[30분 하이라이트] 하나은행 K리그2 2026 26R 충남아산 vs 충북청주 (2026-09-12)",
            "match": "충남아산 vs 충북청주",
            "score": "2 : 1",
            "date": "2026.09.12",
            "youtube_id": "eCURQpehjlQ",
            "embed_url": "https://www.youtube.com/embed/eCURQpehjlQ",
            "thumbnail": "https://i.ytimg.com/vi/eCURQpehjlQ/sddefault.jpg",
            "source": "K리그2 공식"
        },
        {
            "title": "[30분 하이라이트] 하나은행 K리그2 2026 26R 안산 vs 화성 (2026-09-12)",
            "match": "안산 vs 화성",
            "score": "0 : 0",
            "date": "2026.09.12",
            "youtube_id": "B23-DvGY214",
            "embed_url": "https://www.youtube.com/embed/B23-DvGY214",
            "thumbnail": "https://i.ytimg.com/vi/B23-DvGY214/sddefault.jpg",
            "source": "K리그2 공식"
        },
        {
            "title": "[30분 하이라이트] 하나은행 K리그2 2026 25R 서울 이랜드 vs 수원삼성 (2026-08-31)",
            "match": "서울E vs 수원삼성",
            "score": "1 : 2",
            "date": "2026.08.31",
            "youtube_id": "zLR7H9tXNOk",
            "embed_url": "https://www.youtube.com/embed/zLR7H9tXNOk",
            "thumbnail": "https://i.ytimg.com/vi/zLR7H9tXNOk/sddefault.jpg",
            "source": "K리그2 공식"
        }
    ]

    try:
        url = "https://www.kleague.com/video_list.do?category=highlight"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=6)
        soup = BeautifulSoup(r.text, "html.parser")
        links = soup.find_all("a", href=lambda x: x and "video_view.do" in x)
        if not links:
            if league_id == 2:
                return default_k2_highlights
            elif league_id == 1:
                return default_k1_highlights
            return default_k1_highlights + default_k2_highlights

        crawled = []
        for a in links[:20]:
            img = a.find("img")
            img_src = img["src"] if img else ""
            m = re.search(r"/vi/([a-zA-Z0-9_-]+)/", img_src)
            yt_id = m.group(1) if m else ""

            raw_text = a.text.strip().replace("\n", " ")
            clean_title = re.sub(r"^highlight\s*", "", raw_text)
            clean_title = re.sub(r"\s*\d{4}\.\d{2}\.\d{2}조회수.*$", "", clean_title)
            clean_title = re.sub(r"\s+", " ", clean_title).strip()

            date_m = re.search(r"(\d{4}\.\d{2}\.\d{2})", raw_text)
            date_str = date_m.group(1) if date_m else ""

            if yt_id:
                # K1 / K2 리그 판별
                is_k2 = "K리그2" in clean_title or "k리그2" in clean_title or any(t in clean_title for t in ["수원삼성", "부산", "성남", "부천", "전남", "경남", "서울E", "충북청주", "충남아산", "김포", "안산", "천안", "화성", "김해", "용인"])
                source_label = "K리그2 공식" if is_k2 else "K리그1 공식"

                if is_k2:
                    # K2에서 단독 '수원' 표기는 수원삼성을 의미하므로 명확화
                    clean_title = re.sub(r'(?<=\s)수원(?=\s|\(|$)', '수원삼성', clean_title)
                
                crawled.append({
                    "title": clean_title if clean_title else "K리그 공식 하이라이트",
                    "match": clean_title,
                    "date": date_str,
                    "youtube_id": yt_id,
                    "embed_url": f"https://www.youtube.com/embed/{yt_id}",
                    "thumbnail": img_src if img_src else f"https://i.ytimg.com/vi/{yt_id}/sddefault.jpg",
                    "source": source_label,
                    "league_id": 2 if is_k2 else 1
                })

        if league_id == 2:
            k2_list = [h for h in crawled if h.get("league_id") == 2]
            existing_ids = {h.get("youtube_id") for h in k2_list}
            for dh in default_k2_highlights:
                if dh.get("youtube_id") not in existing_ids:
                    k2_list.append(dh)
            return k2_list if k2_list else default_k2_highlights
        elif league_id == 1:
            k1_list = [h for h in crawled if h.get("league_id") == 1]
            existing_ids = {h.get("youtube_id") for h in k1_list}
            for dh in default_k1_highlights:
                if dh.get("youtube_id") not in existing_ids:
                    k1_list.append(dh)
            return k1_list if k1_list else default_k1_highlights

        return crawled if crawled else (default_k1_highlights + default_k2_highlights)
    except Exception as e:
        print(f"K리그 하이라이트 영상 크롤링 에러: {e}")
        if league_id == 2:
            return default_k2_highlights
        elif league_id == 1:
            return default_k1_highlights
        return default_k1_highlights + default_k2_highlights


def get_kleague_data(force_refresh=False):
    """
    K리그 전체 데이터 조회 (K리그1, K리그2)
    - 전체 크롤링(순위, 하이라이트 등): 30분 TTL 캐싱
    - 경기 일정/LIVE 스코어(recent_matches): LIVE 경기 시 25초, 일반 시 2분 주기로 동적 갱신
    - 페이지 새로고침 시 LIVE 경기의 최신 시간/스코어/종료 여부를 즉시 반영
    """
    cached_data = None
    cache_valid = False
    now = get_now_kst()

    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
            if "highlights" in cached_data.get("k1", {}) and "highlights" in cached_data.get("k2", {}):
                cache_valid = True
        except Exception as e:
            print(f"K리그 캐시 로드 에러: {e}")

    # 1. 전체 데이터 갱신 필요 여부 판단 (기본 30분 TTL)
    need_full_refresh = force_refresh or not cache_valid
    if cache_valid and not need_full_refresh:
        updated_at_str = cached_data.get("updated_at")
        if updated_at_str:
            try:
                updated_time = datetime.strptime(updated_at_str, "%Y-%m-%d %H:%M:%S")
                diff = (now - updated_time).total_seconds()
                if diff > 1800 or diff < 0:
                    need_full_refresh = True
            except Exception:
                need_full_refresh = True

    if need_full_refresh:
        try:
            # K리그 1
            k1_teams = fetch_kleague_standings(league_id=1, year=2026)
            k1_players = fetch_kleague_player_rankings(league_id=1, year=2026)
            k1_hub = build_kleague_team_hub(k1_teams, k1_players)
            k1_recent = fetch_kleague_recent_matches(league_id=1)
            k1_highlights = fetch_kleague_highlights(league_id=1)

            # K리그 2
            k2_teams = fetch_kleague_standings(league_id=2, year=2026)
            k2_players = fetch_kleague_player_rankings(league_id=2, year=2026)
            k2_hub = build_kleague_team_hub(k2_teams, k2_players)
            k2_recent = fetch_kleague_recent_matches(league_id=2)
            k2_highlights = fetch_kleague_highlights(league_id=2)

            data = {
                "sports": "kleague",
                "title": "K리그 (K LEAGUE)",
                "updated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at_iso": now.isoformat(),
                "matches_updated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
                "highlights": k1_highlights + k2_highlights,
                "k1": {
                    "name": "K리그 1",
                    "teams": k1_teams,
                    "players": k1_players,
                    "team_hub": k1_hub,
                    "recent_matches": k1_recent,
                    "highlights": k1_highlights
                },
                "k2": {
                    "name": "K리그 2",
                    "teams": k2_teams,
                    "players": k2_players,
                    "team_hub": k2_hub,
                    "recent_matches": k2_recent,
                    "highlights": k2_highlights
                }
            }

            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return data
        except Exception as e:
            print(f"K리그 전체 크롤링 에러: {e}")
            if cached_data:
                return cached_data
            raise e

    # 2. 캐시가 유효한 경우: 경기 결과 및 LIVE 스코어의 동적 갱신 여부 확인!
    k1_matches = cached_data.get("k1", {}).get("recent_matches", [])
    k2_matches = cached_data.get("k2", {}).get("recent_matches", [])
    has_live = any(m.get("is_live") for m in (k1_matches + k2_matches))
    matches_updated_at = cached_data.get("matches_updated_at")
    need_matches_refresh = False

    if has_live:
        # LIVE 경기 진행 중: 25초 이상 경과 시 즉시 fetch
        if not matches_updated_at:
            need_matches_refresh = True
        else:
            try:
                m_time = datetime.strptime(matches_updated_at, "%Y-%m-%d %H:%M:%S")
                diff = (now - m_time).total_seconds()
                if diff >= 25 or diff < 0:
                    need_matches_refresh = True
            except Exception:
                need_matches_refresh = True
    else:
        # LIVE 경기가 없더라도 2분(120초) 이상 지났으면 최신 경기 스케줄/결과 확인
        if not matches_updated_at:
            need_matches_refresh = True
        else:
            try:
                m_time = datetime.strptime(matches_updated_at, "%Y-%m-%d %H:%M:%S")
                diff = (now - m_time).total_seconds()
                if diff >= 120 or diff < 0:
                    need_matches_refresh = True
            except Exception:
                need_matches_refresh = True

    if need_matches_refresh:
        try:
            k1_recent = fetch_kleague_recent_matches(league_id=1)
            k2_recent = fetch_kleague_recent_matches(league_id=2)
            if k1_recent:
                cached_data["k1"]["recent_matches"] = k1_recent
            if k2_recent:
                cached_data["k2"]["recent_matches"] = k2_recent
            cached_data["matches_updated_at"] = now.strftime("%Y-%m-%d %H:%M:%S")
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(cached_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"K리그 경기 동적 갱신 에러: {e}")

    return cached_data
