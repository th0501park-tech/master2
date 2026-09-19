"""
해외축구 (프리미어리그, 라리가, 분데스리가, 챔피언스리그, 유로파리그) 데이터 서비스
Goal.com 크롤링 및 ESPN Soccer API 백업 연동
"""
import os
import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)
CACHE_FILE = os.path.join(CACHE_DIR, "overseas_soccer_data.json")

# 해외축구 리그 정의
LEAGUES = {
    "epl": {
        "name": "프리미어리그 (Premier League)",
        "shortName": "EPL",
        "country": "잉글랜드",
        "espnCode": "eng.1",
        "goalUrl": "https://www.goal.com/kr/%ED%94%84%EB%A6%AC%EB%AF%B8%EC%96%B4%EB%A6%AC%EA%B7%B8/%EC%88%9C%EC%9C%84/2kwbbcootiqqgmrzs6o5inle5",
        "icon": "fa-crown",
        "color": "#38003c"
    },
    "laliga": {
        "name": "라리가 (LaLiga)",
        "shortName": "LaLiga",
        "country": "스페인",
        "espnCode": "esp.1",
        "goalUrl": "https://www.goal.com/kr/%ED%94%84%EB%A6%AC%EB%A9%94%EB%9D%BC%EB%A6%AC%EA%B0%80/%EC%88%9C%EC%9C%84/34pl8szyvrbwcmfkuocjm3r6t",
        "icon": "fa-shield-halved",
        "color": "#ee8707"
    },
    "bundesliga": {
        "name": "분데스리가 (Bundesliga)",
        "shortName": "Bundesliga",
        "country": "독일",
        "espnCode": "ger.1",
        "goalUrl": "https://www.goal.com/kr/%EB%B6%84%EB%8D%B0%EC%8A%A4%EB%A6%AC%EA%B0%80/%EC%88%9C%EC%9C%84/6by3h89i2eykc341oz7lv1ddd",
        "icon": "fa-futbol",
        "color": "#d20515"
    },
    "ucl": {
        "name": "UEFA 챔피언스리그 (Champions League)",
        "shortName": "UCL",
        "country": "유럽",
        "espnCode": "uefa.champions",
        "goalUrl": "https://www.goal.com/kr/%EC%B1%94%ED%94%BC%EC%96%B8%EC%8A%A4%EB%A6%AC%EA%B7%B8/%EC%88%9C%EC%9C%84/4oogyu6o156iphvdvphwpck10",
        "icon": "fa-star",
        "color": "#001489"
    },
    "uel": {
        "name": "UEFA 유로파리그 (Europa League)",
        "shortName": "UEL",
        "country": "유럽",
        "espnCode": "uefa.europa",
        "goalUrl": "",
        "icon": "fa-trophy",
        "color": "#f68e1e"
    }
}

# 주요 해외 구단 한글 번역 사전
TEAM_KR_NAMES = {
    "Arsenal": "아스널",
    "Manchester City": "맨체스터 시티",
    "Liverpool": "리버풀",
    "Aston Villa": "애스턴 빌라",
    "Tottenham Hotspur": "토트넘 홋스퍼",
    "Chelsea": "첼시",
    "Newcastle United": "뉴캐슬",
    "Manchester United": "맨체스터 유나이티드",
    "West Ham United": "웨스트햄",
    "Brighton & Hove Albion": "브라이튼",
    "Bournemouth": "본머스",
    "Crystal Palace": "크리스탈 팰리스",
    "Wolverhampton Wanderers": "울버햄튼",
    "Fulham": "풀럼",
    "Everton": "에버턴",
    "Brentford": "브렌트포드",
    "Nottingham Forest": "노팅엄 포레스트",
    "Leicester City": "레스터 시티",
    "Ipswich Town": "입스위치",
    "Southampton": "사우샘프턴",
    "Real Madrid": "레알 마드리드",
    "Barcelona": "바르셀로나",
    "FC Barcelona": "바르셀로나",
    "Atlético Madrid": "아틀레티코 마드리드",
    "Girona": "지로나",
    "Athletic Club": "아틀레틱 빌바오",
    "Real Sociedad": "레알 소시에다드",
    "Real Betis": "레알 베티스",
    "Villarreal": "비야레알",
    "Valencia": "발렌시아",
    "Sevilla": "세비야",
    "Mallorca": "마요르카",
    "Celta Vigo": "셀타 비고",
    "Bayern Munich": "바이에른 뮌헨",
    "Bayer Leverkusen": "레버쿠젠",
    "Borussia Dortmund": "도르트문트",
    "RB Leipzig": "라이프치히",
    "VfB Stuttgart": "슈투트가르트",
    "Eintracht Frankfurt": "프랑크푸르트",
    "SC Freiburg": "프라이부르크",
    "Mainz 05": "마인츠",
    "Paris Saint-Germain": "파리 생제르맹",
    "Inter Milan": "인테르",
    "AC Milan": "AC 밀란",
    "Juventus": "유벤투스",
    "Atalanta": "아탈란타",
    "Napoli": "나폴리",
    "Roma": "AS 로마"
}


def translate_team_name(name):
    """구단명을 한글명으로 변환 (매핑 없으면 원문 반환)"""
    for eng, kr in TEAM_KR_NAMES.items():
        if eng.lower() in name.lower() or name.lower() in eng.lower():
            return kr
    return name


def fetch_standings_goal(goal_url):
    """Goal.com 크롤링을 통한 순위표 조회"""
    if not goal_url:
        return []
    try:
        resp = requests.get(goal_url, headers=HEADERS, timeout=8)
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        table = soup.find("table")
        if not table:
            return []
        
        ranks = []
        rows = table.find_all("tr")
        for tr in rows[1:]:
            cols = [td.text.strip() for td in tr.find_all("td")]
            if len(cols) >= 10:
                img_el = tr.find("img")
                emblem = img_el.get("src", "") if img_el else ""
                
                # Goal.com 순위 컬럼: [POS, 팀명, '', P, W, D, L, F, A, +/-, 승점, 최근폼]
                # 컬럼 파싱
                rank_str = cols[0]
                team_name = cols[1]
                
                # 숫자 컬럼 추출
                nums = [c for c in cols[2:] if c.lstrip('-').isdigit()]
                if len(nums) >= 7:
                    games = int(nums[0])
                    win = int(nums[1])
                    draw = int(nums[2])
                    loss = int(nums[3])
                    gf = int(nums[4])
                    ga = int(nums[5])
                    gd = int(nums[6])
                    pts = int(nums[7]) if len(nums) > 7 else (win * 3 + draw)
                else:
                    games, win, draw, loss, gf, ga, gd, pts = 0, 0, 0, 0, 0, 0, 0, 0

                recent_str = cols[-1] if len(cols) > 10 else ""
                recent = list(recent_str) if recent_str else []

                ranks.append({
                    "rank": int(rank_str) if rank_str.isdigit() else rank_str,
                    "team": team_name,
                    "fullName": team_name,
                    "emblem": emblem,
                    "games": games,
                    "points": pts,
                    "win": win,
                    "draw": draw,
                    "loss": loss,
                    "goalsFor": gf,
                    "goalsAgainst": ga,
                    "goalDiff": gd,
                    "recent": recent
                })
        return ranks
    except Exception as e:
        print(f"Goal.com 크롤링 실패: {e}")
        return []


def fetch_standings_espn(espn_code):
    """ESPN Soccer API를 통한 순위표 조회"""
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{espn_code}/standings"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=8)
        if resp.status_code != 200:
            return []
        data = resp.json()
        children = data.get("children", [])
        if not children:
            return []
        entries = children[0].get("standings", {}).get("entries", [])
        ranks = []
        for entry in entries:
            team = entry.get("team", {})
            stats = {s.get("name"): s.get("value") for s in entry.get("stats", [])}
            
            # 로고 추출
            logos = team.get("logos", [])
            emblem = logos[0].get("href", "") if logos else ""
            
            eng_name = team.get("displayName", team.get("name", ""))
            kr_name = translate_team_name(eng_name)

            ranks.append({
                "rank": int(stats.get("rank", len(ranks) + 1)),
                "team": kr_name,
                "teamEng": eng_name,
                "fullName": eng_name,
                "emblem": emblem,
                "games": int(stats.get("gamesPlayed", 0)),
                "points": int(stats.get("points", 0)),
                "win": int(stats.get("wins", 0)),
                "draw": int(stats.get("ties", 0)),
                "loss": int(stats.get("losses", 0)),
                "goalsFor": int(stats.get("pointsFor", 0)),
                "goalsAgainst": int(stats.get("pointsAgainst", 0)),
                "goalDiff": int(stats.get("pointDifferential", 0)),
                "recent": []
            })
        return ranks
    except Exception as e:
        print(f"ESPN 순위 API 에러 ({espn_code}): {e}")
        return []


def fetch_player_leaders_espn(espn_code):
    """ESPN 통계 API를 통한 득점 및 도움 순위 조회"""
    url = f"https://site.web.api.espn.com/apis/site/v2/sports/soccer/{espn_code}/statistics"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=8)
        if resp.status_code != 200:
            return []
        data = resp.json()
        cat_list = []
        for cat in data.get("stats", []):
            name = cat.get("name")
            display_name = cat.get("displayName")
            is_goal = "goal" in name.lower()
            
            title = "득점 순위 (Top Scorers)" if is_goal else "도움 순위 (Top Assists)"
            icon = "fa-futbol" if is_goal else "fa-hands-helping"
            
            leaders = []
            for rank_idx, lead in enumerate(cat.get("leaders", [])[:15], start=1):
                athlete = lead.get("athlete", {})
                team_data = athlete.get("team", {})
                eng_team = team_data.get("displayName", "")
                kr_team = translate_team_name(eng_team)
                
                headshot = athlete.get("headshot", {}).get("href", "")
                val_str = lead.get("displayValue", "")
                # Format value
                val = f"{lead.get('value', 0)}개 ({val_str})" if val_str else f"{lead.get('value', 0)}"

                leaders.append({
                    "rank": rank_idx,
                    "name": athlete.get("displayName"),
                    "team": kr_team,
                    "teamEng": eng_team,
                    "teamEmblem": team_data.get("logos", [{}])[0].get("href", "") if team_data.get("logos") else "",
                    "headshot": headshot,
                    "value": val,
                    "numeric_val": lead.get("value", 0)
                })

            cat_list.append({
                "category": title,
                "icon": icon,
                "first_player": leaders[0] if leaders else None,
                "ranks": leaders
            })
        return cat_list
    except Exception as e:
        print(f"ESPN 선수 순위 API 에러 ({espn_code}): {e}")
        return []


def build_soccer_team_hub(teams, player_categories):
    """해외축구 구단별 순위 및 소속 리더보드 선수 매핑"""
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
                    "headshot": p.get("headshot", "")
                })
            else:
                # 혹시 영문팀명으로 일치할 경우
                for k, v in hub.items():
                    if p.get("teamEng") and p["teamEng"] in v["team"].get("fullName", ""):
                        v["players"].append({
                            "category": cat["category"],
                            "rank": p["rank"],
                            "name": p["name"],
                            "value": p["value"],
                            "headshot": p.get("headshot", "")
                        })
                        break
    return hub


def get_overseas_soccer_data(force_refresh=False):
    """해외축구 전체 5대 대회 데이터 조회 및 캐싱"""
    if not force_refresh and os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            cached_time = datetime.fromisoformat(data.get("updated_at_iso", "2000-01-01"))
            if (datetime.now() - cached_time).total_seconds() < 300:
                return data
        except Exception as e:
            print(f"해외축구 캐시 로드 에러: {e}")

    result_leagues = {}
    for key, cfg in LEAGUES.items():
        # 1. Goal.com 시도 후, 없거나 비어있으면 ESPN 연동
        teams = []
        if cfg["goalUrl"]:
            teams = fetch_standings_goal(cfg["goalUrl"])
        if not teams:
            teams = fetch_standings_espn(cfg["espnCode"])

        # 2. 선수 랭킹
        players = fetch_player_leaders_espn(cfg["espnCode"])

        # 3. 구단 허브
        hub = build_soccer_team_hub(teams, players)

        result_leagues[key] = {
            "key": key,
            "name": cfg["name"],
            "shortName": cfg["shortName"],
            "country": cfg["country"],
            "color": cfg["color"],
            "icon": cfg["icon"],
            "teams": teams,
            "players": players,
            "team_hub": hub
        }

    now = datetime.now()
    data = {
        "sports": "overseas",
        "title": "해외 축구 (Overseas Football)",
        "updated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at_iso": now.isoformat(),
        "leagues": result_leagues
    }

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return data
