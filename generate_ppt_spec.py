"""
SPORTS HUB - 프로그램 명세서, 프로세스 흐름도, 소스 구성도 PowerPoint (PPTX) 생성 스크립트
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation()
# 16:9 와이드스크린 설정
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6] # 빈 슬라이드

# 컬러 팔레트 정의
COLOR_NAVY = RGBColor(15, 23, 42)      # #0F172A (다크 네이비)
COLOR_BLUE = RGBColor(30, 58, 138)     # #1E3A8A (메인 블루)
COLOR_LIGHT_BG = RGBColor(248, 250, 252) # #F8FAFC (연회색 배경)
COLOR_WHITE = RGBColor(255, 255, 255)  # #FFFFFF
COLOR_CARD_BG = RGBColor(255, 255, 255)
COLOR_BORDER = RGBColor(203, 213, 225) # #CBD5E1
COLOR_TEXT_MAIN = RGBColor(15, 23, 42)
COLOR_TEXT_MUTED = RGBColor(100, 116, 139)
COLOR_PRIMARY_BLUE = RGBColor(37, 99, 235) # #2563EB
COLOR_ACCENT_AMBER = RGBColor(217, 119, 6) # #D97706
COLOR_RED_LIVE = RGBColor(220, 38, 38)     # #DC2626
COLOR_GREEN = RGBColor(22, 163, 74)        # #16A34A

def create_base_slide(title_text, category_text="SPORTS HUB SYSTEM ARCHITECTURE"):
    slide = prs.slides.add_slide(blank_layout)
    
    # 배경
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLOR_LIGHT_BG
    bg.line.fill.background()

    # 상단 헤더 바
    header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(1.1))
    tf = header_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p_cat = tf.paragraphs[0]
    p_cat.text = category_text
    p_cat.font.name = "Malgun Gothic"
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = COLOR_PRIMARY_BLUE

    p_title = tf.add_paragraph()
    p_title.text = title_text
    p_title.font.name = "Malgun Gothic"
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_NAVY
    p_title.space_before = Pt(4)

    # 하단 푸터 라인
    footer_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(7.0), Inches(11.7), Inches(0.02))
    footer_line.fill.solid()
    footer_line.fill.fore_color.rgb = COLOR_BORDER
    footer_line.line.fill.background()

    # 푸터 텍스트
    footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(11.7), Inches(0.3))
    ft_tf = footer_box.text_frame
    p_ft = ft_tf.paragraphs[0]
    p_ft.text = "SPORTS HUB v2.4.0  |  실시간 스포츠 종합 대시보드 시스템 명세서  |  Confidential"
    p_ft.font.name = "Malgun Gothic"
    p_ft.font.size = Pt(9)
    p_ft.font.color.rgb = COLOR_TEXT_MUTED

    return slide

def add_card(slide, x, y, w, h, bg_color=COLOR_WHITE, border_color=COLOR_BORDER):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)
    else:
        card.line.fill.background()
    return card


# ==============================================================================
# Slide 1: 표지 (Cover Slide)
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)

# 다크 네이비 배경
bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
bg1.fill.solid()
bg1.fill.fore_color.rgb = COLOR_NAVY
bg1.line.fill.background()

# 장식용 사각형 라인
dec = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.2), Inches(1.8), Inches(0.12), Inches(3.2))
dec.fill.solid()
dec.fill.fore_color.rgb = COLOR_PRIMARY_BLUE
dec.line.fill.background()

title_box = s1.shapes.add_textbox(Inches(1.5), Inches(1.7), Inches(10.5), Inches(3.5))
tf1 = title_box.text_frame
tf1.word_wrap = True

p1 = tf1.paragraphs[0]
p1.text = "SPORTS ALL-IN-ONE HUB DASHBOARD"
p1.font.name = "Malgun Gothic"
p1.font.size = Pt(13)
p1.font.bold = True
p1.font.color.rgb = RGBColor(96, 165, 250)

p2 = tf1.add_paragraph()
p2.text = "SPORTS HUB 시스템 설계 및 프로그램 명세서"
p2.font.name = "Malgun Gothic"
p2.font.size = Pt(32)
p2.font.bold = True
p2.font.color.rgb = COLOR_WHITE
p2.space_before = Pt(12)

p3 = tf1.add_paragraph()
p3.text = "실시간 스포츠 순위 · 경기결과 스코어보드 · 네이버 실시간 문자중계 · 프로세스 흐름도"
p3.font.name = "Malgun Gothic"
p3.font.size = Pt(16)
p3.font.color.rgb = RGBColor(226, 232, 240)
p3.space_before = Pt(14)

# 하단 정보 카드
meta_box = s1.shapes.add_textbox(Inches(1.5), Inches(5.4), Inches(10.5), Inches(1.2))
tf_meta = meta_box.text_frame
p_meta1 = tf_meta.paragraphs[0]
p_meta1.text = "• 대상 종목: KBO 한국프로야구  |  K리그 1·2  |  해외축구 5대리그  |  MLB 메이저리그"
p_meta1.font.name = "Malgun Gothic"
p_meta1.font.size = Pt(11)
p_meta1.font.color.rgb = RGBColor(148, 163, 184)

p_meta2 = tf_meta.add_paragraph()
p_meta2.text = "• 기술 스택: Python 3.14 · FastAPI · Jinja2 · Vanilla JS · TailwindCSS · REST API Caching Engine"
p_meta2.font.name = "Malgun Gothic"
p_meta2.font.size = Pt(11)
p_meta2.font.color.rgb = RGBColor(148, 163, 184)
p_meta2.space_before = Pt(4)

p_meta3 = tf_meta.add_paragraph()
p_meta3.text = "• 문서 버전: v2.4.0  |  작성일: 2026-09-20  |  저장소: https://github.com/th0501park-tech/master2"
p_meta3.font.name = "Malgun Gothic"
p_meta3.font.size = Pt(11)
p_meta3.font.color.rgb = RGBColor(148, 163, 184)
p_meta3.space_before = Pt(4)


# ==============================================================================
# Slide 2: 프로젝트 개요 및 주요 핵심 기능
# ==============================================================================
s2 = create_base_slide("프로젝트 개요 및 핵심 아키텍처 특징", "01. PROJECT OVERVIEW")

# 3개 컬럼 카드 배치
card_data_s2 = [
    ("⚾ 4대 프로 스포츠 통합 제공", 
     "KBO, K리그, 해외축구, MLB 단일 플랫폼 통합", 
     "• KBO / MLB: 10개 구단 및 30개 구단 순위, 타자/투수 개인기록 리더보드 통합\n• K리그 1·2: 승강제 반영 전 구단 순위 및 득점/도움/공격포인트 순위\n• 해외축구: EPL, 라리가, 분데스리가, UCL, UEL 5개 리그 탭 완벽 지원\n• 반응형 SPA: 새로고침 없는 원클릭 종목/서브리그 즉시 전환"),
    ("🔥 상단 스코어 & 네이버 문자중계", 
     "실시간 LIVE 중계확인 모달 & 레이아웃 혁신", 
     "• 실시간 문자중계 모달: LIVE 경기 카드에서 [⚡ 실시간 중계확인] 클릭 시 네이버스포츠 실시간 문자중계 즉시 렌더링\n• 볼카운트 / 투구 추적 / 이닝별 상세 결과를 모달에서 이탈 없이 확인\n• 야구(KBO/MLB): 실시간 LIVE 이닝, 승·패·세이브 결정투수, 선발투수 예고\n• 축구(K리그/해외축구): 공식 상태(1S/2S/HT/ET/PK), 네이버 kfootball 실시간 분/스코어 연동"),
    ("⚡ 고성능 캐싱 & 영상 지연로딩", 
     "0.5초 이내 초고속 응답 & 마이팀 개인화", 
     "• 로컬 파일 캐시: 5~15분 주기 TTL 캐싱으로 외부 API 호출 쿼터 및 지연 방지\n• Facade 패턴: 종료 경기 하이라이트는 고화질 포스터를 선로딩하여 트래픽 90% 절감\n• 마이팀(선호 구단): 로컬스토리지 연동으로 응원팀 경기 최상단 정렬 및 골드 강조\n• 다크/라이트 모드: 시스템 설정 자동 감지 및 사용자 수동 토글 지원")
]

for idx, (head, sub, desc) in enumerate(card_data_s2):
    cx = 0.8 + idx * 4.0
    add_card(s2, cx, 1.7, 3.7, 4.9)
    tb = s2.shapes.add_textbox(Inches(cx + 0.2), Inches(1.9), Inches(3.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = head
    p.font.name = "Malgun Gothic"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE

    p_sub = tf.add_paragraph()
    p_sub.text = sub
    p_sub.font.name = "Malgun Gothic"
    p_sub.font.size = Pt(10)
    p_sub.font.bold = True
    p_sub.font.color.rgb = COLOR_TEXT_MUTED
    p_sub.space_before = Pt(4)

    p_desc = tf.add_paragraph()
    p_desc.text = desc
    p_desc.font.name = "Malgun Gothic"
    p_desc.font.size = Pt(10)
    p_desc.font.color.rgb = COLOR_TEXT_MAIN
    p_desc.space_before = Pt(12)


# ==============================================================================
# Slide 3: 시스템 아키텍처 및 소스 구성도
# ==============================================================================
s3 = create_base_slide("시스템 아키텍처 및 디렉토리 소스 구성도", "02. SYSTEM ARCHITECTURE")

# 좌측: 아키텍처 계층 다이어그램
add_card(s3, 0.8, 1.7, 5.6, 4.9)
tb_l = s3.shapes.add_textbox(Inches(1.0), Inches(1.9), Inches(5.2), Inches(4.5))
tf_l = tb_l.text_frame
tf_l.word_wrap = True

p = tf_l.paragraphs[0]
p.text = "🏛️ 4-Tier Layered Architecture"
p.font.name = "Malgun Gothic"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = COLOR_NAVY

layers = [
    ("1. Presentation Layer (클라이언트)", "• HTML5, Jinja2 SSR Templates (app/templates/index.html)\n• Vanilla JS 클라이언트 인터랙션 (app/static/js/main.js)\n• TailwindCSS CDN & Custom Styles (app/static/css/style.css)"),
    ("2. Application Layer (웹 서버)", "• ASGI 기반 고성능 웹 서버 (run.py / Uvicorn)\n• FastAPI 메인 컨트롤러 (app/main.py) - 라우팅 및 데이터 통합"),
    ("3. Business Layer (스포츠 데이터 엔진)", "• KBO 프로야구 서비스 (app/services/kbo_service.py)\n• K리그 축구 서비스 (app/services/kleague_service.py)\n• MLB 메이저리그 서비스 (app/services/mlb_service.py)\n• 해외축구 5대리그 서비스 (app/services/overseas_soccer_service.py)"),
    ("4. Persistence & External Integration", "• 로컬 파일 캐싱 엔진 (cache/*.json, TTL 관리)\n• 외부 데이터 API: 네이버 스포츠, MLB Stats, ESPN, K리그 포털")
]

for l_title, l_desc in layers:
    p_t = tf_l.add_paragraph()
    p_t.text = l_title
    p_t.font.name = "Malgun Gothic"
    p_t.font.size = Pt(10)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_PRIMARY_BLUE
    p_t.space_before = Pt(8)

    p_d = tf_l.add_paragraph()
    p_d.text = l_desc
    p_d.font.name = "Malgun Gothic"
    p_d.font.size = Pt(9)
    p_d.font.color.rgb = COLOR_TEXT_MAIN
    p_d.space_before = Pt(2)

# 우측: 디렉토리 소스 구조 트리
add_card(s3, 6.7, 1.7, 5.8, 4.9)
tb_r = s3.shapes.add_textbox(Inches(6.9), Inches(1.9), Inches(5.4), Inches(4.5))
tf_r = tb_r.text_frame
tf_r.word_wrap = True

p_r = tf_r.paragraphs[0]
p_r.text = "📂 프로젝트 소스 구성도 (Source Directory Tree)"
p_r.font.name = "Malgun Gothic"
p_r.font.size = Pt(14)
p_r.font.bold = True
p_r.font.color.rgb = COLOR_NAVY

tree_text = """WEB_SPORTS/
├── run.py                     # [진입점] Uvicorn 웹서버 기동 스크립트
├── requirements.txt           # [의존성] FastAPI, Uvicorn, Requests, BS4
├── Procfile / render.yaml     # [배포] Render.com 클라우드 호스팅 설정
├── app/
│   ├── main.py                # [컨트롤러] FastAPI 인스턴스 및 루트 라우트
│   ├── services/              # [도메인 서비스] 4대 스포츠 데이터 수집 엔진
│   │   ├── kbo_service.py     #  - KBO 실시간 이닝/스코어, 결정투수, 순위
│   │   ├── kleague_service.py #  - K리그 금주예정/최근경기, 순위, 득점
│   │   ├── mlb_service.py     #  - MLB 실시간 이닝, 승/패/세이브 투수, 순위
│   │   └── overseas_soccer_service.py # - 해외축구 5대리그, 클락시간
│   ├── templates/
│   │   └── index.html         # [뷰] 메인 반응형 대시보드 템플릿 (SSR)
│   └── static/
│       ├── js/main.js         # [스크립트] SPA 탭, 필터 칩, 마이팀, Facade
│       └── css/style.css      # [스타일] 경기 상태 칩, 다크모드, 애니메이션
└── cache/                     # [영속성 캐시] 로컬 JSON 캐시 파일 저장소
    ├── kbo_data.json          #  - KBO 최신 캐시 데이터
    ├── kleague_data.json      #  - K리그 최신 캐시 데이터
    ├── mlb_data.json          #  - MLB 최신 캐시 데이터
    └── overseas_soccer_data.json # - 해외축구 최신 캐시 데이터"""

p_tree = tf_r.add_paragraph()
p_tree.text = tree_text
p_tree.font.name = "Consolas"
p_tree.font.size = Pt(8.5)
p_tree.font.color.rgb = RGBColor(30, 41, 59)
p_tree.space_before = Pt(8)


# ==============================================================================
# Slide 4: 백엔드 프로그램 명세서
# ==============================================================================
s4 = create_base_slide("백엔드 프로그램 명세서 (Backend Services)", "03. BACKEND SPECIFICATIONS")

# 4개 서비스 카드
services_data = [
    ("⚾ KBO 프로야구 서비스", "kbo_service.py (약 650 라인)", 
     "• 네이버 스포츠 KBO API (api-gw.sports.naver.com)\n• 실시간 LIVE: status_code(STARTED) 기반 당일 진행중 이닝/현재투수\n• 최근 경기 결과: 승리투수(winPitcherName), 패전투수(losePitcherName)\n• 예정 경기: 오늘/내일 선발투수 예고(homeStarterName, awayStarterName)\n• 팀순위 및 타자/투수 리더보드 수집 및 로컬 캐싱 (kbo_data.json)"),
    ("🧢 MLB 메이저리그 서비스", "mlb_service.py (약 450 라인)", 
     "• MLB Stats 공식 API (statsapi.mlb.com)\n• hydrate 파라미터 적용: linescore, decisions, probablePitcher 일괄 취득\n• 결정투수 명세: 승리투수(W), 패전투수(L), 세이브투수(S) 완벽 추출\n• 실시간 이닝 및 선발 매치업 예고 제공\n• AL/NL 30개 구단 디비전 순위 및 개인기록 수집 (mlb_data.json)"),
    ("⚽ K리그 (K1 · K2) 서비스", "kleague_service.py (네이버 kfootball + K리그 공식 API)", 
     "• 네이버 스포츠 K리그 API(kfootball) + K리그 공식 포털 하이브리드 연동\n• 실시간 LIVE 동기화: status: STARTED, 실시간 분(1S 30, 2S 15 등) 및 점수 반영\n• 네이버 gameId 자동 추출: 네이버 실시간 문자중계 팝업 모달 연동 지원\n• 주차별 필터링: 금주 일요일까지 예정된 경기만 '금주 예정', 지난주 경기만 종료 표기\n• K1/K2 25개 구단 공식 엠블럼 및 득점/도움/무실점 순위 제공"),
    ("🌍 해외축구 5대리그 서비스", "overseas_soccer_service.py (약 680 라인)", 
     "• ESPN Soccer Scoreboard API (EPL, 라리가, 분데스리가, UCL, UEL)\n• 한국 표준시(KST, UTC+9) 자동 변환: UTC 일정을 한국 시간대로 정확히 보정\n• 캘린더 기반 동적 일정 수집: 금주 주말 예정 경기 + 지난주 종료 경기\n• 실시간 분 정보: displayClock (35', 72') 및 하이라이트 영상 추출\n• 구단명 한국어 자동 매핑 딕셔너리 (TEAM_KR_NAMES)")
]

for idx, (stitle, sfile, sdesc) in enumerate(services_data):
    col = idx % 2
    row = idx // 2
    cx = 0.8 + col * 5.9
    cy = 1.7 + row * 2.55
    add_card(s4, cx, cy, 5.6, 2.35)
    tb = s4.shapes.add_textbox(Inches(cx + 0.2), Inches(cy + 0.15), Inches(5.2), Inches(2.05))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = stitle
    p.font.name = "Malgun Gothic"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE

    p_f = tf.add_paragraph()
    p_f.text = sfile
    p_f.font.name = "Consolas"
    p_f.font.size = Pt(9)
    p_f.font.bold = True
    p_f.font.color.rgb = COLOR_TEXT_MUTED
    p_f.space_before = Pt(2)

    p_d = tf.add_paragraph()
    p_d.text = sdesc
    p_d.font.name = "Malgun Gothic"
    p_d.font.size = Pt(9)
    p_d.font.color.rgb = COLOR_TEXT_MAIN
    p_d.space_before = Pt(6)


# ==============================================================================
# Slide 5: 프론트엔드 프로그램 명세서
# ==============================================================================
s5 = create_base_slide("프론트엔드 프로그램 명세서 (Frontend & SPA)", "04. FRONTEND SPECIFICATIONS")

fe_cards = [
    ("⚡ 실시간 중계확인 & 네이버 문자중계", "main.js (openLiveRelayModal, closeLiveRelayModal)",
     "• LIVE 진행 중인 경기: 하단 [하이라이트] 대신 [⚡ 실시간 중계확인] 버튼 노출\n• 원클릭 팝업 모달: 네이버스포츠 실시간 문자중계(/relay)를 인앱 Iframe으로 즉시 렌더링\n• 외부 브라우저 새창 이동([네이버스포츠로 이동]) 및 ESC/외부클릭 닫기 지원\n• 타 종목(KBO, K리그 등) liveUrl / gameId 기반 동적 라우팅"),
    ("🎛️ 경기 상태별 원클릭 필터 칩", "main.js (setMatchFilter, filterMatchesByStatus)",
     "• 4종 필터 칩: [전체], [🔴 LIVE], [최근 결과], [금주/내일 예정]\n• 클릭 시 새로고침 없이 해당 상태의 경기 카드만 즉시 필터링 렌더링\n• LIVE 상태 시 실시간 깜빡임 펄스 뱃지 & 실시간 투수/이닝 표기\n• .match-filter-chip.active 스타일 적용 및 라이트/다크모드 완벽 대응"),
    ("⭐ 마이팀(선호 구단) 개인화", "main.js (toggleFavoriteTeam, updateMyTeamBanner)",
     "• 경기 카드 및 순위표의 ★ 별표 클릭 시 선호 구단으로 즉시 지정\n• localStorage 연동: 브라우저 재방문 시에도 선호 구단 상태 영구 보존\n• 선호 구단 등록 시 해당 구단 경기 최상단 우선 정렬 & 골드 링 테두리 강조\n• [선호 구단 경기만 보기] 원클릭 필터 제공"),
    ("🎬 Facade 기반 하이라이트 플레이어", "main.js (Facade Player & Iframe On-Demand)",
     "• Facade 기법: YouTube 고화질 썸네일 포스터 및 재생 버튼만 초기 렌더링\n• 종료/예정 경기에서 [🎬 하이라이트] 클릭 시 해당 영상으로 스크롤 이동 및 자동 로드\n• 초기 페이지 로딩 속도 0.5초 이내 유지 및 불필요한 네트워크 트래픽 90% 절감\n• 다크모드/라이트모드 완벽 대응 및 반응형 모바일 최적화")
]

for idx, (ftitle, ffile, fdesc) in enumerate(fe_cards):
    col = idx % 2
    row = idx // 2
    cx = 0.8 + col * 5.9
    cy = 1.7 + row * 2.55
    add_card(s5, cx, cy, 5.6, 2.35)
    tb = s5.shapes.add_textbox(Inches(cx + 0.2), Inches(cy + 0.15), Inches(5.2), Inches(2.05))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = ftitle
    p.font.name = "Malgun Gothic"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE

    p_f = tf.add_paragraph()
    p_f.text = ffile
    p_f.font.name = "Consolas"
    p_f.font.size = Pt(9)
    p_f.font.bold = True
    p_f.font.color.rgb = COLOR_TEXT_MUTED
    p_f.space_before = Pt(2)

    p_d = tf.add_paragraph()
    p_d.text = fdesc
    p_d.font.name = "Malgun Gothic"
    p_d.font.size = Pt(9)
    p_d.font.color.rgb = COLOR_TEXT_MAIN
    p_d.space_before = Pt(6)


# ==============================================================================
# Slide 6: 프로세스 흐름도 (End-to-End Flow)
# ==============================================================================
s6 = create_base_slide("엔드투엔드 데이터 파이프라인 및 프로세스 흐름도", "05. PROCESS FLOW")

steps = [
    ("Step 1", "서버 초기화 및 캐시 로드", "• run.py 실행 시 Uvicorn ASGI 기동\n• cache/ 폴더 내 4대 스포츠 데이터 검증\n• 캐시 부재 시 백그라운드 크롤링 수행"),
    ("Step 2", "사용자 브라우저 접속 (SSR)", "• GET / 요청 수신 시 FastAPI 컨트롤러 작동\n• 캐시된 KBO/K리그/해외축구/MLB 데이터 바인딩\n• 상단 스코어보드/하단 영상 초기 HTML 전송"),
    ("Step 3", "클라이언트 데이터 Hydration", "• window.INITIAL_DATA에 전체 데이터 적재\n• localStorage에서 마이팀 구단 및 테마 복원\n• 마이팀 경기 최상단 우선 배치"),
    ("Step 4", "동적 상태 필터링 (SPA)", "• [🔴 LIVE], [최근 결과], [금주 예정] 칩 클릭\n• status 플래그에 따라 카드 실시간 재배치\n• LIVE 시 중계확인 버튼, 종료 시 하이라이트 버튼 표출"),
    ("Step 5", "실시간 중계 & 영상 상호작용", "• [⚡ 실시간 중계확인]: 네이버 문자중계 모달 Iframe 팝업\n• [🎬 하이라이트]: 공식 영상 플레이어 이동 및 스트리밍\n• 외부 링크 새창 이동 지원")
]

for idx, (snum, stitle, sdesc) in enumerate(steps):
    cx = 0.8 + idx * 2.38
    add_card(s6, cx, 1.7, 2.22, 4.9)
    tb = s6.shapes.add_textbox(Inches(cx + 0.15), Inches(1.85), Inches(1.92), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True

    p_num = tf.paragraphs[0]
    p_num.text = snum
    p_num.font.name = "Malgun Gothic"
    p_num.font.size = Pt(11)
    p_num.font.bold = True
    p_num.font.color.rgb = COLOR_PRIMARY_BLUE

    p_t = tf.add_paragraph()
    p_t.text = stitle
    p_t.font.name = "Malgun Gothic"
    p_t.font.size = Pt(11)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_NAVY
    p_t.space_before = Pt(4)

    p_d = tf.add_paragraph()
    p_d.text = sdesc
    p_d.font.name = "Malgun Gothic"
    p_d.font.size = Pt(8.5)
    p_d.font.color.rgb = COLOR_TEXT_MAIN
    p_d.space_before = Pt(10)


# ==============================================================================
# Slide 7: 외부 데이터 소스 및 API 연동 명세
# ==============================================================================
s7 = create_base_slide("외부 데이터 소스 및 실시간 API 연동 명세", "06. EXTERNAL API INTEGRATION")

api_cards = [
    ("⚾ 네이버 스포츠 KBO API", "https://api-gw.sports.naver.com/schedule/games",
     "• 연동 방식: HTTP GET, JSON 응답\n• 파라미터: upperCategoryId=kbaseball&fromDate,toDate&size=100\n• 실시간 항목: 실시간 이닝, statusCode(STARTED/RESULT/BEFORE), 승·패 결정투수, 선발투수 예고\n• 네이버 실시간 문자중계 URL (https://m.sports.naver.com/game/{gameId}/relay) 연동"),
    ("🧢 MLB Stats 공식 API", "https://statsapi.mlb.com/api/v1/schedule",
     "• 연동 방식: HTTP GET, RESTful JSON 응답\n• 파라미터: sportId=1&startDate,endDate&hydrate=linescore,decisions,probablePitcher\n• 실시간 이닝 스코어보드, 승(W)·패(L)·세이브(S) 결정투수, 선발투수 매치업\n• 30개 구단 리그/디비전 순위 및 타자/투수 Top 5 리더보드 연동"),
    ("⚽ 네이버 스포츠 K리그 & 공식 포털 API", "https://api-gw.sports.naver.com/schedule/games",
     "• 연동 방식: HTTP GET (네이버 kfootball) + POST (K리그 공식 포털 getScheduleList.do)\n• 실시간 LIVE 동기화: 네이버 K리그 API로 실시간 분/점수/gameId 정밀 추출\n• 주차 필터: 금주 일요일까지 경기만 '금주 예정' 표기, 지난주 월요일 이후 경기만 종료 표기\n• 실시간 문자중계 팝업 모달 연동 및 25개 구단 엠블럼 매핑"),
    ("🌍 ESPN Soccer Scoreboard API", "https://site.web.api.espn.com/apis/site/v2/sports/soccer/{code}/scoreboard",
     "• 연동 방식: HTTP GET, JSON 응답\n• KST 자동 변환: UTC 일정 데이터를 한국 표준시(UTC+9)로 보정하여 날짜/시간 정확도 확보\n• 동적 캘린더 연동: 지난주부터 금주 주말까지의 핵심 매치일만 동적 추출\n• 지원 리그: EPL, 라리가, 분데스리가, UCL, UEL 5개 리그 통합")
]

for idx, (atitle, aurl, adesc) in enumerate(api_cards):
    col = idx % 2
    row = idx // 2
    cx = 0.8 + col * 5.9
    cy = 1.7 + row * 2.55
    add_card(s7, cx, cy, 5.6, 2.35)
    tb = s7.shapes.add_textbox(Inches(cx + 0.2), Inches(cy + 0.15), Inches(5.2), Inches(2.05))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = atitle
    p.font.name = "Malgun Gothic"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE

    p_u = tf.add_paragraph()
    p_u.text = aurl
    p_u.font.name = "Consolas"
    p_u.font.size = Pt(8.5)
    p_u.font.bold = True
    p_u.font.color.rgb = COLOR_TEXT_MUTED
    p_u.space_before = Pt(2)

    p_d = tf.add_paragraph()
    p_d.text = adesc
    p_d.font.name = "Malgun Gothic"
    p_d.font.size = Pt(8.5)
    p_d.font.color.rgb = COLOR_TEXT_MAIN
    p_d.space_before = Pt(6)


# ==============================================================================
# Slide 8: 배포 및 운영 환경 가이드
# ==============================================================================
s8 = create_base_slide("시스템 배포 및 운영 유지보수 가이드", "07. DEPLOYMENT & OPERATIONS")

ops_cards = [
    ("💻 로컬 개발 및 실행 환경", 
     "• 실행 명령: python run.py\n• 기본 바인딩: http://127.0.0.1:8000\n• 환경변수 지원:\n   - HOST=0.0.0.0 (외부 접속 허용)\n   - PORT=8000 (포트 번호 변경)\n   - RELOAD=true (코드 수정 시 자동 리로드)\n• 자동 캐시 워밍: 서버 기동 시 4대 스포츠 데이터 무결성 자동 검증"),
    ("☁️ 클라우드 프로덕션 배포 (Render.com)", 
     "• Procfile: web: uvicorn app.main:app --host 0.0.0.0 --port $PORT\n• render.yaml: 인프라 코드화(IaC) 사전 구성 완료\n• 배포 절차:\n   1. GitHub master2 저장소 연결\n   2. Build Command: pip install -r requirements.txt\n   3. Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT\n• HTTPS 인증서 자동 발급 및 24시간 무중단 가동"),
    ("🔄 데이터 갱신 및 유지보수 주기", 
     "• KBO / MLB (야구):\n   - 경기 진행 중: 3~5분 주기 LIVE 스코어보드 갱신\n   - 경기 종료 후: 승·패·세이브 투수 영구 저장\n• K리그 / 해외축구 (축구):\n   - 주말 경기일: 전·후반 실시간 분 정보 갱신\n   - 주중: 금주 예정 경기 및 지난주 결과 고정\n• 캐시 디렉토리: cache/*.json (Git 형상관리 연동)"),
    ("🔒 안정성 및 장애 대응 전략", 
     "• Fallback 체계 구축:\n   - 네이버 KBO 장애 시 koreabaseball 포털 크롤링\n   - ESPN 장애 시 Goal.com 크롤링 대체\n• 네트워크 단절 대응:\n   - 외부 API 전체 실패 시 기존 정상 캐시 무한 유지\n• 클라이언트 오류 격리:\n   - 종목별 렌더링 함수 독립 분리로 한 종목 에러가 타 종목에 미치는 영향 0%")
]

for idx, (otitle, odesc) in enumerate(ops_cards):
    col = idx % 2
    row = idx // 2
    cx = 0.8 + col * 5.9
    cy = 1.7 + row * 2.55
    add_card(s8, cx, cy, 5.6, 2.35)
    tb = s8.shapes.add_textbox(Inches(cx + 0.2), Inches(cy + 0.15), Inches(5.2), Inches(2.05))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = otitle
    p.font.name = "Malgun Gothic"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE

    p_d = tf.add_paragraph()
    p_d.text = odesc
    p_d.font.name = "Malgun Gothic"
    p_d.font.size = Pt(9)
    p_d.font.color.rgb = COLOR_TEXT_MAIN
    p_d.space_before = Pt(6)
 
 
# ==============================================================================
# Slide 9: 최근 시스템 수정 및 보완 이력 (v2.4.0 Changelog)
# ==============================================================================
s9 = create_base_slide("최근 시스템 수정 및 안정화 보완 이력 (v2.4.0)", "08. SYSTEM CHANGELOG (v2.4.0)")

changelog_cards_v24 = [
    ("🌐 서버 타임존 무결성 & 캐시 프리징 해결", 
     "• 배경: Render 클라우드(UTC)와 로컬(KST) 간 9시간 시차로 음수 diff 발생 -> 캐시 갱신 최대 9시간 동결 버그\n• 조치:\n   - get_now_kst() 표준화로 서버 OS 타임존과 무관하게 한국 표준시(UTC+9) 일치\n   - diff > TTL or diff < 0 무효화 안전장치 탑재 (음수 즉시 갱신)\n• 효과: 배포 후에도 실시간 스코어/이닝 즉시 갱신 및 캐시 무결성 100% 확보"),
    ("🧢 MLB 실시간 LIVE 정밀 판정 (Game Over)", 
     "• 배경: 공식 기록원 최종 승인 전(Game Over)인 경기가 LIVE 상태로 남아있던 현상\n• 조치:\n   - MLB Stats API statusCode('O', 'F', 'CR', 'FR') 및 abstractGameCode('F') 검증\n   - detailedState('Game Over', 'Final') 검증으로 경기 종료 즉시 '종료' 상태 전환\n• 효과: 끝난 경기가 LIVE로 오표기되는 버그 완전 방지 및 정확한 상태 표출"),
    ("⚾ 실시간 이닝 한국어화 & 투수/타자 매치업", 
     "• 배경: 기존 영문 약어 이닝 표기 및 실시간 승부 정보(투수/타자) 부재\n• 조치:\n   - 실시간 LIVE 이닝 포맷 한국어 정밀 매핑 ('8회초 1아웃', '8회말' 등)\n   - 공식 linescore에서 현재 마운드 투수(current_pitcher) 및 타석 타자(current_batter) 실시간 추출하여 표출\n• 효과: MLB 경기 진행 상황의 직관적 시각화 및 실시간 긴장감 전달"),
    ("🔄 당일 전 경기 확대 & 스마트 자동 폴링", 
     "• 배경: 당일 경기 수가 많을 때 일부 종료 경기가 누락되거나 백그라운드 갱신 부족\n• 조치:\n   - 종료 경기 25개, 예정 경기 16개로 노출 대폭 확대 (당일 15경기 전수 커버)\n   - LIVE 경기 시 25초, 비경기 시간대 90초 스마트 백그라운드 자동 폴링 탑재\n• 효과: 별도 새로고침 없이도 최신 경기 결과를 완전하고 쾌적하게 자동 열람")
]

for idx, (ctitle, cdesc) in enumerate(changelog_cards_v24):
    col = idx % 2
    row = idx // 2
    cx = 0.8 + col * 5.9
    cy = 1.7 + row * 2.55
    add_card(s9, cx, cy, 5.6, 2.35)
    tb = s9.shapes.add_textbox(Inches(cx + 0.2), Inches(cy + 0.15), Inches(5.2), Inches(2.05))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = ctitle
    p.font.name = "Malgun Gothic"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE

    p_d = tf.add_paragraph()
    p_d.text = cdesc
    p_d.font.name = "Malgun Gothic"
    p_d.font.size = Pt(8.5)
    p_d.font.color.rgb = COLOR_TEXT_MAIN
    p_d.space_before = Pt(5)


# ==============================================================================
# Slide 10: 누적 시스템 보완 및 릴리즈 이력 (v2.0.0 ~ v2.3.0)
# ==============================================================================
s10 = create_base_slide("누적 시스템 보완 및 릴리즈 이력 (v2.0.0 ~ v2.3.0)", "09. HISTORICAL CHANGELOG")

changelog_cards_prev = [
    ("⚡ v2.3.0 스마트 캐시 갱신 & LIVE 안전 판별", 
     "• 스마트 캐시: 30분 TTL 캐시 유지 + LIVE 경기 시 25초 주기 실시간 fetch\n• 안전 종료 판정: 경기 시작 기준 야구 5.5시간, 축구 3.5시간 초과 시 자동 종료\n• 실시간 중계 모달 UX 단독 팝업화: 외부 새 창 제거 -> 단독 내부 모달 표출\n• 네이버 새 창 보기 및 MLB 3D게임데이 바로가기 액션 버튼 지원"),
    ("🧢 v2.3.0 MLB 한국시간(KST) & 콘솔 무결성", 
     "• MLB 한국시간 자동 변환: UTC 기준 9시간 시차 반영 (%m.%d 요일 HH:MM)\n• MLB 30개 구단 공식 Stats API 팀 식별자(ID) 오타 전면 수정\n• 네이버 해외야구(wbaseball) API 사전 매핑으로 공식 gameId 100% 연동\n• F12 콘솔 무결성: iframe onload, ESPN artwork 401, Tailwind CDN 경고 0(Zero) 달성"),
    ("🖥️ v2.2.0 네이버 실시간 문자중계 모달 탑재", 
     "• LIVE 경기 카드에 [⚡ 실시간 중계확인] 버튼 인터랙티브 자동 전환\n• 네이버스포츠 실시간 문자중계 인라인 모달 연동 (볼카운트/투구추적/이닝결과)\n• 페이지 이탈 없이 실시간 중계를 확인하는 원스톱 UX 환경 구축"),
    ("🏆 v2.0.0 ~ v2.1.0 4대 스포츠 통합 & 레이아웃 개편", 
     "• 4대 스포츠 올인원 통합: KBO, K리그 1·2, 유럽 축구 5대리그, MLB 메이저리그\n• 상단 경기결과 스코어보드 / 하단 공식 영상 혁신 레이아웃 적용\n• 원클릭 상태 필터 칩 ([전체], [LIVE], [최근 결과], [금주/내일 예정]) 및 마이팀 개인화")
]

for idx, (ctitle, cdesc) in enumerate(changelog_cards_prev):
    col = idx % 2
    row = idx // 2
    cx = 0.8 + col * 5.9
    cy = 1.7 + row * 2.55
    add_card(s10, cx, cy, 5.6, 2.35)
    tb = s10.shapes.add_textbox(Inches(cx + 0.2), Inches(cy + 0.15), Inches(5.2), Inches(2.05))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = ctitle
    p.font.name = "Malgun Gothic"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE

    p_d = tf.add_paragraph()
    p_d.text = cdesc
    p_d.font.name = "Malgun Gothic"
    p_d.font.size = Pt(8.5)
    p_d.font.color.rgb = COLOR_TEXT_MAIN
    p_d.space_before = Pt(5)

output_ppt_path = "/Users/소스/WEB_SPORTS/SPORTS_HUB_프로젝트_설계_및_명세서.pptx"
prs.save(output_ppt_path)
print(f"PowerPoint file successfully generated at: {output_ppt_path}")

