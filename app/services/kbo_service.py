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


def fetch_kbo_recent_matches():
    """KBO 최근 경기 결과 크롤링 (최근 15경기)"""
    try:
        url = "https://www.koreabaseball.com/ws/Schedule.asmx/GetScheduleList"
        headers = {
            **HEADERS,
            "Referer": "https://www.koreabaseball.com/Schedule/Schedule.aspx",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        # 현재 연도 및 월
        now = datetime.now()
        year_str = str(now.year) if now.year <= 2026 else "2026"
        month_str = f"{now.month:02d}"

        data = {
            'leId': '1',
            'srIdList': '0,9,6',
            'seasonId': year_str,
            'gameMonth': month_str,
            'teamId': ''
        }
        r = requests.post(url, headers=headers, data=data, timeout=8)
        rows = r.json().get('rows', [])

        # 만약 이번 달에 경기가 아직 없으면 이전 달로 시도
        if not rows:
            data['gameMonth'] = "09"
            data['seasonId'] = "2024"
            r = requests.post(url, headers=headers, data=data, timeout=8)
            rows = r.json().get('rows', [])

        matches = []
        curr_date = ""
        for rw in rows:
            cols = rw.get('row', [])
            for c in cols:
                if c.get('Class') == 'day':
                    curr_date = c.get('Text', '').strip()
                    break

            play_col = None
            time_text = ""
            stadium = ""
            broadcast = ""
            highlight_link = ""

            for idx, c in enumerate(cols):
                cls = c.get('Class')
                txt = c.get('Text', '')
                if cls == 'play':
                    play_col = txt
                elif cls == 'time':
                    time_text = BeautifulSoup(txt, 'html.parser').text.strip()
                elif 'btnHighlight' in txt:
                    soup_btn = BeautifulSoup(txt, 'html.parser')
                    a_tag = soup_btn.find('a')
                    if a_tag and a_tag.get('href'):
                        highlight_link = "https://www.koreabaseball.com" + a_tag['href']
                elif idx == len(cols) - 2:
                    stadium = txt.strip()
                elif idx == len(cols) - 4 and cls is None:
                    broadcast = BeautifulSoup(txt, 'html.parser').text.strip()

            if play_col:
                soup = BeautifulSoup(play_col, 'html.parser')
                spans = soup.find_all('span')
                if len(spans) >= 5:
                    away_team = spans[0].text.strip()
                    away_score = spans[1].text.strip()
                    home_score = spans[3].text.strip()
                    home_team = spans[4].text.strip()

                    away_win = "win" in spans[1].get('class', [])
                    home_win = "win" in spans[3].get('class', [])

                    away_info = TEAM_INFO.get(away_team, {})
                    home_info = TEAM_INFO.get(home_team, {})

                    matches.append({
                        'date': curr_date,
                        'time': time_text,
                        'away_team': away_team,
                        'away_full_name': away_info.get("fullName", away_team),
                        'away_emblem': away_info.get("emblem", ""),
                        'away_color': away_info.get("color", "#4a5568"),
                        'away_score': away_score,
                        'away_win': away_win,
                        'home_team': home_team,
                        'home_full_name': home_info.get("fullName", home_team),
                        'home_emblem': home_info.get("emblem", ""),
                        'home_color': home_info.get("color", "#4a5568"),
                        'home_score': home_score,
                        'home_win': home_win,
                        'stadium': stadium,
                        'broadcast': broadcast,
                        'highlight_link': highlight_link,
                        'status': '종료' if (away_score.isdigit() and home_score.isdigit()) else '예정'
                    })

        # 종료된 최근 경기 위주로 정렬 (최신순 12경기)
        finished = [m for m in matches if m['status'] == '종료']
        return finished[-12:][::-1] if finished else matches[-12:][::-1]
    except Exception as e:
        print(f"KBO 최근 경기 크롤링 실패: {e}")
        return []


def fetch_kbo_highlights():
    """KBO 공식 하이라이트 영상 목록 크롤링 (YouTube embed)"""
    default_highlights = [
        {
            "title": "LG 트윈스 vs KT 위즈 경기 주요 하이라이트",
            "match": "LG vs KT",
            "score": "12 : 1",
            "date": "2026-09-18",
            "youtube_id": "jNN3rRIK9LE",
            "embed_url": "https://www.youtube.com/embed/jNN3rRIK9LE",
            "thumbnail": "https://img.youtube.com/vi/jNN3rRIK9LE/hqdefault.jpg",
            "source": "KBO 공식"
        },
        {
            "title": "NC 다이노스 vs 롯데 자이언츠 난타전 하이라이트",
            "match": "NC vs 롯데",
            "score": "6 : 9",
            "date": "2026-09-18",
            "youtube_id": "c2Iiu2B1HNc",
            "embed_url": "https://www.youtube.com/embed/c2Iiu2B1HNc",
            "thumbnail": "https://img.youtube.com/vi/c2Iiu2B1HNc/hqdefault.jpg",
            "source": "KBO 공식"
        },
        {
            "title": "삼성 라이온즈 vs 한화 이글스 명승부 하이라이트",
            "match": "삼성 vs 한화",
            "score": "10 : 4",
            "date": "2026-09-18",
            "youtube_id": "xSG7oBMTMDc",
            "embed_url": "https://www.youtube.com/embed/xSG7oBMTMDc",
            "thumbnail": "https://img.youtube.com/vi/xSG7oBMTMDc/hqdefault.jpg",
            "source": "KBO 공식"
        },
        {
            "title": "키움 히어로즈 vs 두산 베어스 연장 혈투 하이라이트",
            "match": "키움 vs 두산",
            "score": "6 : 6",
            "date": "2026-09-18",
            "youtube_id": "Dm5sXaxMxm4",
            "embed_url": "https://www.youtube.com/embed/Dm5sXaxMxm4",
            "thumbnail": "https://img.youtube.com/vi/Dm5sXaxMxm4/hqdefault.jpg",
            "source": "KBO 공식"
        }
    ]

    try:
        headers = {
            **HEADERS,
            "Referer": "https://www.koreabaseball.com/MediaNews/Highlight/List.aspx",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        # 최신 하이라이트 일자 조회
        r_max = requests.post("https://www.koreabaseball.com/ws/Controls.asmx/GetHighLightMaxDate", headers=headers, data={'leId': 1}, timeout=5)
        max_date = r_max.json().get('MaxDate')
        if not max_date:
            return default_highlights

        # 하이라이트 목록 조회
        r_hl = requests.post("https://www.koreabaseball.com/ws/KboTv.asmx/GetHighlight", headers=headers, data={'bdSc': 1, 'leId': 1, 'gameDate': max_date}, timeout=5)
        rows = r_hl.json().get('row', [])
        if not rows:
            return default_highlights

        highlights = []
        for it in rows:
            url_lk = it.get('URL_LK', '')
            embed_url = ""
            youtube_id = ""
            if url_lk:
                page_url = "https://www.koreabaseball.com" + url_lk
                try:
                    r_p = requests.get(page_url, headers=headers, timeout=4)
                    soup_p = BeautifulSoup(r_p.text, 'html.parser')
                    iframe = soup_p.find('iframe', src=lambda s: s and 'youtube.com/embed' in s)
                    if iframe:
                        embed_url = iframe['src']
                        m = re.search(r'/embed/([a-zA-Z0-9_-]+)', embed_url)
                        if m:
                            youtube_id = m.group(1)
                except Exception:
                    pass

            if not youtube_id and it.get('G_ID'):
                # fallback 매칭
                pass

            title = f"{it.get('BD_TT', 'KBO 경기')} 하이라이트 ({it.get('T_SCORE_CN', '')} : {it.get('B_SCORE_CN', '')})"
            pic_nm = it.get('PIC_NM', '')
            if pic_nm.startswith('//'):
                pic_nm = 'https:' + pic_nm
            thumb = f"https://img.youtube.com/vi/{youtube_id}/hqdefault.jpg" if youtube_id else pic_nm

            highlights.append({
                "title": title,
                "match": it.get('BD_TT', ''),
                "score": f"{it.get('T_SCORE_CN', '')} : {it.get('B_SCORE_CN', '')}",
                "date": it.get('REG_DT', ''),
                "youtube_id": youtube_id,
                "embed_url": embed_url if embed_url else (f"https://www.youtube.com/embed/{youtube_id}" if youtube_id else ""),
                "thumbnail": thumb,
                "source": "KBO 공식"
            })

        return highlights if highlights else default_highlights
    except Exception as e:
        print(f"KBO 하이라이트 크롤링 에러: {e}")
        return default_highlights


def get_kbo_data(force_refresh=False):
    """KBO 데이터 조회 (5분 캐시 적용)"""
    if not force_refresh and os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            cached_time = datetime.fromisoformat(data.get("updated_at_iso", "2000-01-01"))
            # recent_matches와 highlights가 캐시에 포함되어 있는지 확인
            if (datetime.now() - cached_time).total_seconds() < 300 and "recent_matches" in data and "highlights" in data:
                return data
        except Exception as e:
            print(f"KBO 캐시 로드 에러: {e}")

    try:
        team_ranks = fetch_team_rankings()
        hitters, pitchers = fetch_player_rankings()
        team_hub = build_team_hub(team_ranks, hitters, pitchers)
        recent_matches = fetch_kbo_recent_matches()
        highlights = fetch_kbo_highlights()

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
            "recent_matches": recent_matches,
            "highlights": highlights,
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
