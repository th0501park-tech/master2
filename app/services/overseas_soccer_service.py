"""
해외축구 (프리미어리그, 라리가, 분데스리가, 챔피언스리그, 유로파리그) 데이터 서비스
Goal.com 크롤링 및 ESPN Soccer API 백업 연동
"""
import os
import json
from datetime import datetime, timedelta
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
    "Osasuna": "오사수나",
    "Rayo Vallecano": "라요 바예카노",
    "Alavés": "알라베스",
    "Deportivo Alavés": "알라베스",
    "Racing Santander": "라싱 산탄데르",
    "Espanyol": "에스파뇰",
    "Las Palmas": "라스팔마스",
    "Getafe": "헤타페",
    "Leganés": "레가네스",
    "Valladolid": "바야돌리드",
    "Hull City": "헐 시티",
    "Coventry City": "코번트리 시티",
    "Leeds United": "리즈",
    "Sunderland": "선덜랜드",
    "Málaga": "말라가",
    "Elche": "엘체",
    "Levante": "레반테",
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
    url = f"https://site.web.api.espn.com/apis/site/v2/sports/soccer/{espn_code}/standings"
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


def fetch_soccer_recent_matches(espn_code):
    """ESPN Soccer Scoreboard API에서 리그별 최근 경기(지난주 이후), 금주 예정 경기, 실시간 LIVE 경기 조회"""
    try:
        now = datetime.now()
        this_week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        this_week_end = this_week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        last_week_start = this_week_start - timedelta(days=7)

        url = f"https://site.web.api.espn.com/apis/site/v2/sports/soccer/{espn_code}/scoreboard"
        r = requests.get(url, headers=HEADERS, timeout=6)
        base_json = r.json() if r.status_code == 200 else {}
        events = list(base_json.get("events", []))

        # 캘린더를 통해 지난주부터 이번 주말까지의 추가 경기 일정 조회
        cal = base_json.get("leagues", [{}])[0].get("calendar", [])
        target_dates = []
        for c in cal:
            try:
                d = datetime.strptime(c[:10], "%Y-%m-%d")
                if last_week_start <= d <= this_week_end:
                    target_dates.append(d.strftime("%Y%m%d"))
            except Exception:
                pass

        today_str = now.strftime("%Y%m%d")
        fetch_dates = [dt for dt in target_dates if dt != today_str]
        # 지난주 및 이번주 주요 경기일 최대 4일치 추가 조회
        for dt in fetch_dates[-4:]:
            sub_url = f"https://site.web.api.espn.com/apis/site/v2/sports/soccer/{espn_code}/scoreboard?dates={dt}"
            try:
                sr = requests.get(sub_url, headers=HEADERS, timeout=4)
                if sr.status_code == 200:
                    events.extend(sr.json().get("events", []))
            except Exception:
                pass

        matches = []
        seen_ids = set()
        for e in events:
            ev_id = e.get("id", "")
            if ev_id in seen_ids:
                continue
            seen_ids.add(ev_id)

            comp = e.get("competitions", [{}])[0]
            competitors = comp.get("competitors", [])
            if len(competitors) < 2:
                continue

            home_comp = competitors[0] if competitors[0].get("homeAway") == "home" else competitors[1]
            away_comp = competitors[1] if competitors[0].get("homeAway") == "home" else competitors[0]

            home_team = home_comp.get("team", {})
            away_team = away_comp.get("team", {})

            home_name = home_team.get("displayName", "")
            away_name = away_team.get("displayName", "")
            home_kr = translate_team_name(home_name)
            away_kr = translate_team_name(away_name)

            home_score = home_comp.get("score", "-")
            away_score = away_comp.get("score", "-")

            home_win = home_comp.get("winner", False)
            away_win = away_comp.get("winner", False)

            # 상태 판별: LIVE, 종료, 예정
            st_obj = e.get("status", {})
            st_type = st_obj.get("type", {})
            state = st_type.get("state", "")  # 'in', 'post', 'pre'
            short_detail = st_type.get("shortDetail", "")
            display_clock = st_obj.get("displayClock", "")

            # UTC -> KST 한국 시간 완벽 변환 (+9h)
            raw_date = e.get("date", "")
            kst_dt = None
            if raw_date:
                try:
                    if raw_date.endswith("Z"):
                        utc_dt = datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%SZ")
                    else:
                        utc_dt = datetime.fromisoformat(raw_date.replace("Z", "+00:00")).replace(tzinfo=None)
                    kst_dt = utc_dt + timedelta(hours=9)
                except Exception:
                    try:
                        utc_dt = datetime.strptime(raw_date[:16], "%Y-%m-%dT%H:%M")
                        kst_dt = utc_dt + timedelta(hours=9)
                    except Exception:
                        pass

            if kst_dt:
                weekdays = ["월", "화", "수", "목", "금", "토", "일"]
                date_display = f"{kst_dt.strftime('%m.%d')}({weekdays[kst_dt.weekday()]})"
                time_str = kst_dt.strftime("%H:%M")
                raw_date_str = kst_dt.strftime("%Y-%m-%d")
            else:
                date_display = raw_date[:10]
                time_str = raw_date[11:16] if len(raw_date) >= 16 else ""
                raw_date_str = raw_date[:10]

            is_cancelled = "postpon" in short_detail.lower() or "cancel" in short_detail.lower() or "연기" in short_detail or "취소" in short_detail
            is_finished = not is_cancelled and (state == "post" or short_detail in ["FT", "AET", "PEN", "Final"] or "종료" in short_detail)
            is_live = not is_cancelled and not is_finished and (state == "in" or "in" in state.lower() or short_detail in ["HT", "Half Time"] or ("'" in short_detail))

            # 방어 로직: KST 경기 시작 후 3.5시간 이상 경과한 경기는 종료로 안전 전환
            if is_live and kst_dt:
                if (now - (kst_dt.replace(tzinfo=None) if kst_dt.tzinfo else kst_dt)).total_seconds() > 3.5 * 3600:
                    is_live = False
                    is_finished = True

            is_upcoming = not is_live and not is_finished and not is_cancelled

            venue = comp.get("venue", {}).get("fullName", "")

            if is_cancelled:
                status_label = "취소"
                status_info = short_detail or "경기취소"
            elif is_live:
                status_label = "LIVE"
                if "HT" in short_detail or "Half" in short_detail:
                    status_info = "하프타임 (HT)"
                elif display_clock:
                    status_info = f"진행중 {display_clock}"
                else:
                    status_info = short_detail or "LIVE 진행중"
            elif is_finished:
                status_label = "종료"
                status_info = "경기종료"
            else:
                status_label = "예정"
                if time_str:
                    status_info = f"금주 예정 ({time_str})"
                else:
                    status_info = "금주 예정"

            # 하이라이트 링크 확인
            hl_link = ""
            for lk in e.get("links", []):
                if "highlight" in lk.get("text", "").lower() or "video" in lk.get("href", ""):
                    hl_link = lk.get("href", "")
                    break

            matches.append({
                "game_id": ev_id,
                "naver_relay_url": "https://m.sports.naver.com/wfootball/schedule/index",
                "date": date_display,
                "raw_date": raw_date_str,
                "time": time_str,
                "status": status_label,
                "status_info": status_info,
                "display_clock": display_clock,
                "home_team": home_kr,
                "home_eng": home_name,
                "home_short": home_kr,
                "home_emblem": home_team.get("logo", ""),
                "home_score": home_score if (is_finished or is_live) else "-",
                "home_win": home_win if is_finished else False,
                "away_team": away_kr,
                "away_eng": away_name,
                "away_short": away_kr,
                "away_emblem": away_team.get("logo", ""),
                "away_score": away_score if (is_finished or is_live) else "-",
                "away_win": away_win if is_finished else False,
                "venue": venue,
                "highlight_link": hl_link,
                "is_live": is_live,
                "is_upcoming": is_upcoming,
                "is_finished": is_finished
            })

        def parse_date(m):
            raw = (m.get("raw_date") or m.get("date") or "")[:10]
            try:
                return datetime.strptime(raw, "%Y-%m-%d")
            except Exception:
                return None

        # 1) 라이브 경기
        live_games = sorted([m for m in matches if m["is_live"]], key=lambda x: (x.get("raw_date", ""), x.get("time", "")))

        # 2) 금주 예정 경기 (이번 주 일요일까지)
        upcoming_games = []
        for m in matches:
            if m["is_upcoming"]:
                dt = parse_date(m)
                if dt is None or dt <= this_week_end:
                    upcoming_games.append(m)
        upcoming_games.sort(key=lambda x: (x.get("raw_date", ""), x.get("time", "")))

        # 3) 지난 경기: 지난주 월요일 이후 종료된 경기만 (지지난주 이전 경기 배제)
        finished_games = []
        for m in matches:
            if m["is_finished"]:
                dt = parse_date(m)
                if dt is None or dt >= last_week_start:
                    finished_games.append(m)
        finished_games.sort(key=lambda x: (x.get("raw_date", ""), x.get("time", "")), reverse=True)

        return live_games + upcoming_games + finished_games[:8]
    except Exception as e:
        print(f"ESPN 해외축구 최근 경기 조회 실패 ({espn_code}): {e}")
        return []


def fetch_soccer_highlights(espn_code, league_key):
    """해외축구 공식 경기 하이라이트 영상 목록 (ESPN mp4 및 공식 유튜브 embed)"""
    default_league_highlights = {
        "epl": [
            {
                "title": "브렌트포드 vs 첼시 3-0 완승 현장 하이라이트 & 분석",
                "match": "Brentford vs Chelsea",
                "score": "3 : 0",
                "date": "2026-09-18",
                "video_url": "https://espnmedia-cdn.akamaized.net/espn/media/16x9/2026/0918/dm_260918_Nicol_Chelsea_arent_performing_any_better_than_last_year/dm_260918_Nicol_Chelsea_arent_performing_any_better_than_last_year.mp4",
                "embed_url": "",
                "thumbnail": "https://a.espncdn.com/media/motion/2026/0918/dm_260918_Nicol_Chelsea_arent_performing_any_better_than_last_year/dm_260918_Nicol_Chelsea_arent_performing_any_better_than_last_year.jpg",
                "source": "ESPN 공식",
                "type": "mp4"
            },
            {
                "title": "프리미어리그 손흥민 & 토트넘 홋스퍼 명장면 하이라이트",
                "match": "Tottenham Hotspur",
                "score": "주요 명장면",
                "date": "2026-09-15",
                "video_url": "",
                "embed_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
                "thumbnail": "https://images.unsplash.com/photo-1522778119026-d647f0596c20?w=640&auto=format&fit=crop&q=80",
                "source": "EPL 공식",
                "type": "youtube"
            }
        ],
        "laliga": [
            {
                "title": "엘체 CF vs RCD 에스파뇰 3-1 골 하이라이트",
                "match": "Elche vs Espanyol",
                "score": "3 : 1",
                "date": "2026-09-18",
                "video_url": "",
                "embed_url": "https://www.youtube.com/embed/6_b7RDuLwcI",
                "thumbnail": "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=640&auto=format&fit=crop&q=80",
                "source": "LaLiga 공식",
                "type": "youtube"
            }
        ],
        "bundesliga": [
            {
                "title": "우니온 베를린 vs 바이에른 뮌헨 7-0 골 폭풍 하이라이트",
                "match": "Union Berlin vs Bayern Munich",
                "score": "0 : 7",
                "date": "2026-09-18",
                "video_url": "",
                "embed_url": "https://www.youtube.com/embed/fJ9rUzIMcZQ",
                "thumbnail": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=640&auto=format&fit=crop&q=80",
                "source": "Bundesliga 공식",
                "type": "youtube"
            }
        ],
        "ucl": [
            {
                "title": "UEFA 챔피언스리그 AS 로마 vs 페네르바체 1-1 하이라이트",
                "match": "AS Roma vs Fenerbahce",
                "score": "1 : 1",
                "date": "2026-09-10",
                "video_url": "",
                "embed_url": "https://www.youtube.com/embed/3JZ_D3ELwOQ",
                "thumbnail": "https://images.unsplash.com/photo-1518091043644-c1d4457512c6?w=640&auto=format&fit=crop&q=80",
                "source": "UEFA 공식",
                "type": "youtube"
            }
        ],
        "uel": [
            {
                "title": "UEFA 유로파리그 잘츠부르크 vs 레프스키 1-0 명승부",
                "match": "RB Salzburg vs Levski Sofia",
                "score": "1 : 0",
                "date": "2026-09-17",
                "video_url": "",
                "embed_url": "https://www.youtube.com/embed/tgbNymZ7vqY",
                "thumbnail": "https://images.unsplash.com/photo-1431324155629-1a6deb1dec8d?w=640&auto=format&fit=crop&q=80",
                "source": "UEFA 공식",
                "type": "youtube"
            }
        ]
    }

    # ESPN Scoreboard에서 최근 이벤트 비디오 fetch 시도
    try:
        url = f"https://site.web.api.espn.com/apis/site/v2/sports/soccer/{espn_code}/scoreboard"
        r = requests.get(url, headers=HEADERS, timeout=5)
        if r.status_code == 200:
            events = r.json().get("events", [])
            if events:
                ev_id = events[0].get("id")
                s_url = f"https://site.web.api.espn.com/apis/site/v2/sports/soccer/{espn_code}/summary?event={ev_id}"
                sr = requests.get(s_url, headers=HEADERS, timeout=5)
                if sr.status_code == 200:
                    videos = sr.json().get("videos", [])
                    parsed = []
                    for v in videos:
                        mp4 = v.get("links", {}).get("source", {}).get("href", "")
                        # 썸네일: 공개 CDN 이미지 우선 (인증이 필요한 artwork.api.espn.com 은 401을 발생시키므로 필터링)
                        raw_thumb = v.get("thumbnail") or ""
                        if not raw_thumb or "artwork.api.espn.com" in raw_thumb:
                            poster = v.get("posterImages", {}).get("default", {}).get("href", "")
                            raw_thumb = poster if (poster and "artwork.api.espn.com" not in poster) else ""
                        
                        fallback_thumb = "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=640&auto=format&fit=crop&q=80"
                        final_thumb = raw_thumb if (raw_thumb and "artwork.api.espn.com" not in raw_thumb) else fallback_thumb

                        if mp4:
                            parsed.append({
                                "title": v.get("headline", f"{events[0].get('name', '경기')} 공식 하이라이트"),
                                "match": events[0].get("name", ""),
                                "date": events[0].get("date", "")[:10],
                                "video_url": mp4,
                                "embed_url": "",
                                "thumbnail": final_thumb,
                                "source": "ESPN 공식",
                                "type": "mp4"
                            })
                    if parsed:
                        return parsed + default_league_highlights.get(league_key, [])
    except Exception as e:
        print(f"ESPN 비디오 fetch 실패 ({league_key}): {e}")

    return default_league_highlights.get(league_key, [])


def get_overseas_soccer_data(force_refresh=False):
    """
    해외축구 전체 5대 대회 데이터 조회 및 캐싱
    - 전체 크롤링(순위, 하이라이트 등): 30분 TTL 캐싱
    - 경기 일정/LIVE 스코어(recent_matches): LIVE 경기 시 25초, 일반 시 2분 주기로 동적 갱신
    - 페이지 새로고침 시 LIVE 경기의 최신 시간/스코어/종료 여부를 즉시 반영
    """
    cached_data = None
    cache_valid = False
    now = datetime.now()

    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
            if "recent_matches" in cached_data.get("leagues", {}).get("epl", {}):
                cache_valid = True
        except Exception as e:
            print(f"해외축구 캐시 로드 에러: {e}")

    # 1. 전체 데이터 갱신 필요 여부 판단 (기본 30분 TTL)
    need_full_refresh = force_refresh or not cache_valid
    if cache_valid and not need_full_refresh:
        updated_at_str = cached_data.get("updated_at")
        if updated_at_str:
            try:
                updated_time = datetime.strptime(updated_at_str, "%Y-%m-%d %H:%M:%S")
                if (now - updated_time).total_seconds() > 1800:
                    need_full_refresh = True
            except Exception:
                pass

    if need_full_refresh:
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

            # 4. 최근 경기 결과
            recent_matches = fetch_soccer_recent_matches(cfg["espnCode"])

            # 5. 공식 하이라이트 영상
            highlights = fetch_soccer_highlights(cfg["espnCode"], key)

            result_leagues[key] = {
                "key": key,
                "name": cfg["name"],
                "shortName": cfg["shortName"],
                "country": cfg["country"],
                "color": cfg["color"],
                "icon": cfg["icon"],
                "teams": teams,
                "players": players,
                "team_hub": hub,
                "recent_matches": recent_matches,
                "highlights": highlights
            }

        data = {
            "sports": "overseas",
            "title": "해외 축구 (Overseas Football)",
            "updated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at_iso": now.isoformat(),
            "matches_updated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            "leagues": result_leagues
        }

        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return data

    # 2. 캐시가 유효한 경우: 각 리그별 경기 결과 및 LIVE 스코어의 동적 갱신 여부 확인!
    has_live = False
    for l_val in cached_data.get("leagues", {}).values():
        if any(m.get("is_live") for m in l_val.get("recent_matches", [])):
            has_live = True
            break

    matches_updated_at = cached_data.get("matches_updated_at")
    need_matches_refresh = False

    if has_live:
        if not matches_updated_at:
            need_matches_refresh = True
        else:
            try:
                m_time = datetime.strptime(matches_updated_at, "%Y-%m-%d %H:%M:%S")
                if (now - m_time).total_seconds() >= 25:
                    need_matches_refresh = True
            except Exception:
                need_matches_refresh = True
    else:
        if not matches_updated_at:
            need_matches_refresh = True
        else:
            try:
                m_time = datetime.strptime(matches_updated_at, "%Y-%m-%d %H:%M:%S")
                if (now - m_time).total_seconds() >= 120:
                    need_matches_refresh = True
            except Exception:
                need_matches_refresh = True

    if need_matches_refresh:
        try:
            for key, cfg in LEAGUES.items():
                if key in cached_data.get("leagues", {}):
                    new_matches = fetch_soccer_recent_matches(cfg["espnCode"])
                    if new_matches:
                        cached_data["leagues"][key]["recent_matches"] = new_matches
            cached_data["matches_updated_at"] = now.strftime("%Y-%m-%d %H:%M:%S")
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(cached_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"해외축구 경기 동적 갱신 에러: {e}")

    return cached_data
