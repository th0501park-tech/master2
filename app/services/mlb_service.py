"""
MLB (메이저리그 베이스볼) 데이터 서비스 모듈
공식 MLB Stats API 연동 및 캐싱
"""
import os
import json
from datetime import datetime
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)
CACHE_FILE = os.path.join(CACHE_DIR, "mlb_data.json")

# MLB 30개 구단 한글명 및 컬러
MLB_TEAMS = {
    108: {"name": "LA 에인절스", "color": "#BA0021", "short": "LAA"},
    109: {"name": "애리조나 다이아몬드백스", "color": "#A71930", "short": "ARI"},
    110: {"name": "볼티모어 오리올스", "color": "#DF4601", "short": "BAL"},
    111: {"name": "보스턴 레드삭스", "color": "#BD3039", "short": "BOS"},
    112: {"name": "시카고 컵스", "color": "#0E3386", "short": "CHC"},
    113: {"name": "시카고 화이트삭스", "color": "#27251F", "short": "CWS"},
    114: {"name": "신시내티 레즈", "color": "#C6011F", "short": "CIN"},
    115: {"name": "클리블랜드 가디언스", "color": "#E31937", "short": "CLE"},
    116: {"name": "콜로라도 로키스", "color": "#333366", "short": "COL"},
    117: {"name": "디트로이트 타이거스", "color": "#0C2340", "short": "DET"},
    118: {"name": "휴스턴 애스트로스", "color": "#002D62", "short": "HOU"},
    119: {"name": "LA 다저스", "color": "#005A9C", "short": "LAD"},
    120: {"name": "워싱턴 내셔널스", "color": "#AB0003", "short": "WSH"},
    121: {"name": "뉴욕 메츠", "color": "#002D72", "short": "NYM"},
    133: {"name": "오클랜드 애슬레틱스", "color": "#003831", "short": "OAK"},
    134: {"name": "피츠버그 파이리츠", "color": "#FDB827", "short": "PIT"},
    135: {"name": "샌디에이고 파드리스", "color": "#2F241D", "short": "SD"},
    136: {"name": "시애틀 매리너스", "color": "#0C2340", "short": "SEA"},
    137: {"name": "샌프란시스코 자이언츠", "color": "#FD5A1E", "short": "SF"},
    138: {"name": "세인트루이스 카디널스", "color": "#C41E3A", "short": "STL"},
    139: {"name": "템파베이 레이스", "color": "#092C5C", "short": "TB"},
    140: {"name": "텍사스 레인저스", "color": "#003278", "short": "TEX"},
    141: {"name": "토론토 블루제이스", "color": "#134A8E", "short": "TOR"},
    142: {"name": "미네소타 트윈스", "color": "#002B5C", "short": "MIN"},
    143: {"name": "필라델피아 필리스", "color": "#E81828", "short": "PHI"},
    144: {"name": "애틀랜타 브레이브스", "color": "#CE1141", "short": "ATL"},
    145: {"name": "시카고 화이트삭스", "color": "#27251F", "short": "CWS"},
    146: {"name": "마이애미 말린스", "color": "#00A3E0", "short": "MIA"},
    147: {"name": "뉴욕 양키스", "color": "#0C2340", "short": "NYY"},
    158: {"name": "밀워키 브루어스", "color": "#12284B", "short": "MIL"},
    118: {"name": "캔자스시티 로열스", "color": "#004687", "short": "KC"}
}

DIV_NAMES = {
    200: "AL 서부 (AL West)",
    201: "AL 동부 (AL East)",
    202: "AL 중부 (AL Central)",
    203: "NL 서부 (NL West)",
    204: "NL 동부 (NL East)",
    205: "NL 중부 (NL Central)"
}


def fetch_mlb_standings():
    """MLB 공식 API에서 전체 순위 및 지구별 순위 조회"""
    url = "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=8)
        if resp.status_code != 200:
            return [], []
        data = resp.json()
        
        divisions = []
        all_teams = []
        for rec in data.get("records", []):
            div_id = rec.get("division", {}).get("id")
            div_name = DIV_NAMES.get(div_id, rec.get("division", {}).get("name", "지구"))
            league_id = rec.get("league", {}).get("id")
            league_name = "아메리칸 리그" if league_id == 103 else "내셔널 리그"

            div_team_list = []
            for tr in rec.get("teamRecords", []):
                t = tr.get("team", {})
                t_id = t.get("id")
                meta = MLB_TEAMS.get(t_id, {
                    "name": t.get("name"),
                    "color": "#1e293b",
                    "short": t.get("name")
                })
                
                streak = tr.get("streak", {}).get("streakCode", "-")
                logo = f"https://www.mlbstatic.com/team-logos/{t_id}.svg"
                
                # 최근 10경기
                splits = tr.get("records", {}).get("splitRecords", [])
                last_ten = "-"
                for s in splits:
                    if s.get("type") == "lastTen":
                        last_ten = f"{s.get('wins')}-{s.get('losses')}"

                team_entry = {
                    "rank": int(tr.get("divisionRank", 0)),
                    "teamId": t_id,
                    "team": meta["name"],
                    "teamEng": t.get("name"),
                    "color": meta["color"],
                    "emblem": logo,
                    "games": tr.get("gamesPlayed", 0),
                    "win": tr.get("wins", 0),
                    "loss": tr.get("losses", 0),
                    "rate": tr.get("winningPercentage", ".000"),
                    "game_diff": tr.get("gamesBack", "-"),
                    "runDiff": tr.get("runDifferential", 0),
                    "streak": streak,
                    "recent10": last_ten,
                    "league": league_name,
                    "division": div_name
                }
                div_team_list.append(team_entry)
                all_teams.append(team_entry)

            divisions.append({
                "divisionId": div_id,
                "divisionName": div_name,
                "league": league_name,
                "teams": div_team_list
            })

        # 승률 기준 전체 정렬
        all_teams_sorted = sorted(all_teams, key=lambda x: float(x["rate"]) if x["rate"].replace('.', '').isdigit() else 0, reverse=True)
        for i, t in enumerate(all_teams_sorted, 1):
            t["overallRank"] = i

        return divisions, all_teams_sorted
    except Exception as e:
        print(f"MLB 순위 API 에러: {e}")
        return [], []


def fetch_mlb_leaders():
    """MLB 공식 API에서 타자/투수 리더보드 조회"""
    # 타자: 홈런, 타율, 타점, 안타
    # 투수: 평균자책점(ERA), 다승, 탈삼진, 세이브
    categories = [
        # 타자
        {"cat": "homeRuns", "title": "홈런 (Home Runs)", "group": "hitting", "icon": "fa-baseball-bat-ball"},
        {"cat": "battingAverage", "title": "타율 (Batting Average)", "group": "hitting", "icon": "fa-bullseye"},
        {"cat": "runsBattedIn", "title": "타점 (RBI)", "group": "hitting", "icon": "fa-award"},
        {"cat": "hits", "title": "안타 (Hits)", "group": "hitting", "icon": "fa-baseball"},
        {"cat": "stolenBases", "title": "도루 (Stolen Bases)", "group": "hitting", "icon": "fa-person-running"},
        {"cat": "onBasePlusSlugging", "title": "OPS (출루율+장타율)", "group": "hitting", "icon": "fa-fire"},
        # 투수
        {"cat": "earnedRunAverage", "title": "평균자책점 (ERA)", "group": "pitching", "icon": "fa-shield-halved"},
        {"cat": "wins", "title": "다승 (Wins)", "group": "pitching", "icon": "fa-trophy"},
        {"cat": "strikeouts", "title": "탈삼진 (Strikeouts)", "group": "pitching", "icon": "fa-bolt"},
        {"cat": "saves", "title": "세이브 (Saves)", "group": "pitching", "icon": "fa-lock"},
        {"cat": "whip", "title": "WHIP (이닝당 출루허용)", "group": "pitching", "icon": "fa-gauge-high"}
    ]

    hitter_cats = []
    pitcher_cats = []

    cat_keys = ",".join([c["cat"] for c in categories])
    url = f"https://statsapi.mlb.com/api/v1/stats/leaders?leaderCategories={cat_keys}&statGroup=hitting,pitching&limit=5"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=8)
        if resp.status_code == 200:
            ldata = resp.json()
            league_leaders = ldata.get("leagueLeaders", [])

            # 매핑 편의를 위해 카테고리별로 그룹핑
            cat_map = {}
            for item in league_leaders:
                cname = item.get("leaderCategory")
                if cname not in cat_map:
                    cat_map[cname] = item.get("leaders", [])
                else:
                    cat_map[cname].extend(item.get("leaders", []))

            for cfg in categories:
                cname = cfg["cat"]
                raw_leaders = cat_map.get(cname, [])
                
                # 중복 제거 및 상위 5명
                seen_persons = set()
                formatted_ranks = []
                for lead in raw_leaders:
                    p = lead.get("person", {})
                    pid = p.get("id")
                    if pid in seen_persons:
                        continue
                    seen_persons.add(pid)

                    team = lead.get("team", {})
                    tid = team.get("id")
                    t_meta = MLB_TEAMS.get(tid, {"name": team.get("name"), "color": "#1e293b"})

                    photo = f"https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/{pid}/headshot/67/current"
                    team_emblem = f"https://www.mlbstatic.com/team-logos/{tid}.svg"

                    formatted_ranks.append({
                        "rank": len(formatted_ranks) + 1,
                        "name": p.get("fullName"),
                        "playerId": pid,
                        "team": t_meta["name"],
                        "teamEng": team.get("name"),
                        "teamColor": t_meta["color"],
                        "teamEmblem": team_emblem,
                        "photo": photo,
                        "value": lead.get("value")
                    })
                    if len(formatted_ranks) >= 5:
                        break

                cat_obj = {
                    "category": cfg["title"],
                    "icon": cfg["icon"],
                    "first_player": formatted_ranks[0] if formatted_ranks else None,
                    "first_img": formatted_ranks[0]["photo"] if formatted_ranks else "",
                    "ranks": formatted_ranks
                }

                if cfg["group"] == "hitting":
                    hitter_cats.append(cat_obj)
                else:
                    pitcher_cats.append(cat_obj)
    except Exception as e:
        print(f"MLB 리더보드 API 에러: {e}")

    return hitter_cats, pitcher_cats


def build_mlb_team_hub(all_teams, hitter_cats, pitcher_cats):
    """MLB 구단별 순위 및 소속 선수 몰아보기 데이터 매핑"""
    hub = {}
    for t in all_teams:
        hub[t["team"]] = {
            "team": t,
            "hitters": [],
            "pitchers": []
        }

    for cat in hitter_cats:
        for p in cat["ranks"]:
            t_name = p["team"]
            if t_name in hub:
                hub[t_name]["hitters"].append({
                    "category": cat["category"],
                    "rank": p["rank"],
                    "name": p["name"],
                    "value": p["value"],
                    "photo": p.get("photo", "")
                })

    for cat in pitcher_cats:
        for p in cat["ranks"]:
            t_name = p["team"]
            if t_name in hub:
                hub[t_name]["pitchers"].append({
                    "category": cat["category"],
                    "rank": p["rank"],
                    "name": p["name"],
                    "value": p["value"],
                    "photo": p.get("photo", "")
                })

    return hub


def get_mlb_data(force_refresh=False):
    """MLB 전체 데이터 조회 및 캐싱"""
    if not force_refresh and os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            cached_time = datetime.fromisoformat(data.get("updated_at_iso", "2000-01-01"))
            if (datetime.now() - cached_time).total_seconds() < 300:
                return data
        except Exception as e:
            print(f"MLB 캐시 로드 에러: {e}")

    try:
        divisions, all_teams = fetch_mlb_standings()
        hitters, pitchers = fetch_mlb_leaders()
        hub = build_mlb_team_hub(all_teams, hitters, pitchers)

        now = datetime.now()
        data = {
            "sports": "mlb",
            "title": "MLB 메이저리그 (Major League Baseball)",
            "updated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at_iso": now.isoformat(),
            "divisions": divisions,
            "all_teams": all_teams,
            "hitters": hitters,
            "pitchers": pitchers,
            "team_hub": hub
        }

        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return data
    except Exception as e:
        print(f"MLB 수집 에러: {e}")
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        raise e
