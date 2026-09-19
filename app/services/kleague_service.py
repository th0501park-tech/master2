"""
K리그 (K리그1, K리그2) 데이터 서비스 모듈
K리그 공식 데이터 포털 및 공식 사이트 연동
"""
import os
import json
from datetime import datetime
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/json; charset=utf-8"
}

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)
CACHE_FILE = os.path.join(CACHE_DIR, "kleague_data.json")

# K리그 주요 구단 대표 컬러 및 엠블럼
KLEAGUE_TEAMS = {
    "울산": {
        "fullName": "울산 HD FC",
        "shortName": "울산",
        "color": "#002B49",
        "accent": "#F5A623",
        "emblem": "https://upload.wikimedia.org/wikipedia/ko/thumb/9/91/Ulsan_HD_FC_logo.svg/200px-Ulsan_HD_FC_logo.svg.png"
    },
    "포항": {
        "fullName": "포항 스틸러스",
        "shortName": "포항",
        "color": "#E31B23",
        "accent": "#000000",
        "emblem": "https://upload.wikimedia.org/wikipedia/ko/thumb/2/23/Pohang_Steelers_logo.svg/200px-Pohang_Steelers_logo.svg.png"
    },
    "광주": {
        "fullName": "광주 FC",
        "shortName": "광주",
        "color": "#FDB913",
        "accent": "#C8102E",
        "emblem": "https://upload.wikimedia.org/wikipedia/ko/thumb/2/2a/Gwangju_FC_logo.svg/200px-Gwangju_FC_logo.svg.png"
    },
    "전북": {
        "fullName": "전북 현대 모터스",
        "shortName": "전북",
        "color": "#00552E",
        "accent": "#A3D867",
        "emblem": "https://upload.wikimedia.org/wikipedia/ko/thumb/2/2c/Jeonbuk_Hyundai_Motors_emblem.svg/200px-Jeonbuk_Hyundai_Motors_emblem.svg.png"
    },
    "대구": {
        "fullName": "대구 FC",
        "shortName": "대구",
        "color": "#76C5EE",
        "accent": "#142548",
        "emblem": "https://upload.wikimedia.org/wikipedia/ko/thumb/1/14/Daegu_FC_emblem.svg/200px-Daegu_FC_emblem.svg.png"
    },
    "인천": {
        "fullName": "인천 유나이티드",
        "shortName": "인천",
        "color": "#0047AB",
        "accent": "#000000",
        "emblem": "https://upload.wikimedia.org/wikipedia/ko/thumb/b/be/Incheon_United_FC_emblem.svg/200px-Incheon_United_FC_emblem.svg.png"
    },
    "서울": {
        "fullName": "FC 서울",
        "shortName": "서울",
        "color": "#C8102E",
        "accent": "#000000",
        "emblem": "https://upload.wikimedia.org/wikipedia/ko/thumb/c/cd/FC_Seoul_emblem.svg/200px-FC_Seoul_emblem.svg.png"
    },
    "대전": {
        "fullName": "대전 하나 시티즌",
        "shortName": "대전",
        "color": "#006738",
        "accent": "#862633",
        "emblem": "https://upload.wikimedia.org/wikipedia/ko/thumb/e/e0/Daejeon_Hana_Citizen_emblem.svg/200px-Daejeon_Hana_Citizen_emblem.svg.png"
    },
    "제주": {
        "fullName": "제주 유나이티드",
        "shortName": "제주",
        "color": "#FF671F",
        "accent": "#C8102E",
        "emblem": "https://upload.wikimedia.org/wikipedia/ko/thumb/d/d4/Jeju_United_FC_emblem.svg/200px-Jeju_United_FC_emblem.svg.png"
    },
    "강원": {
        "fullName": "강원 FC",
        "shortName": "강원",
        "color": "#E55C00",
        "accent": "#004534",
        "emblem": "https://upload.wikimedia.org/wikipedia/ko/thumb/7/7b/Gangwon_FC_logo.svg/200px-Gangwon_FC_logo.svg.png"
    },
    "수원FC": {
        "fullName": "수원 FC",
        "shortName": "수원FC",
        "color": "#002B49",
        "accent": "#E31B23",
        "emblem": "https://upload.wikimedia.org/wikipedia/ko/thumb/7/74/Suwon_FC_logo.svg/200px-Suwon_FC_logo.svg.png"
    },
    "김천": {
        "fullName": "김천 상무 FC",
        "shortName": "김천",
        "color": "#BA0C2F",
        "accent": "#0C2340",
        "emblem": "https://upload.wikimedia.org/wikipedia/ko/thumb/5/52/Gimcheon_Sangmu_FC_emblem.svg/200px-Gimcheon_Sangmu_FC_emblem.svg.png"
    },
    "안양": {
        "fullName": "FC 안양",
        "shortName": "안양",
        "color": "#532E85",
        "accent": "#E8AF27",
        "emblem": "https://upload.wikimedia.org/wikipedia/ko/thumb/c/cd/FC_Anyang_logo.svg/200px-FC_Anyang_logo.svg.png"
    },
    "수원": {
        "fullName": "수원 삼성 블루윙즈",
        "shortName": "수원",
        "color": "#0055A5",
        "accent": "#E31B23",
        "emblem": "https://upload.wikimedia.org/wikipedia/ko/thumb/0/08/Suwon_Samsung_Bluewings_logo.svg/200px-Suwon_Samsung_Bluewings_logo.svg.png"
    },
    "부산": {
        "fullName": "부산 아이파크",
        "shortName": "부산",
        "color": "#C8102E",
        "accent": "#FFFFFF",
        "emblem": "https://upload.wikimedia.org/wikipedia/ko/thumb/4/4b/Busan_IPark_logo.svg/200px-Busan_IPark_logo.svg.png"
    },
    "성남": {
        "fullName": "성남 FC",
        "shortName": "성남",
        "color": "#1C1C1C",
        "accent": "#A7A8AA",
        "emblem": "https://upload.wikimedia.org/wikipedia/ko/thumb/9/91/Seongnam_FC_emblem.svg/200px-Seongnam_FC_emblem.svg.png"
    },
    "부천": {
        "fullName": "부천 FC 1995",
        "shortName": "부천",
        "color": "#BA0C2F",
        "accent": "#000000",
        "emblem": "https://upload.wikimedia.org/wikipedia/ko/thumb/3/36/Bucheon_FC_1995_logo.svg/200px-Bucheon_FC_1995_logo.svg.png"
    },
    "전남": {
        "fullName": "전남 드래곤즈",
        "shortName": "전남",
        "color": "#FFC72C",
        "accent": "#000000",
        "emblem": "https://upload.wikimedia.org/wikipedia/ko/thumb/4/4e/Jeonnam_Dragons_emblem.svg/200px-Jeonnam_Dragons_emblem.svg.png"
    },
    "경남": {
        "fullName": "경남 FC",
        "shortName": "경남",
        "color": "#C8102E",
        "accent": "#FFFFFF",
        "emblem": "https://upload.wikimedia.org/wikipedia/ko/thumb/0/09/Gyeongnam_FC_logo.svg/200px-Gyeongnam_FC_logo.svg.png"
    },
    "서울E": {
        "fullName": "서울 이랜드 FC",
        "shortName": "서울E",
        "color": "#00205B",
        "accent": "#A7A8AA",
        "emblem": "https://upload.wikimedia.org/wikipedia/ko/thumb/d/d3/Seoul_E-Land_FC_logo.svg/200px-Seoul_E-Land_FC_logo.svg.png"
    },
    "충북청주": {
        "fullName": "충북 청주 FC",
        "shortName": "충북청주",
        "color": "#002B49",
        "accent": "#C8102E",
        "emblem": "https://upload.wikimedia.org/wikipedia/ko/thumb/e/e3/Chungbuk_Cheongju_FC_logo.svg/200px-Chungbuk_Cheongju_FC_logo.svg.png"
    },
    "충남아산": {
        "fullName": "충남 아산 FC",
        "shortName": "충남아산",
        "color": "#003A70",
        "accent": "#FDB913",
        "emblem": "https://upload.wikimedia.org/wikipedia/ko/thumb/8/8f/Chungnam_Asan_FC_emblem.svg/200px-Chungnam_Asan_FC_emblem.svg.png"
    },
    "김포": {
        "fullName": "김포 FC",
        "shortName": "김포",
        "color": "#0047AB",
        "accent": "#FFC72C",
        "emblem": "https://upload.wikimedia.org/wikipedia/ko/thumb/1/1a/Gimpo_FC_logo.svg/200px-Gimpo_FC_logo.svg.png"
    },
    "안산": {
        "fullName": "안산 그리너스 FC",
        "shortName": "안산",
        "color": "#006738",
        "accent": "#FDB913",
        "emblem": "https://upload.wikimedia.org/wikipedia/ko/thumb/6/62/Ansan_Greeners_FC_emblem.svg/200px-Ansan_Greeners_FC_emblem.svg.png"
    },
    "천안": {
        "fullName": "천안 시티 FC",
        "shortName": "천안",
        "color": "#76C5EE",
        "accent": "#002B49",
        "emblem": "https://upload.wikimedia.org/wikipedia/ko/thumb/1/1d/Cheonan_City_FC_logo.svg/200px-Cheonan_City_FC_logo.svg.png"
    }
}


def get_team_meta(team_name):
    """구단 메타데이터(색상, 엠블럼 등) 조회"""
    for key, info in KLEAGUE_TEAMS.items():
        if key in team_name or team_name in key:
            return info
    return {
        "fullName": team_name,
        "shortName": team_name,
        "color": "#334155",
        "accent": "#64748b",
        "emblem": ""
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
        meta = get_team_meta(t_name)
        
        recent_games = []
        for i in range(1, 7):
            g = r.get(f"game{i:02d}")
            if g:
                recent_games.append(g)
                
        result.append({
            "rank": r.get("rank"),
            "teamId": r.get("teamId"),
            "team": t_name,
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


def get_kleague_data(force_refresh=False):
    """K리그 전체 데이터 조회 (K리그1, K리그2) 및 캐싱"""
    if not force_refresh and os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            cached_time = datetime.fromisoformat(data.get("updated_at_iso", "2000-01-01"))
            if (datetime.now() - cached_time).total_seconds() < 300:
                return data
        except Exception as e:
            print(f"K리그 캐시 로드 에러: {e}")

    try:
        # K리그 1
        k1_teams = fetch_kleague_standings(league_id=1, year=2026)
        k1_players = fetch_kleague_player_rankings(league_id=1, year=2026)
        k1_hub = build_kleague_team_hub(k1_teams, k1_players)

        # K리그 2
        k2_teams = fetch_kleague_standings(league_id=2, year=2026)
        k2_players = fetch_kleague_player_rankings(league_id=2, year=2026)
        k2_hub = build_kleague_team_hub(k2_teams, k2_players)

        now = datetime.now()
        data = {
            "sports": "kleague",
            "title": "K리그 (K LEAGUE)",
            "updated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at_iso": now.isoformat(),
            "k1": {
                "name": "K리그 1",
                "teams": k1_teams,
                "players": k1_players,
                "team_hub": k1_hub
            },
            "k2": {
                "name": "K리그 2",
                "teams": k2_teams,
                "players": k2_players,
                "team_hub": k2_hub
            }
        }

        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return data
    except Exception as e:
        print(f"K리그 크롤링 에러: {e}")
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        raise e
