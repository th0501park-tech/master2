"""
MLB (메이저리그 베이스볼) 데이터 서비스 모듈
공식 MLB Stats API 연동 및 캐싱
"""
import os
import json
from datetime import datetime, timezone, timedelta
import requests

KST = timezone(timedelta(hours=9))

def get_now_kst():
    """한국 표준시(KST, UTC+9) 기준 datetime 반환 (서버 타임존 무관)"""
    return datetime.now(timezone.utc).astimezone(KST).replace(tzinfo=None)

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
    113: {"name": "신시내티 레즈", "color": "#C6011F", "short": "CIN"},
    114: {"name": "클리블랜드 가디언스", "color": "#E31937", "short": "CLE"},
    115: {"name": "콜로라도 로키스", "color": "#333366", "short": "COL"},
    116: {"name": "디트로이트 타이거스", "color": "#0C2340", "short": "DET"},
    117: {"name": "휴스턴 애스트로스", "color": "#002D62", "short": "HOU"},
    118: {"name": "캔자스시티 로열스", "color": "#004687", "short": "KC"},
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
    158: {"name": "밀워키 브루어스", "color": "#12284B", "short": "MIL"}
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


def normalize_mlb_team_name(name):
    """네이버 스포츠와 MLB 팀명 정규화 매칭 헬퍼"""
    if not name:
        return ""
    n = name.replace(" ", "")
    if "화이트삭스" in n or "시카고W" in n:
        return "시카고W"
    if "다저스" in n or "LA다저스" in n:
        return "LA다저스"
    if "양키스" in n or "뉴욕양키스" in n:
        return "뉴욕양키스"
    if "메츠" in n or "뉴욕메츠" in n:
        return "뉴욕메츠"
    if "에인절스" in n or "LA에인절스" in n:
        return "LA에인절스"
    if "애슬레틱스" in n:
        return "애슬레틱스"
    if "탬파" in n or "템파" in n:
        return "탬파베이"
    suffixes = ["가디언스", "로키스", "타이거스", "애스트로스", "로열스", "내셔널스", "파이리츠", "파드리스", "매리너스", "자이언츠", "카디널스", "레이스", "레인저스", "블루제이스", "트윈스", "필리스", "브레이브스", "말린스", "브루어스", "다이아몬드백스", "오리올스", "레드삭스", "컵스", "레즈"]
    for s in suffixes:
        if n.endswith(s) and len(n) > len(s):
            return n[:-len(s)]
    return n


def fetch_naver_wbaseball_map():
    """네이버 스포츠 해외야구 API를 통해 실시간 네이버 경기 gameId 매핑 조회"""
    naver_map = {}
    try:
        now = get_now_kst()
        from_date = (now - timedelta(days=2)).strftime("%Y-%m-%d")
        to_date = (now + timedelta(days=2)).strftime("%Y-%m-%d")
        url = f"https://api-gw.sports.naver.com/schedule/games?fields=basic%2CsuperOrganId&fromDate={from_date}&toDate={to_date}&upperCategoryId=wbaseball&size=100"
        r = requests.get(url, headers=HEADERS, timeout=5)
        if r.status_code == 200:
            games = r.json().get("result", {}).get("games", [])
            for g in games:
                g_id = g.get("gameId", "")
                home = normalize_mlb_team_name(g.get("homeTeamName", ""))
                away = normalize_mlb_team_name(g.get("awayTeamName", ""))
                dt = g.get("gameDate", "")
                if g_id and home and away:
                    naver_map[(dt, home, away)] = g_id
                    naver_map[(home, away)] = g_id
    except Exception as e:
        print(f"네이버 해외야구 API 매핑 에러: {e}")
    return naver_map


def fetch_mlb_recent_matches():
    """MLB 공식 Stats API에서 최근 경기 결과, 오늘/내일 예정 경기, 실시간 LIVE 경기 조회"""
    try:
        now = get_now_kst()
        # 최근 2일(어제/그저께)부터 향후 2일(오늘/내일/모레)까지
        start_d = (now - timedelta(days=2)).strftime("%Y-%m-%d")
        end_d = (now + timedelta(days=2)).strftime("%Y-%m-%d")

        # 네이버 실시간 문자중계 gameId 매핑 사전 조회
        naver_map = fetch_naver_wbaseball_map()

        url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate={start_d}&endDate={end_d}&hydrate=linescore,decisions,team,probablePitcher"
        r = requests.get(url, headers=HEADERS, timeout=7)
        dates = r.json().get("dates", []) if r.status_code == 200 else []

        # 만약 해당 기간 경기가 없으면 2024년 9월 시즌 후반부 fallback
        if not dates:
            fb_url = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2024-09-17&endDate=2024-09-19&hydrate=linescore,decisions,team,probablePitcher"
            r_fb = requests.get(fb_url, headers=HEADERS, timeout=6)
            dates = r_fb.json().get("dates", []) if r_fb.status_code == 200 else []

        matches = []
        for d_item in dates:
            for g in d_item.get("games", []):
                game_pk = g.get("gamePk")
                status_obj = g.get("status", {})
                state = status_obj.get("abstractGameState", "")  # 'Live', 'Final', 'Preview'
                detailed_state = status_obj.get("detailedState", "Final")
                status_code = status_obj.get("statusCode", "")
                abstract_code = status_obj.get("abstractGameCode", "")
                det_lower = detailed_state.lower()

                away = g.get("teams", {}).get("away", {})
                home = g.get("teams", {}).get("home", {})
                away_team_id = away.get("team", {}).get("id")
                home_team_id = home.get("team", {}).get("id")

                away_info = MLB_TEAMS.get(away_team_id, {})
                home_info = MLB_TEAMS.get(home_team_id, {})

                away_name = away_info.get("name", away.get("team", {}).get("name", ""))
                home_name = home_info.get("name", home.get("team", {}).get("name", ""))

                away_emblem = f"https://www.mlbstatic.com/team-logos/{away_team_id}.svg" if away_team_id else ""
                home_emblem = f"https://www.mlbstatic.com/team-logos/{home_team_id}.svg" if home_team_id else ""

                decisions = g.get("decisions", {})
                winner_pitcher = decisions.get("winner", {}).get("fullName", "")
                loser_pitcher = decisions.get("loser", {}).get("fullName", "")
                save_pitcher = decisions.get("save", {}).get("fullName", "")

                pitcher_parts = []
                if winner_pitcher:
                    pitcher_parts.append(f"승: {winner_pitcher}")
                if loser_pitcher:
                    pitcher_parts.append(f"패: {loser_pitcher}")
                if save_pitcher:
                    pitcher_parts.append(f"세: {save_pitcher}")
                pitcher_note = " | ".join(pitcher_parts)

                # 선발투수
                away_prob = away.get("probablePitcher", {}).get("fullName", "")
                home_prob = home.get("probablePitcher", {}).get("fullName", "")
                starter_note = ""
                if away_prob or home_prob:
                    starter_note = f"선발: {away_prob or '미정'} vs {home_prob or '미정'}"

                # 시간 표시 (UTC -> KST 한국 시간 완벽 변환)
                raw_datetime = g.get("gameDate", "")
                kst_dt = None
                if raw_datetime:
                    try:
                        if raw_datetime.endswith("Z"):
                            utc_dt = datetime.strptime(raw_datetime, "%Y-%m-%dT%H:%M:%SZ")
                        else:
                            utc_dt = datetime.fromisoformat(raw_datetime.replace('Z', '+00:00')).replace(tzinfo=None)
                        kst_dt = utc_dt + timedelta(hours=9)
                    except Exception:
                        try:
                            utc_dt = datetime.strptime(raw_datetime[:16], "%Y-%m-%dT%H:%M")
                            kst_dt = utc_dt + timedelta(hours=9)
                        except Exception:
                            pass

                if kst_dt:
                    weekdays = ["월", "화", "수", "목", "금", "토", "일"]
                    date_display = f"{kst_dt.strftime('%m.%d')}({weekdays[kst_dt.weekday()]})"
                    time_str = kst_dt.strftime("%H:%M")
                    raw_date = kst_dt.strftime("%Y-%m-%d")
                else:
                    date_display = raw_datetime[:10]
                    time_str = raw_datetime[11:16] if len(raw_datetime) >= 16 else ""
                    raw_date = raw_datetime[:10]

                # 이닝 / 상태 정보 파싱
                linescore = g.get("linescore", {})
                curr_inning_num = linescore.get("currentInning")
                curr_inning = linescore.get("currentInningOrdinal", "")
                inning_half = linescore.get("inningHalf", "")
                outs = linescore.get("outs")
                balls = linescore.get("balls")
                strikes = linescore.get("strikes")

                # 실시간 수비(투수) / 공격(타자)
                defense = linescore.get("defense", {})
                offense = linescore.get("offense", {})
                curr_pitcher = defense.get("pitcher", {}).get("fullName", "")
                curr_batter = offense.get("batter", {}).get("fullName", "")

                # 취소, 종료, 라이브 정밀 판정
                is_cancelled = (
                    "postpon" in det_lower or 
                    "cancel" in det_lower or 
                    "suspended" in det_lower or 
                    status_code in ["DI", "DR", "POSTPONED", "CANCELLED", "SUSPENDED"]
                )
                is_finished = not is_cancelled and (
                    state == "Final" or 
                    abstract_code == "F" or 
                    status_code in ["F", "O", "CR", "FR"] or 
                    "final" in det_lower or 
                    "game over" in det_lower or 
                    "completed" in det_lower
                )
                is_live = not is_cancelled and not is_finished and (
                    state == "Live" or 
                    abstract_code == "L" or 
                    status_code in ["I", "M", "PW", "PR"] or 
                    "in progress" in det_lower or 
                    "warmup" in det_lower
                )

                # 방어 로직: 경기 시작(KST) 후 4.5시간 이상 경과한 경기는 종료로 안전 전환
                if is_live and kst_dt:
                    if (now - kst_dt).total_seconds() > 4.5 * 3600:
                        is_live = False
                        is_finished = True

                is_upcoming = not is_live and not is_finished and not is_cancelled

                # 스코어 처리 (진행중이거나 종료된 경기면 숫자, 미진행이면 '-')
                raw_away_score = away.get("score")
                raw_home_score = home.get("score")
                if is_finished or is_live:
                    away_score_val = raw_away_score if raw_away_score is not None else 0
                    home_score_val = raw_home_score if raw_home_score is not None else 0
                else:
                    away_score_val = "-"
                    home_score_val = "-"

                away_win = away.get("isWinner", False)
                home_win = home.get("isWinner", False)
                if is_finished and not away_win and not home_win and away_score_val != "-" and home_score_val != "-":
                    if away_score_val > home_score_val:
                        away_win = True
                    elif home_score_val > away_score_val:
                        home_win = True

                # 상태 텍스트 한국어 정밀 매핑
                if is_cancelled:
                    status_label = "취소"
                    status_info = "우천취소" if "rain" in det_lower else (detailed_state or "경기취소")
                elif is_live:
                    status_label = "LIVE"
                    half_kr = "초" if inning_half.lower() == "top" else ("말" if inning_half.lower() == "bottom" else "")
                    if curr_inning_num:
                        inning_str = f"{curr_inning_num}회{half_kr}"
                    elif curr_inning:
                        clean_ord = curr_inning.replace('th', '').replace('st', '').replace('nd', '').replace('rd', '')
                        inning_str = f"{clean_ord}회{half_kr}"
                    else:
                        inning_str = "진행중"

                    if outs is not None and outs >= 0 and inning_str != "진행중":
                        status_info = f"{inning_str} {outs}아웃"
                    else:
                        status_info = inning_str

                    if "warmup" in det_lower:
                        status_info = "시작전 (몸푸는중)"

                    if not pitcher_note and curr_pitcher:
                        pitcher_note = f"투수: {curr_pitcher}"
                elif is_finished:
                    status_label = "종료"
                    status_info = "종료"
                else:
                    status_label = "예정"
                    status_info = f"예정 ({time_str})" if time_str else "예정"

                h_norm = normalize_mlb_team_name(home_name)
                a_norm = normalize_mlb_team_name(away_name)
                naver_game_id = naver_map.get((raw_date, h_norm, a_norm)) or naver_map.get((h_norm, a_norm)) or ""

                matches.append({
                    "game_id": naver_game_id or str(game_pk),
                    "naver_game_id": naver_game_id,
                    "game_pk": game_pk,
                    "naver_relay_url": f"https://m.sports.naver.com/game/{naver_game_id}/relay" if naver_game_id else "https://m.sports.naver.com/wbaseball/schedule/index",
                    "gameday_url": f"https://www.mlb.com/gameday/{game_pk}",
                    "date": date_display,
                    "raw_date": raw_date,
                    "time": time_str,
                    "status": status_label,
                    "status_info": status_info,
                    "away_id": away_team_id,
                    "away_team": away_name,
                    "away_eng": away.get("team", {}).get("name", ""),
                    "away_emblem": away_emblem,
                    "away_color": away_info.get("color", "#002D62"),
                    "away_score": away_score_val,
                    "away_win": away_win,
                    "home_id": home_team_id,
                    "home_team": home_name,
                    "home_eng": home.get("team", {}).get("name", ""),
                    "home_emblem": home_emblem,
                    "home_color": home_info.get("color", "#BA0021"),
                    "home_score": home_score_val,
                    "home_win": home_win,
                    "venue": g.get("venue", {}).get("name", ""),
                    "win_pitcher": winner_pitcher,
                    "lose_pitcher": loser_pitcher,
                    "save_pitcher": save_pitcher,
                    "current_pitcher": curr_pitcher,
                    "current_batter": curr_batter,
                    "outs": outs,
                    "balls": balls,
                    "strikes": strikes,
                    "pitcher_note": pitcher_note or "정규 경기",
                    "starter_note": starter_note,
                    "is_live": is_live,
                    "is_upcoming": is_upcoming,
                    "is_finished": is_finished
                })

        live_games = sorted([m for m in matches if m["is_live"]], key=lambda x: (x.get("raw_date", ""), x.get("time", "")))
        upcoming_games = sorted([m for m in matches if m["is_upcoming"]], key=lambda x: (x.get("raw_date", ""), x.get("time", "")))
        finished_games = sorted([m for m in matches if m["is_finished"]], key=lambda x: (x.get("raw_date", ""), x.get("time", "")), reverse=True)

        return live_games + upcoming_games[:16] + finished_games[:25]
    except Exception as e:
        print(f"MLB 최근 경기 조회 실패: {e}")
        return []


def fetch_mlb_highlights(recent_matches=None):
    """MLB 공식 Film Room / Cuts 영상 목록 조회 (mp4 직링크 바로 재생)"""
    default_highlights = [
        {
            "title": "오클랜드 vs 시카고 컵스 경기 종합 하이라이트",
            "match": "Athletics vs. Cubs",
            "score": "5 : 3",
            "date": "2024-09-18",
            "video_url": "https://mlb-cuts-diamond.mlb.com/FORGE/2024/2024-09/18/86028ed4-e4cdb89a-1313bd2f-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
            "thumbnail": "https://img.mlbstatic.com/mlb-images/image/upload/w_1920,h_1080,f_jpg,c_fill,g_auto/mlb/y5o0hn51ptf0d5cqzrxx.jpg",
            "duration": "03:11",
            "source": "MLB Film Room",
            "type": "mp4"
        },
        {
            "title": "LA 다저스 오타니 쇼헤이 역사적인 50-50 대기록 하이라이트",
            "match": "Dodgers vs. Marlins",
            "score": "20 : 4",
            "date": "2024-09-19",
            "video_url": "https://mlb-cuts-diamond.mlb.com/FORGE/2024/2024-09/19/d6c8e312-32a8ba71-d101a89f-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
            "thumbnail": "https://images.unsplash.com/photo-1508344928928-7165b67de128?w=640&auto=format&fit=crop&q=80",
            "duration": "04:25",
            "source": "MLB Film Room",
            "type": "mp4"
        },
        {
            "title": "샌디에이고 파드리스 김하성 결승 적시타 및 호수비 모음",
            "match": "Padres vs. Giants",
            "score": "4 : 2",
            "date": "2024-09-15",
            "video_url": "https://mlb-cuts-diamond.mlb.com/FORGE/2024/2024-09/18/86028ed4-e4cdb89a-1313bd2f-csvm-diamondgcp-asset_1280x720_59_4000K.mp4",
            "thumbnail": "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?w=640&auto=format&fit=crop&q=80",
            "duration": "02:40",
            "source": "MLB Film Room",
            "type": "mp4"
        }
    ]

    try:
        pks = []
        if recent_matches:
            pks = [m["game_pk"] for m in recent_matches[:3] if m.get("game_pk")]
        if not pks:
            pks = [746831]

        highlights = []
        for pk in pks:
            url = f"https://statsapi.mlb.com/api/v1/game/{pk}/content"
            r = requests.get(url, headers=HEADERS, timeout=5)
            if r.status_code == 200:
                items = r.json().get("highlights", {}).get("highlights", {}).get("items", [])
                for it in items[:3]:
                    playbacks = it.get("playbacks", [])
                    mp4_url = ""
                    for pb in playbacks:
                        if "mp4" in pb.get("name", "").lower() and "1280x720" in pb.get("url", ""):
                            mp4_url = pb.get("url")
                            break
                    if not mp4_url:
                        for pb in playbacks:
                            if "mp4" in pb.get("name", "").lower():
                                mp4_url = pb.get("url")
                                break

                    cuts = it.get("image", {}).get("cuts", [])
                    thumb = cuts[0].get("src", "") if cuts else ""

                    if mp4_url:
                        highlights.append({
                            "title": it.get("title", "MLB 경기 하이라이트"),
                            "description": it.get("description", ""),
                            "match": it.get("title", ""),
                            "date": it.get("date", "")[:10],
                            "video_url": mp4_url,
                            "thumbnail": thumb,
                            "duration": it.get("duration", "02:30"),
                            "source": "MLB Film Room",
                            "type": "mp4"
                        })

        return highlights if highlights else default_highlights
    except Exception as e:
        print(f"MLB 하이라이트 영상 조회 실패: {e}")
        return default_highlights


def get_mlb_data(force_refresh=False):
    """
    MLB 전체 데이터 조회 및 캐싱
    - 전체 크롤링(순위, 하이라이트 등): 30분 TTL 캐싱
    - 경기 일정/LIVE 스코어(recent_matches): LIVE 경기 시 20초, 일반 시 90초 주기로 동적 갱신
    - 타임존 독립적(KST 기준) 운영 및 미래 타임스탬프 오류 방지
    """
    cached_data = None
    cache_valid = False
    now = get_now_kst()

    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
            if "recent_matches" in cached_data and "highlights" in cached_data:
                cache_valid = True
        except Exception as e:
            print(f"MLB 캐시 로드 에러: {e}")

    # 1. 전체 데이터 갱신 필요 여부 판단 (기본 30분 TTL)
    need_full_refresh = force_refresh or not cache_valid
    if cache_valid and not need_full_refresh:
        updated_at_str = cached_data.get("updated_at")
        if updated_at_str:
            try:
                updated_time = datetime.strptime(updated_at_str, "%Y-%m-%d %H:%M:%S")
                diff = (now - updated_time).total_seconds()
                # 30분 초과 또는 비정상적인 미래 타임스탬프(음수) 시 전체 갱신
                if diff > 1800 or diff < 0:
                    need_full_refresh = True
            except Exception:
                need_full_refresh = True

    if need_full_refresh:
        try:
            divisions, all_teams = fetch_mlb_standings()
            hitters, pitchers = fetch_mlb_leaders()
            hub = build_mlb_team_hub(all_teams, hitters, pitchers)
            recent_matches = fetch_mlb_recent_matches()
            highlights = fetch_mlb_highlights(recent_matches)

            data = {
                "sports": "mlb",
                "title": "MLB 메이저리그 (Major League Baseball)",
                "updated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at_iso": now.isoformat(),
                "matches_updated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
                "divisions": divisions,
                "all_teams": all_teams,
                "hitters": hitters,
                "pitchers": pitchers,
                "team_hub": hub,
                "recent_matches": recent_matches,
                "highlights": highlights
            }

            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return data
        except Exception as e:
            print(f"MLB 수집 에러: {e}")
            if cached_data:
                return cached_data
            raise e

    # 2. 캐시가 유효한 경우: 경기 결과 및 LIVE 스코어의 동적 갱신 여부 확인!
    has_live = any(m.get("is_live") for m in cached_data.get("recent_matches", []))
    matches_updated_at = cached_data.get("matches_updated_at")
    need_matches_refresh = False

    if has_live:
        if not matches_updated_at:
            need_matches_refresh = True
        else:
            try:
                m_time = datetime.strptime(matches_updated_at, "%Y-%m-%d %H:%M:%S")
                diff = (now - m_time).total_seconds()
                # LIVE 진행 중: 20초 이상 경과했거나 미래 타임스탬프면 갱신
                if diff >= 20 or diff < 0:
                    need_matches_refresh = True
            except Exception:
                need_matches_refresh = True
    else:
        if not matches_updated_at:
            need_matches_refresh = True
        else:
            try:
                m_time = datetime.strptime(matches_updated_at, "%Y-%m-%d %H:%M:%S")
                diff = (now - m_time).total_seconds()
                # LIVE 없을 때: 90초 이상 경과했거나 미래 타임스탬프면 갱신
                if diff >= 90 or diff < 0:
                    need_matches_refresh = True
            except Exception:
                need_matches_refresh = True

    if need_matches_refresh:
        try:
            new_matches = fetch_mlb_recent_matches()
            if new_matches:
                cached_data["recent_matches"] = new_matches
                cached_data["matches_updated_at"] = now.strftime("%Y-%m-%d %H:%M:%S")
                with open(CACHE_FILE, "w", encoding="utf-8") as f:
                    json.dump(cached_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"MLB 경기 동적 갱신 에러: {e}")

    return cached_data
