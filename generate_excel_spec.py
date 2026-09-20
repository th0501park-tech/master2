"""
SPORTS HUB - 프로그램 명세서, 프로세스 흐름도, 소스 구성도 Excel 생성 스크립트
"""
import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()
# 기본 시트 제거
wb.remove(wb.active)

# 스타일 정의
HEADER_FILL = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid") # Navy Blue
SUBHEADER_FILL = PatternFill(start_color="3B82F6", end_color="3B82F6", fill_type="solid") # Royal Blue
SECTION_FILL = PatternFill(start_color="DBEAFE", end_color="DBEAFE", fill_type="solid") # Light Blue
ZEBRA_FILL = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid") # Slate light
HIGHLIGHT_FILL = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid") # Amber light

HEADER_FONT = Font(name="Malgun Gothic", size=11, bold=True, color="FFFFFF")
TITLE_FONT = Font(name="Malgun Gothic", size=16, bold=True, color="1E3A8A")
SUBTITLE_FONT = Font(name="Malgun Gothic", size=11, italic=True, color="475569")
BOLD_FONT = Font(name="Malgun Gothic", size=10, bold=True, color="0F172A")
REGULAR_FONT = Font(name="Malgun Gothic", size=10, color="1E293B")
CODE_FONT = Font(name="Consolas", size=9, color="0F172A")

THIN_BORDER_SIDE = Side(style="thin", color="CBD5E1")
THIN_BORDER = Border(left=THIN_BORDER_SIDE, right=THIN_BORDER_SIDE, top=THIN_BORDER_SIDE, bottom=THIN_BORDER_SIDE)
HEADER_BORDER = Border(left=THIN_BORDER_SIDE, right=THIN_BORDER_SIDE, top=Side(style="medium", color="1E3A8A"), bottom=Side(style="medium", color="1E3A8A"))

ALIGN_CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
ALIGN_LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)
ALIGN_RIGHT = Alignment(horizontal="right", vertical="center", wrap_text=True)

def apply_sheet_styling(ws, title_text, col_widths, headers, data_rows, status_col_idx=None):
    # 1. 제목 행
    ws.merge_cells("A1:G1" if len(headers) >= 7 else f"A1:{get_column_letter(len(headers))}1")
    title_cell = ws["A1"]
    title_cell.value = f"📊 {title_text}"
    title_cell.font = TITLE_FONT
    title_cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[1].height = 40

    # 2. 부제목 / 설명
    ws.merge_cells("A2:G2" if len(headers) >= 7 else f"A2:{get_column_letter(len(headers))}2")
    sub_cell = ws["A2"]
    sub_cell.value = f"프로젝트: SPORTS HUB (실시간 스포츠 종합 대시보드)  |  작성일자: 2026-09-20  |  버전: v2.4.0"
    sub_cell.font = SUBTITLE_FONT
    sub_cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[2].height = 20

    # 3. 빈 행 (여백)
    ws.row_dimensions[3].height = 10

    # 4. 헤더 행
    header_row = 4
    ws.row_dimensions[header_row].height = 28
    for col_idx, h in enumerate(headers, start=1):
        cell = ws.cell(row=header_row, column=col_idx, value=h)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = ALIGN_CENTER
        cell.border = HEADER_BORDER

    # 5. 데이터 행
    current_row = header_row + 1
    for r_idx, row in enumerate(data_rows, start=current_row):
        ws.row_dimensions[r_idx].height = 24
        is_zebra = (r_idx % 2 == 0)
        for c_idx, val in enumerate(row, start=1):
            cell = ws.cell(row=r_idx, column=c_idx, value=val)
            cell.font = REGULAR_FONT
            cell.border = THIN_BORDER
            
            # 셀 채우기
            if is_zebra:
                cell.fill = ZEBRA_FILL

            # 정렬 규칙
            if c_idx == 1:
                cell.alignment = ALIGN_CENTER
            elif isinstance(val, (int, float)):
                cell.alignment = ALIGN_RIGHT
            elif any(kw in str(val) for kw in ["http", "/", ".py", ".html", ".js", ".css"]):
                cell.font = CODE_FONT
                cell.alignment = ALIGN_LEFT
            else:
                cell.alignment = ALIGN_LEFT

    # 열 너비 설정
    for col_idx, width in enumerate(col_widths, start=1):
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    ws.views.sheetView[0].showGridLines = True


# ==============================================================================
# Sheet 1: 표지 및 프로젝트 개요
# ==============================================================================
ws1 = wb.create_sheet(title="01_프로젝트개요")
ws1.views.sheetView[0].showGridLines = True
ws1.column_dimensions["A"].width = 6
ws1.column_dimensions["B"].width = 24
ws1.column_dimensions["C"].width = 60

# 메인 타이틀
ws1.merge_cells("B2:C2")
c = ws1["B2"]
c.value = "🏆 SPORTS HUB 시스템 설계 및 프로그램 명세서"
c.font = Font(name="Malgun Gothic", size=18, bold=True, color="1E3A8A")
c.alignment = ALIGN_CENTER
ws1.row_dimensions[2].height = 50

overview_items = [
    ("프로젝트명", "SPORTS HUB - 실시간 스포츠 종합 순위 & 기록 대시보드"),
    ("시스템 정의", "KBO 한국프로야구, K리그(1·2), 해외축구 5대리그, MLB 메이저리그 4대 스포츠의 실시간 스코어, 순위, 선수 기록, 공식 하이라이트 영상 및 네이버스포츠 실시간 문자중계를 단일 웹 허브에서 통합 제공하는 올인원 대시보드"),
    ("시스템 버전", "v2.4.0 (2026.09.20 업데이트)"),
    ("작성 일자", "2026년 09월 20일"),
    ("주요 대상 종목", "1) KBO 프로야구  2) K리그 1 / K리그 2  3) 해외축구 (EPL, 라리가, 분데스리가, UCL, UEL)  4) MLB 메이저리그"),
    ("아키텍처 구조", "FastAPI 비동기 웹 프레임워크 기반 SSR(Jinja2) + Vanilla JS 클라이언트 Hydration + 파일 기반 캐싱 레이어"),
    ("백엔드 기술 스택", "Python 3.14, FastAPI 0.115+, Uvicorn(ASGI), Jinja2 템플릿 엔진, Requests, BeautifulSoup4, LXML"),
    ("프론트엔드 기술 스택", "TailwindCSS (CDN 기반 모던 스타일링), FontAwesome 6, Vanilla JavaScript (ES6+), YouTube Embed API, Iframe Modal"),
    ("데이터 연동 소스", "네이버 스포츠 KBO/K리그/해외야구 API, K리그 공식 데이터 포털, MLB Stats API, ESPN Soccer Scoreboard API, Goal.com"),
    ("캐싱 및 성능 최적화", "서버 타임존(UTC/KST) 무결성 표준화(get_now_kst) 및 diff<0 무효화 안전장치, 스마트 캐시 갱신(LIVE 시 25초 주기 실시간 fetch), 파일 캐시, Facade 지연 로딩"),
    ("최근 주요 개선사항", "1) 서버 타임존(Render UTC vs 로컬 KST) 불일치 캐시 프리징 버그 완전 해결(get_now_kst 표준화 및 음수 diff 즉시 갱신 가드 탑재)\n2) MLB 실시간 LIVE 판정 정밀화: statusCode(O, F, CR, FR) 및 Game Over 즉시 종료 처리로 끝난 경기 고정 현상 원천 해결\n3) 공식 linescore 기반 현재 마운드 투수(current_pitcher) 및 타석 타자(current_batter) 실시간 매치업 표출 & 이닝 한국어 포맷팅(8회초 1아웃)\n4) 당일 전 경기 커버(종료 경기 25개, 예정 경기 16개 확대) 및 LIVE 경기 25초/비경기 90초 스마트 자동 백그라운드 폴링\n5) 실시간 중계 모달(live-relay-modal) 단독 팝업화 & 네이버 새 창 / MLB 3D게임데이 바로가기 버튼 제공\n6) F12 브라우저 개발자도구 콘솔 오류 3종(iframe onload, ESPN artwork 401, Tailwind 경고) 0(Zero) 무결성 확보"),
    ("운영 및 배포 환경", "로컬(Uvicorn 로컬 호스트 8000번 포트), 클라우드 PaaS(Render.com Procfile / render.yaml 사전 구성)"),
    ("저장소 (Git)", "https://github.com/th0501park-tech/master2.git (main branch)")
]

ws1.row_dimensions[4].height = 26
ws1.cell(row=4, column=2, value="구분 항목").fill = HEADER_FILL
ws1.cell(row=4, column=2).font = HEADER_FONT
ws1.cell(row=4, column=2).alignment = ALIGN_CENTER
ws1.cell(row=4, column=2).border = HEADER_BORDER

ws1.cell(row=4, column=3, value="상세 내용").fill = HEADER_FILL
ws1.cell(row=4, column=3).font = HEADER_FONT
ws1.cell(row=4, column=3).alignment = ALIGN_CENTER
ws1.cell(row=4, column=3).border = HEADER_BORDER

for idx, (k, v) in enumerate(overview_items, start=5):
    ws1.row_dimensions[idx].height = 36 if "\n" in v else 24
    c_k = ws1.cell(row=idx, column=2, value=k)
    c_k.font = BOLD_FONT
    c_k.fill = SECTION_FILL
    c_k.alignment = ALIGN_CENTER
    c_k.border = THIN_BORDER
    
    c_v = ws1.cell(row=idx, column=3, value=v)
    c_v.font = REGULAR_FONT
    c_v.alignment = ALIGN_LEFT
    c_v.border = THIN_BORDER


# ==============================================================================
# Sheet 2: 프로그램 명세서 (Program Specifications)
# ==============================================================================
ws2 = wb.create_sheet(title="02_프로그램명세서")
prog_headers = ["NO", "모듈/파일경로", "프로그램명", "주요 함수/기능", "역할 및 동작 설명", "입력 데이터", "출력/반환 데이터", "비고"]
prog_widths = [6, 28, 20, 24, 45, 20, 22, 16]
prog_data = [
    (1, "run.py", "웹서버 엔트리포인트", "main", "Uvicorn 서버 인스턴스 기동 (로컬 127.0.0.1:8000 및 핫리로드 지원)", "환경변수(HOST, PORT)", "ASGI Server Process", "로컬 개발용"),
    (2, "app/main.py", "FastAPI 메인 컨트롤러", "index_page, health_check", "HTTP 요청 라우팅, 4대 스포츠 데이터 종합 수집, Jinja2 템플릿 SSR 렌더링", "HTTP Request (GET /)", "HTML 웹페이지 (SSR)", "FastAPI Core"),
    (3, "app/services/kbo_service.py", "KBO 데이터 수집 엔진", "get_kbo_data\nfetch_kbo_recent_matches\nfetch_team_rankings\nfetch_player_rankings", "네이버 스포츠 KBO API 연동: 실시간 이닝/스코어, 승·패전 결정투수, 선발투수 예고, gameId 매핑, 순위 및 리더보드", "force_refresh (bool)", "KBO Data Dict (JSON)", "네이버 gameId 연동"),
    (4, "app/services/kleague_service.py", "K리그 데이터 수집 엔진", "get_kleague_data\nfetch_kleague_recent_matches\nfetch_naver_kfootball_map", "K리그 공식 포털 + 네이버 kfootball API: 공식 상태코드(1S/2S/HT/ET/PK) 실시간 분(Minute) 인식, 실시간 스코어, gameId 매핑", "league_id (1 or 2)", "KLeague Data Dict (JSON)", "네이버 kfootball 연동"),
    (5, "app/services/mlb_service.py", "MLB 데이터 수집 엔진", "get_mlb_data\nfetch_mlb_recent_matches\nfetch_mlb_standings", "MLB Stats API 연동: 30개 구단 순위, 실시간 이닝 스코어, 승·패·세이브 결정투수, 선발투수 예고, game_id 매핑, 개인기록", "force_refresh (bool)", "MLB Data Dict (JSON)", "Stats API hydrate 적용"),
    (6, "app/services/overseas_soccer_service.py", "해외축구 데이터 수집 엔진", "get_overseas_soccer_data\nfetch_soccer_recent_matches\nfetch_standings_espn", "ESPN Scoreboard & 캘린더 연동: 5대리그 순위, UTC->KST 한국시간 자동 변환, 실시간 분(Clock) 정보, 최근 종료 경기", "espn_code (str)", "Overseas Soccer Dict (JSON)", "KST 변환 & 팀명 한글화"),
    (7, "app/templates/index.html", "메인 대시보드 뷰 템플릿", "Jinja2 템플릿 & 모달", "상단 경기결과 & 스코어보드 그리드, [실시간 중계확인] 버튼 분기, live-relay-modal(네이버 문자중계 뷰어), 하단 영상 플레이어", "FastAPI 전달 Context", "HTML 웹 브라우저 렌더링", "실시간 중계 모달 포함"),
    (8, "app/static/js/main.js", "클라이언트 SPA 제어 스크립트", "switchSport, setMatchFilter, openLiveRelayModal, closeLiveRelayModal", "종목 탭 전환, 원클릭 상태 필터링, 마이팀 로컬스토리지 저장, 네이버스포츠 실시간 문자중계 모달 제어, 영상 Facade 재생", "사용자 클릭 이벤트", "DOM 동적 업데이트", "반응형 인터랙션"),
    (9, "app/static/css/style.css", "스타일시트 및 테마", "Tailwind 보조 커스텀 스타일", "경기 상태 필터 칩 액티브 스타일, 다크모드 대응, 라이브 뱃지 펄스 애니메이션, 마이팀 골드 테두리", "CSS Rules", "화면 시각 디자인", "다크/라이트 모드 지원"),
    (10, "cache/*.json", "로컬 데이터 캐시 엔진", "kbo, kleague, mlb, overseas", "네트워크 지연 방지 및 외부 API 호출 쿼터 절약을 위한 로컬 파일 기반 JSON 캐시 (TTL 5~15분)", "API Raw Response", "가공된 JSON 파일", "고속 로딩 보장")
]
apply_sheet_styling(ws2, "프로그램 명세서 (Program Specifications)", prog_widths, prog_headers, prog_data)


# ==============================================================================
# Sheet 3: 프로세스 흐름도 (Process Flow)
# ==============================================================================
ws3 = wb.create_sheet(title="03_프로세스흐름도")
flow_headers = ["단계 (Phase)", "프로세스 단계명", "수행 주체 (Actor)", "상세 동작 및 비즈니스 로직", "입력 / 데이터", "출력 / 결과", "예외 및 Fallback 처리"]
flow_widths = [14, 22, 20, 48, 22, 22, 28]
flow_data = [
    ("1. 초기 기동", "서버 시작 및 캐시 준비", "Uvicorn / FastAPI (main.py)", "서버 구동 시 cache/ 디렉토리 내 4대 스포츠 캐시 파일 존재 여부 및 최신 여부 자동 검증", "run.py 실행", "캐시 준비 완료 로그", "캐시 없을 시 즉시 백그라운드 데이터 수집"),
    ("2. 클라이언트 요청", "메인 대시보드 페이지 요청", "사용자 브라우저", "사용자가 웹 브라우저를 통해 http://127.0.0.1:8000/ 접속", "HTTP GET /", "서버 요청 전달", "서버 미응답 시 500 에러 핸들링"),
    ("3. 서버 데이터 취합", "종합 스포츠 데이터 로드", "FastAPI (index_page 라우트)", "KBO, K리그, 해외축구, MLB 각 서비스 모듈을 병렬 호출하여 최신 캐시 데이터 로드", "get_*_data() 호출", "종합 딕셔너리 객체", "외부 API 실패 시 최근 캐시 데이터 fallback"),
    ("4. SSR 초기 렌더링", "HTML 템플릿 바인딩", "Jinja2 템플릿 엔진", "index.html에 최신 경기 결과(상단), LIVE 상태별 [실시간 중계확인]/[하이라이트] 버튼 분기, 하단 영상 바인딩 후 전송", "Context Data + index.html", "완성된 HTML 스트림", "파싱 오류 방지 escape 처리"),
    ("5. 클라이언트 동기화", "데이터 Hydration 및 세팅", "main.js (DOMContentLoaded)", "window.INITIAL_DATA에 서버 데이터 보관, 로컬스토리지에서 마이팀(선호 구단) 및 테마 상태 복원", "localStorage (myTeam, theme)", "마이팀 뱃지 및 테마 반영", "로컬스토리지 비어있을 시 기본값 설정"),
    ("6. 경기 상태 필터링", "실시간/최근/예정 필터링", "main.js (setMatchFilter)", "사용자가 [전체], [🔴 LIVE], [최근 결과], [금주 예정] 칩 클릭 시 status 플래그에 따라 카드 동적 렌더링", "currentMatchFilter ('live' 등)", "필터링된 스코어보드 갱신", "해당 경기 없을 시 '일정 없음' 안내 카드 표시"),
    ("7. 종목 및 리그 전환", "SPA 동적 콘텐츠 스위칭", "main.js (switchSport / switchSub)", "페이지 새로고침 없이 상단 탭 클릭 시 KBO, K리그(1/2), 해외축구(5대리그), MLB 화면 즉시 전환", "sportType, subType", "해당 종목 경기/순위/영상 표시", "데이터 부재 시 준비 중 안내"),
    ("8. 마이팀(구단) 연동", "선호 구단 등록 및 우선 노출", "main.js (toggleFavoriteTeam)", "카드 내 ★ 별표 클릭 시 선호 구단으로 등록, 해당 구단 경기를 최상단 정렬 및 골드 테두리 강조", "teamName, sportKey", "localStorage 저장 및 카드 재정렬", "언제든 별표 재클릭으로 해제 가능"),
    ("9. 실시간 문자중계", "네이버스포츠 모달 렌더링", "main.js (openLiveRelayModal)", "LIVE 경기 카드의 [⚡ 실시간 중계확인] 클릭 시 네이버스포츠 실시간 문자중계 모달 즉시 팝업 (볼카운트/투구추적/이닝기록)", "game_id, team info", "Iframe 인라인 렌더링 및 새 창 링크", "새 창으로 보기 대체 링크 제공"),
    ("10. 영상 지연 로딩", "Facade 기반 하이라이트 재생", "main.js (Facade & Iframe)", "종료 경기 카드의 [하이라이트] 클릭 시 Facade 포스터 -> YouTube Iframe 동적 전환 및 자동재생", "클릭 이벤트", "YouTube / MP4 비디오 스트리밍", "유튜브 404 시 CDN 백업 포스터 대체"),
    ("11. 주기적 데이터 갱신", "백그라운드 캐시 리프레시", "Background Scheduler / API", "경기 진행 시간대(라이브 경기 발생 시) 캐시 만료 주기에 맞춰 외부 API 최신 스코어 및 이닝 갱신", "Timer / Scheduler Event", "cache/*.json 갱신", "네트워크 단절 시 기존 캐시 보존")
]
apply_sheet_styling(ws3, "시스템 프로세스 흐름도 (System Process Flow)", flow_widths, flow_headers, flow_data)


# ==============================================================================
# Sheet 4: 소스 구성도 (Source Architecture)
# ==============================================================================
ws4 = wb.create_sheet(title="04_소스구성도")
src_headers = ["계층 (Layer)", "디렉토리 / 파일명", "모듈 구분", "파일 설명 및 역할", "주요 구성 요소", "종속성 / 기술 라이브러리"]
src_widths = [16, 28, 16, 42, 35, 25]
src_data = [
    ("루트 환경", "run.py", "실행 파일", "애플리케이션 진입점 및 로컬 ASGI 웹서버 기동", "uvicorn.run, HOST, PORT 설정", "uvicorn, os"),
    ("루트 환경", "Procfile / render.yaml", "배포 설정", "Render.com 등 클라우드 PaaS 배포 규격 정의", "web: uvicorn app.main:app, build script", "PaaS Runtime"),
    ("루트 환경", "requirements.txt", "의존성 정의", "프로젝트 실행에 필요한 Python 패키지 목록", "fastapi, uvicorn, jinja2, requests, bs4 등", "pip / PyPI"),
    ("Application Layer", "app/main.py", "FastAPI App", "HTTP 요청 핸들러, 정적 파일 마운트, 템플릿 라우팅", "FastAPI instance, index_page route", "fastapi, jinja2"),
    ("Business Layer", "app/services/kbo_service.py", "서비스 모듈", "KBO 프로야구 실시간 스코어, 순위, 투수기록 수집", "fetch_kbo_recent_matches, fetch_team_rankings", "requests, json, datetime"),
    ("Business Layer", "app/services/kleague_service.py", "서비스 모듈", "K리그1·2 공식 일정, 순위, 득점순위, 금주/지난주 필터", "fetch_kleague_recent_matches, get_team_meta", "requests, json, datetime"),
    ("Business Layer", "app/services/mlb_service.py", "서비스 모듈", "MLB 30개 구단 순위, 실시간 이닝, 승·패·세이브 투수", "fetch_mlb_recent_matches, fetch_mlb_standings", "requests, json"),
    ("Business Layer", "app/services/overseas_soccer_service.py", "서비스 모듈", "유럽 5대 축구리그 순위, 금주/지난주 경기, 클락 정보", "fetch_soccer_recent_matches, translate_team_name", "requests, bs4, datetime"),
    ("Presentation Layer", "app/templates/index.html", "템플릿 (SSR)", "메인 반응형 대시보드 마크업 구조 정의 (상단 결과/하단 영상)", "스코어보드 그리드, 하이라이트 플레이어, 순위표", "Jinja2, HTML5"),
    ("Presentation Layer", "app/static/js/main.js", "클라이언트 스크립트", "SPA 인터랙션, 필터 칩 제어, 마이팀 로컬 스토리지 연동", "render*Matches, setMatchFilter, Facade Player", "Vanilla JavaScript ES6+"),
    ("Presentation Layer", "app/static/css/style.css", "스타일시트", "Tailwind 보조 커스텀 CSS, 상태 칩 디자인, 테마", ".match-filter-chip, .my-team-card, 다크모드", "CSS3, TailwindCSS"),
    ("Persistence Layer", "cache/kbo_data.json", "데이터 캐시", "KBO 프로야구 종합 데이터 파일", "recent_matches, standings, hitters, pitchers", "JSON File"),
    ("Persistence Layer", "cache/kleague_data.json", "데이터 캐시", "K리그1/K리그2 종합 데이터 파일", "k1, k2 (matches, standings, leaders)", "JSON File"),
    ("Persistence Layer", "cache/mlb_data.json", "데이터 캐시", "MLB 메이저리그 종합 데이터 파일", "recent_matches, standings, hitters, pitchers", "JSON File"),
    ("Persistence Layer", "cache/overseas_soccer_data.json", "데이터 캐시", "해외축구 5대리그 종합 데이터 파일", "leagues (epl, laliga, bundesliga, ucl, uel)", "JSON File")
]
apply_sheet_styling(ws4, "소스 구성도 및 디렉토리 아키텍처 (Source Architecture)", src_widths, src_headers, src_data)


# ==============================================================================
# Sheet 5: 외부 API 연동 명세서 (API Integration)
# ==============================================================================
ws5 = wb.create_sheet(title="05_외부API연동명세")
api_headers = ["NO", "대상 종목", "제공 기관", "엔드포인트 URL", "메서드", "주요 파라미터", "수집 및 활용 데이터", "응답 형식", "장애 대응 (Fallback)"]
api_widths = [6, 12, 16, 42, 10, 24, 35, 12, 28]
api_data = [
    (1, "KBO 프로야구", "네이버 스포츠", "https://api-gw.sports.naver.com/schedule/games", "GET", "fields=basic,baseball&fromDate,toDate&size=100&upperCategoryId=kbaseball", "실시간 이닝 스코어, 승·패전 결정투수, 당일/내일 선발투수 예고, 구장, 중계사", "JSON", "koreabaseball.com 크롤링 Fallback"),
    (2, "KBO 프로야구", "KBO 공식포털", "https://www.koreabaseball.com/ws/Schedule.asmx/GetScheduleList", "POST", "leId=1, seasonId=2026, gameMonth=09", "네이버 API 장애 시 백업 일정 및 경기 결과 수집", "JSON/HTML", "기존 JSON 캐시 데이터 보존"),
    (3, "KBO 순위/기록", "네이버 스포츠", "https://api-gw.sports.naver.com/record/kbo/ranking", "GET", "season=2026", "10개 구단 순위, 승/무/패, 승률, 타자 득점·타율 순위, 투수 다승·ERA 순위", "JSON", "KBO 공식 웹페이지 크롤링"),
    (4, "K리그 (1·2)", "K리그 공식포털", "https://www.kleague.com/getScheduleList.do", "POST", "leagueId=1 or 2, year=2026, month=09", "경기일시, 홈/원정팀, 스코어, 경기장, 경기상태(1H, 2H, HT, FE), 중계채널", "JSON", "이전 달 조회 재시도 및 기존 캐시"),
    (5, "K리그 순위", "K리그 공식포털", "https://www.kleague.com/record/teamRank.do", "POST", "leagueId=1 or 2, year=2026, recordType=basic", "구단별 순위, 경기수, 승점, 승/무/패, 득실차, 최근 5경기 전적", "JSON", "전년도 시즌 데이터 fallback"),
    (6, "MLB 메이저리그", "MLB Stats API", "https://statsapi.mlb.com/api/v1/schedule", "GET", "sportId=1&startDate,endDate&hydrate=linescore,decisions,probablePitcher", "실시간 이닝, 홈/원정 스코어, 승리투수, 패전투수, 세이브투수, 선발투수 매치업", "JSON", "최근 로컬 캐시 유지"),
    (7, "MLB 순위/기록", "MLB Stats API", "https://statsapi.mlb.com/api/v1/standings", "GET", "leagueId=103,104&season=2026", "AL/NL 디비전별 30개 구단 순위, 승률, 게임차, 팀 엠블럼", "JSON", "공식 웹 순위 테이블 연동"),
    (8, "해외축구 스코어", "ESPN Soccer", "https://site.web.api.espn.com/apis/site/v2/sports/soccer/{code}/scoreboard", "GET", "dates=YYYYMMDD (캘린더 기반 동적 파라미터)", "실시간 스코어, 전·후반 분(displayClock), 경기상태, 금주 예정 경기, 하이라이트 링크", "JSON", "일자별 재시도 및 기본 일정 사용"),
    (9, "해외축구 순위", "ESPN Soccer", "https://site.web.api.espn.com/apis/site/v2/sports/soccer/{code}/standings", "GET", "espnCode (eng.1, esp.1, ger.1 등)", "리그별 20개 팀 순위, 승점, 골득실, 팀 로고 URL", "JSON", "Goal.com 순위 크롤링 Fallback"),
    (10, "해외축구 순위(백업)", "Goal.com", "https://www.goal.com/kr/{리그명}/순위", "GET", "User-Agent 브라우저 헤더", "ESPN 장애 시 국내 Goal.com 웹 순위 테이블 HTML 파싱", "HTML 파싱", "ESPN 통계 API 복구 시 자동 전환")
]
apply_sheet_styling(ws5, "외부 API 및 데이터 연동 명세서 (API Integration Specs)", api_widths, api_headers, api_data)


# ==============================================================================
# Sheet 6: UI/UX 화면 명세서 (UI_UX Specs)
# ==============================================================================
ws6 = wb.create_sheet(title="06_화면명세서")
ui_headers = ["화면 ID", "영역 / 컴포넌트명", "위치 (Position)", "구성 요소 및 마크업", "인터랙션 및 기능 동작", "디자인 / 스타일 규칙"]
ui_widths = [12, 22, 16, 38, 45, 30]
ui_data = [
    ("SCR-01", "GNB 글로벌 헤더", "화면 최상단 (Sticky)", "서비스 로고(SPORTS HUB), 4대 종목 탭 버튼(KBO, K리그, 해외축구, MLB), 다크모드 토글 버튼", "종목 탭 클릭 시 해당 종목 섹션으로 전환, 다크모드 클릭 시 html 태그 dark 클래스 토글", "Tailwind blur 백드롭, 둥근 모서리, 활성 탭 블루 강조"),
    ("SCR-02", "마이팀 배너 & 필터", "헤더 하단", "선호 구단 안내 배너, [선호 구단 경기만 보기] 원클릭 필터 토글 버튼", "클릭 시 localStorage에 저장된 마이팀 경기만 필터링 노출, 미등록 시 안내 표시", "Amber-400 골드 컬러 테두리 및 뱃지 스타일"),
    ("SCR-03", "경기 결과 헤더 & 필터", "메인 콘텐츠 상단 (1순위)", "섹션 타이틀, 상태 필터 칩 버튼군 ([전체], [🔴 LIVE], [최근 결과], [금주/내일 예정])", "필터 칩 클릭 시 즉시 해당 상태의 경기 카드만 실시간 필터링 렌더링", ".match-filter-chip.active 스타일 적용, LIVE 칩 레드 강조"),
    ("SCR-04", "경기 스코어보드 카드", "메인 콘텐츠 상단 그리드", "날짜/시간, 구장, 상태 뱃지, 홈/원정 엠블럼 및 팀명, 실시간 스코어, 결정투수/선발예고/축구시간 박스, 하이라이트/실시간 중계확인 버튼", "★ 클릭 시 마이팀 토글, LIVE 시 [실시간 중계확인] 클릭 -> 네이버 문자중계 모달 오픈, 종료 시 [하이라이트] 클릭 -> 영상 포커스", "반응형 1~3열 그리드, LIVE 카드 레드 링 애니메이션"),
    ("SCR-05", "공식 영상 플레이어", "메인 콘텐츠 하단 (2순위)", "YouTube / MP4 비디오 뷰어, Facade 포스터 썸네일, 대형 재생 버튼, 영상 타이틀, 출처 배지", "썸네일 클릭 시 즉시 인라인 Iframe 로딩 및 영상 재생 (트래픽 최적화)", "16:9 비율 유지, 다크 백그라운드, 풀스크린 지원"),
    ("SCR-06", "영상 추천 목록", "영상 플레이어 우측/하단", "최근 5~10개 공식 하이라이트 카드 리스트 (썸네일, 재생시간, 제목, 경기 날짜)", "카드 클릭 시 좌측 대형 플레이어에 해당 영상 즉시 로드 및 포커스", "마우스 호버 시 살짝 확대 효과, 모바일 가로/세로 유연 대응"),
    ("SCR-07", "구단별 허브 선택기", "순위 테이블 상단", "리그 소속 전 구단 원형/사각 엠블럼 버튼 리스트", "구단 클릭 시 해당 팀의 세부 성적, 소속 주요선수 득점/도움/ERA 랭킹 동적 표시", "선호 구단 등록된 팀은 별표 및 골드 테두리 자동 부여"),
    ("SCR-08", "리그 종합 순위표", "하단 탭/섹션", "순위, 구단 엠블럼, 팀명, 경기수, 승/무/패, 승점/승률, 게임차, 최근 전적 뱃지", "선호 구단 행 자동 하이라이트 음영 처리, 승률/승점 컬럼 볼드 강조", "스트라이프 테이블, 모바일 가로 스크롤(overflow-x-auto)"),
    ("SCR-09", "실시간 공식 중계센터 모달", "레이어 팝업 (Modal)", "LIVE 뱃지 헤더, 매치업 정보 타이틀, [네이버 새 창 보기] 버튼, [MLB 3D게임데이] 버튼, 닫기 버튼, Iframe 문자중계 뷰어, 안전 안내바", "LIVE 경기 카드에서 [실시간 중계확인] 클릭 시 내부 단독 팝업 오픈, 실시간 볼카운트/투구추적 렌더링, 새 창 버튼 옵션 제공, ESC/배경 클릭 닫기", "fixed inset-0 z-50 백드롭 블러, 최대폭 max-w-4xl, 높이 90vh")
]
apply_sheet_styling(ws6, "화면 및 UI/UX 상세 명세서 (UI/UX Specifications)", ui_widths, ui_headers, ui_data)


# ==============================================================================
# Sheet 7: 시스템 수정 및 보완 이력 (System Changelog)
# ==============================================================================
ws7 = wb.create_sheet(title="07_수정및보완이력")
change_headers = ["NO", "버전", "일자", "구분", "대상 모듈 / 파일", "주요 수정 및 보완 내용", "개선 효과 및 해결 상세"]
change_widths = [6, 12, 14, 14, 32, 50, 40]
change_data = [
    (1, "v2.4.0", "2026-09-20", "긴급 버그수정", "mlb_service.py\nkbo_service.py\nkleague_service.py\noverseas_soccer_service.py", "서버 타임존(Render UTC vs 로컬 KST) 불일치 캐시 프리징 해결 및 KST 표준화:\n- get_now_kst() 공통 표준화로 호스팅 서버 타임존과 무관하게 한국 표준시 일치\n- 캐시 타임스탬프 만료 검사 시 음수(diff < 0) 즉시 무효화 안전장치 탑재\n- 커밋된 미래 타임스탬프 파일로 인해 서버 캐시가 갱신되지 않고 멈추던 버그 원천 해결", "Render 클라우드 배포 후 경기 스코어/상태가 수 시간 동안 멈추던 버그 완전 해결"),
    (2, "v2.4.0", "2026-09-20", "기능 고도화", "app/services/mlb_service.py\napp/static/js/main.js", "MLB 실시간 LIVE 경기 판정 정밀화 및 투수/타자 실시간 연동:\n- MLB API statusCode('O', 'F', 'CR', 'FR') 및 detailedState('Game Over') 즉시 종료 처리\n- 실시간 LIVE 이닝 포맷 한국어 정밀 매핑 (8회초 1아웃, 8회말 등)\n- 공식 linescore에서 현재 마운드 투수(current_pitcher) 및 타석 타자(current_batter) 실시간 추출하여 카드에 표출\n- 종료 경기 노출 25개, 예정 경기 16개로 확대하여 당일 전 경기 및 내일 일정 완벽 커버\n- LIVE 경기 25초, 비경기 시간대 90초 백그라운드 스마트 자동 폴링 적용", "끝난 경기가 LIVE로 남는 현상 방지, 실시간 투수 vs 타자 매치업 카드 시각화, 당일 전 경기 스코어 열람"),
    (3, "v2.3.0", "2026-09-20", "기능 개선", "kbo_service.py\nkleague_service.py\nmlb_service.py\noverseas_soccer_service.py", "스마트 캐시 갱신 구조 도입 및 LIVE 경기 안전 판별 강화:\n- 30분 TTL 캐시 유지 + 라이브 경기 시 25초 주기 실시간 fetch\n- 경기 시작(KST) 기준 안전 종료(야구 5.5h, 축구 3.5h 초과 시 자동 종료) 방어\n- 프론트엔드 30초 무중단 자동 폴링(startLivePolling)", "종료된 경기가 LIVE로 남아있던 버그 완전 해결, 새로고침 시 실시간 최신 스코어/이닝 즉시 동기화"),
    (4, "v2.3.0", "2026-09-20", "기능 개선", "app/services/mlb_service.py\napp/templates/index.html", "MLB 한국 표준시(KST) 변환 & 팀 ID / 네이버 연동 정상화:\n- UTC 시간의 KST 9시간 자동 변환(%m.%d HH:MM) 및 헤더 뱃지 표기\n- MLB 30개 구단 공식 Stats API 팀 식별자 오타 전면 수정\n- 네이버 해외야구(wbaseball) API 매핑(fetch_naver_wbaseball_map)으로 공식 gameId 확보", "경기 시간 가독성 100% 개선 및 네이버 실시간 문자중계 gameId 100% 매핑 연동"),
    (5, "v2.3.0", "2026-09-20", "UI/UX 개선", "app/static/js/main.js\napp/templates/index.html", "실시간 중계 모달(live-relay-modal) UX 단독 팝업화 & 바로가기 강화:\n- [실시간 중계확인] 클릭 시 새 창 동시 실행 제거 -> 단독 내부 팝업으로 깔끔하게 표출\n- 팝업 상단에 초록색 [네이버 새 창 보기], 파란색 [MLB 3D게임데이] 바로가기 액션 버튼 제공\n- 브라우저 iframe 보안 정책으로 인한 멈춤 방어(1.5초 자동 페이드아웃)", "새 창/팝업 이중 실행 혼란 제거, 사용자가 원하는 팝업 내 쾌적한 중계 감상"),
    (6, "v2.3.0", "2026-09-20", "버그 수정", "app/templates/index.html\napp/templates/base.html\noverseas_soccer_service.py", "브라우저 개발자도구 콘솔 오류 3종 완전 제거:\n1) iframe 인라인 onload 제거 및 상단 방어 선언으로 onRelayIframeLoaded is not defined 해결\n2) 해외축구 비디오 썸네일에서 비공개 artwork.api.espn.com 필터링 및 공개 CDN/고화질 이미지 매핑으로 401 해결\n3) Tailwind CDN 프로덕션 경고 필터링 적용\n4) main.js?v=... 스크립트 캐시 버스팅 적용", "F12 개발자도구 콘솔 오류 0(Zero) 무결성 확보"),
    (7, "v2.2.0", "2026-09-19", "기능 추가", "app/templates/index.html\napp/static/js/main.js", "네이버스포츠 실시간 문자중계 모달(live-relay-modal) 최초 구현:\n- LIVE 경기 카드에 [실시간 중계확인] 버튼 노출 및 인라인 모달 연동", "페이지 이탈 없는 실시간 문자중계 확인 환경 제공"),
    (8, "v2.1.0", "2026-09-19", "UI 개선", "app/templates/index.html\napp/static/css/style.css", "상단 경기결과 / 하단 영상 레이아웃 개편 및 상태 필터 칩 고도화", "스코어보드 시인성 향상 및 한눈에 들어오는 경기 요약"),
    (9, "v2.0.0", "2026-09-19", "아키텍처", "전체 프로젝트", "4대 스포츠(KBO, K리그, 해외축구, MLB) 통합 올인원 대시보드 시스템 구축", "종목별 분산 정보를 하나의 웹 허브로 통합")
]
apply_sheet_styling(ws7, "시스템 수정 및 보완 이력 (System Changelog)", change_widths, change_headers, change_data)


# 저장
output_path = "/Users/소스/WEB_SPORTS/SPORTS_HUB_프로그램명세서_및_설계서.xlsx"
wb.save(output_path)
print(f"Excel file successfully generated at: {output_path}")

