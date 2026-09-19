"""
MLB (메이저리그 베이스볼) 데이터 서비스 모듈
공식 MLB Stats API 연동 및 캐싱
"""
import os
import json
from datetime import datetime, timedelta
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


def fetch_mlb_recent_matches():
    """MLB 공식 Stats API에서 최근 경기 결과, 오늘/내일 예정 경기, 실시간 LIVE 경기 조회"""
    try:
        now = datetime.now()
        start_d = (now - timedelta(days=2)).strftime("%Y-%m-%d")
        end_d = (now + timedelta(days=2)).strftime("%Y-%m-%d")

        url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate={start_d}&endDate={end_d}&hydrate=linescore,decisions,team,probablePitcher"
        r = requests.get(url, headers=HEADERS, timeout=6)
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

                # 이닝 / 상태 정보
                linescore = g.get("linescore", {})
                curr_inning = linescore.get("currentInningOrdinal", "")
                inning_half = linescore.get("inningHalf", "")
                
                is_live = state == "Live" or "In Progress" in detailed_state
                is_finished = state == "Final" or "Final" in detailed_state or "Game Over" in detailed_state
                is_upcoming = not is_live and not is_finished

                if is_live:
                    status_label = "LIVE"
                    half_kr = "초" if inning_half.lower() == "top" else ("말" if inning_half.lower() == "bottom" else "")
                    status_info = f"{curr_inning} {half_kr}".strip() or "진행중"
                elif is_finished:
                    status_label = "종료"
                    status_info = "종료"
                else:
                    status_label = "예정"
                    status_info = "예정"

                # 시간 표시
                game_datetime = g.get("gameDate", "")
                time_str = ""
                if len(game_datetime) >= 16:
                    time_str = game_datetime[11:16]

                matches.append({
                    "game_pk": game_pk,
                    "date": game_datetime[:10],
                    "time": time_str,
                    "status": status_label,
                    "status_info": status_info,
                    "away_id": away_team_id,
                    "away_team": away_name,
                    "away_eng": away.get("team", {}).get("name", ""),
                    "away_emblem": away_emblem,
                    "away_color": away_info.get("color", "#002D62"),
                    "away_score": away.get("score", "-") if (is_finished or is_live) else "-",
                    "away_win": away.get("isWinner", False),
                    "home_id": home_team_id,
                    "home_team": home_name,
                    "home_eng": home.get("team", {}).get("name", ""),
                    "home_emblem": home_emblem,
                    "home_color": home_info.get("color", "#BA0021"),
                    "home_score": home.get("score", "-") if (is_finished or is_live) else "-",
                    "home_win": home.get("isWinner", False),
                    "venue": g.get("venue", {}).get("name", ""),
                    "win_pitcher": winner_pitcher,
                    "lose_pitcher": loser_pitcher,
                    "save_pitcher": save_pitcher,
                    "pitcher_note": pitcher_note or "정규 경기",
                    "starter_note": starter_note,
                    "is_live": is_live,
                    "is_upcoming": is_upcoming,
                    "is_finished": is_finished
                })

        live_games = [m for m in matches if m["is_live"]]
        upcoming_games = [m for m in matches if m["is_upcoming"]]
        finished_games = sorted([m for m in matches if m["is_finished"]], key=lambda x: x["date"], reverse=True)

        return live_games + upcoming_games[:4] + finished_games[:10]
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
    """MLB 전체 데이터 조회 및 캐싱"""
    if not force_refresh and os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # 캐시 데이터가 유효하면 즉시 반환 (무료 서버 리소스 절약을 위해 자동 크롤링 방지)
            if "recent_matches" in data and "highlights" in data:
                return data
        except Exception as e:
            print(f"MLB 캐시 로드 에러: {e}")

    try:
        divisions, all_teams = fetch_mlb_standings()
        hitters, pitchers = fetch_mlb_leaders()
        hub = build_mlb_team_hub(all_teams, hitters, pitchers)
        recent_matches = fetch_mlb_recent_matches()
        highlights = fetch_mlb_highlights(recent_matches)

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
            "team_hub": hub,
            "recent_matches": recent_matches,
            "highlights": highlights
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
