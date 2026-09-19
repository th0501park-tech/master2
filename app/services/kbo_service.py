"""
KBO 리그 데이터 서비스 모듈
공식 koreabaseball.com 크롤링 및 캐싱
"""
import os
import json
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)
CACHE_FILE = os.path.join(CACHE_DIR, "kbo_data.json")

# KBO 공식 팀 엠블럼 및 대표 색상 매핑
TEAM_INFO = {
    "KT": {
        "fullName": "kt wiz",
        "shortName": "KT",
        "color": "#ec1a3a",
        "bgColor": "#1e2022",
        "emblem": "https://6ptotvmi5753.edge.naverncp.com/KBO_IMAGE/KBOHome/resources/images/emblem/regular/2022/KT.png"
    },
    "삼성": {
        "fullName": "삼성 라이온즈",
        "shortName": "삼성",
        "color": "#074ca1",
        "bgColor": "#e8f0fe",
        "emblem": "https://6ptotvmi5753.edge.naverncp.com/KBO_IMAGE/KBOHome/resources/images/emblem/regular/2022/SS.png"
    },
    "LG": {
        "fullName": "LG 트윈스",
        "shortName": "LG",
        "color": "#c30452",
        "bgColor": "#fce8f0",
        "emblem": "https://6ptotvmi5753.edge.naverncp.com/KBO_IMAGE/KBOHome/resources/images/emblem/regular/2022/LG.png"
    },
    "KIA": {
        "fullName": "KIA 타이거즈",
        "shortName": "KIA",
        "color": "#ea0029",
        "bgColor": "#fee8e8",
        "emblem": "https://6ptotvmi5753.edge.naverncp.com/KBO_IMAGE/KBOHome/resources/images/emblem/regular/2022/HT.png"
    },
    "두산": {
        "fullName": "두산 베어스",
        "shortName": "두산",
        "color": "#131230",
        "bgColor": "#eef0f8",
        "emblem": "https://6ptotvmi5753.edge.naverncp.com/KBO_IMAGE/KBOHome/resources/images/emblem/regular/2025/OB.png"
    },
    "NC": {
        "fullName": "NC 다이노스",
        "shortName": "NC",
        "color": "#315288",
        "bgColor": "#edf2f9",
        "emblem": "https://6ptotvmi5753.edge.naverncp.com/KBO_IMAGE/KBOHome/resources/images/emblem/regular/2022/NC.png"
    },
    "SSG": {
        "fullName": "SSG 랜더스",
        "shortName": "SSG",
        "color": "#ce0e2d",
        "bgColor": "#feebee",
        "emblem": "https://6ptotvmi5753.edge.naverncp.com/KBO_IMAGE/KBOHome/resources/images/emblem/regular/2024/SK.png"
    },
    "한화": {
        "fullName": "한화 이글스",
        "shortName": "한화",
        "color": "#ff6600",
        "bgColor": "#fff3e8",
        "emblem": "https://6ptotvmi5753.edge.naverncp.com/KBO_IMAGE/KBOHome/resources/images/emblem/regular/2025/HH.png"
    },
    "롯데": {
        "fullName": "롯데 자이언츠",
        "shortName": "롯데",
        "color": "#041e42",
        "bgColor": "#e8ecf4",
        "emblem": "https://6ptotvmi5753.edge.naverncp.com/KBO_IMAGE/KBOHome/resources/images/emblem/regular/2022/LT.png"
    },
    "키움": {
        "fullName": "키움 히어로즈",
        "shortName": "키움",
        "color": "#570514",
        "bgColor": "#f7e8ea",
        "emblem": "https://6ptotvmi5753.edge.naverncp.com/KBO_IMAGE/KBOHome/resources/images/emblem/regular/2022/WO.png"
    }
}


def fetch_team_rankings():
    """KBO 공식 홈페이지에서 팀 순위 크롤링"""
    url = "https://www.koreabaseball.com/Record/TeamRank/TeamRank.aspx"
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    
    table = soup.find("table")
    team_ranks = []
    if table:
        tbody = table.find("tbody") or table
        for tr in tbody.find_all("tr"):
            cols = [td.text.strip() for td in tr.find_all("td")]
            if len(cols) >= 12:
                team_code = cols[1]
                t_info = TEAM_INFO.get(team_code, {
                    "fullName": team_code,
                    "shortName": team_code,
                    "color": "#4a5568",
                    "bgColor": "#edf2f7",
                    "emblem": ""
                })
                team_ranks.append({
                    "rank": int(cols[0]) if cols[0].isdigit() else cols[0],
                    "team": team_code,
                    "fullName": t_info["fullName"],
                    "shortName": t_info.get("shortName", team_code),
                    "color": t_info["color"],
                    "bgColor": t_info["bgColor"],
                    "emblem": t_info["emblem"],
                    "games": int(cols[2]) if cols[2].isdigit() else cols[2],
                    "win": int(cols[3]) if cols[3].isdigit() else cols[3],
                    "loss": int(cols[4]) if cols[4].isdigit() else cols[4],
                    "draw": int(cols[5]) if cols[5].isdigit() else cols[5],
                    "rate": cols[6],
                    "game_diff": cols[7],
                    "recent10": cols[8],
                    "streak": cols[9],
                    "home": cols[10],
                    "away": cols[11]
                })
    return team_ranks


def fetch_player_rankings():
    """KBO 공식 홈페이지에서 선수 순위 (TOP 5 부문별) 크롤링"""
    url = "https://www.koreabaseball.com/Record/Ranking/Top5.aspx"
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    
    records = soup.find_all("div", class_=lambda x: x and "record" in x.split())
    hitter_categories = []
    pitcher_categories = []

    for i, rec in enumerate(records):
        title_el = rec.find("span", class_="title")
        title = title_el.text.strip() if title_el else f"부문 {i+1}"
        
        img_el = rec.find("div", class_="player_first_thumb")
        img_url = ""
        if img_el and img_el.find("img"):
            src = img_el.find("img").get("src", "")
            if src.startswith("//"):
                img_url = "https:" + src
            else:
                img_url = src
                
        ranks = []
        for rank_num, li in enumerate(rec.find_all("li"), start=1):
            name_el = li.find(class_=lambda x: x and "name" in x)
            team_el = li.find(class_=lambda x: x and "team" in x)
            val_el = li.find(class_=lambda x: x and "rr" in x)
            player_name = name_el.text.strip() if name_el else ""
            team_name = team_el.text.strip() if team_el else ""
            val = val_el.text.strip() if val_el else ""
            
            link = ""
            if name_el and name_el.find("a"):
                link = name_el.find("a").get("href", "")
                if link and not link.startswith("http"):
                    link = "https://www.koreabaseball.com" + link

            t_info = TEAM_INFO.get(team_name, {
                "color": "#4a5568",
                "emblem": ""
            })

            ranks.append({
                "rank": rank_num,
                "name": player_name,
                "team": team_name,
                "teamColor": t_info["color"],
                "teamEmblem": t_info["emblem"],
                "value": val,
                "link": link
            })
        
        cat_data = {
            "category": title,
            "first_img": img_url,
            "first_player": ranks[0] if ranks else None,
            "ranks": ranks
        }
        if i < 15:
            hitter_categories.append(cat_data)
        else:
            pitcher_categories.append(cat_data)

    return hitter_categories, pitcher_categories


def build_team_hub(teams, hitters, pitchers):
    """구단별 몰아보기를 위한 구단별 순위 및 선수 데이터 매핑"""
    hub = {}
    for t in teams:
        team_name = t["team"]
        hub[team_name] = {
            "team": t,
            "hitter_records": [],
            "pitcher_records": []
        }

    # 타자 랭킹 등록
    for cat in hitters:
        cat_name = cat["category"]
        for p in cat["ranks"]:
            team_code = p["team"]
            if team_code in hub:
                hub[team_code]["hitter_records"].append({
                    "category": cat_name,
                    "rank": p["rank"],
                    "name": p["name"],
                    "value": p["value"],
                    "link": p.get("link", "")
                })

    # 투수 랭킹 등록
    for cat in pitchers:
        cat_name = cat["category"]
        for p in cat["ranks"]:
            team_code = p["team"]
            if team_code in hub:
                hub[team_code]["pitcher_records"].append({
                    "category": cat_name,
                    "rank": p["rank"],
                    "name": p["name"],
                    "value": p["value"],
                    "link": p.get("link", "")
                })

    return hub


def get_kbo_data(force_refresh=False):
    """KBO 데이터 조회 (5분 캐시 적용)"""
    if not force_refresh and os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            cached_time = datetime.fromisoformat(data.get("updated_at_iso", "2000-01-01"))
            if (datetime.now() - cached_time).total_seconds() < 300:
                return data
        except Exception as e:
            print(f"KBO 캐시 로드 에러: {e}")

    try:
        team_ranks = fetch_team_rankings()
        hitters, pitchers = fetch_player_rankings()
        team_hub = build_team_hub(team_ranks, hitters, pitchers)

        now = datetime.now()
        data = {
            "sports": "kbo",
            "title": "KBO 한국야구",
            "updated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at_iso": now.isoformat(),
            "teams": team_ranks,
            "hitters": hitters,
            "pitchers": pitchers,
            "team_hub": team_hub,
            "team_info": TEAM_INFO
        }

        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return data
    except Exception as e:
        print(f"KBO 크롤링 에러: {e}")
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        raise e
