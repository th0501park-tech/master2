import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# 16:9 와이드 프레젠테이션 초기화
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

# 디자인 색상 팔레트
COLOR_NAVY = RGBColor(15, 23, 42)         # Slate 900 (다크 네이비)
COLOR_DARK_BLUE = RGBColor(30, 41, 59)    # Slate 800 (헤더/강조)
COLOR_CARD_BG = RGBColor(255, 255, 255)   # White
COLOR_CARD_BORDER = RGBColor(226, 232, 240) # Slate 200
COLOR_PRIMARY_BLUE = RGBColor(37, 99, 235)  # Blue 600
COLOR_ACCENT_CYAN = RGBColor(14, 165, 233)  # Sky 500
COLOR_ACCENT_GREEN = RGBColor(16, 185, 129) # Emerald 500
COLOR_ACCENT_AMBER = RGBColor(245, 158, 11) # Amber 500
COLOR_ACCENT_PURPLE = RGBColor(139, 92, 246)# Violet 500
COLOR_BG_LIGHT = RGBColor(248, 250, 252)    # Slate 50
COLOR_TEXT_MAIN = RGBColor(30, 41, 59)      # Slate 800
COLOR_TEXT_MUTED = RGBColor(100, 116, 139)  # Slate 500
COLOR_WHITE = RGBColor(255, 255, 255)

def create_base_slide(title_text, subtitle_text):
    """표준 슬라이드 기본 레이아웃 생성 (배경, 상단 헤더, 로고/태그)"""
    slide = prs.slides.add_slide(blank_layout)
    
    # 배경
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLOR_BG_LIGHT
    bg.line.fill.background()
    
    # 상단 헤더 바
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(1.15))
    header.fill.solid()
    header.fill.fore_color.rgb = COLOR_NAVY
    header.line.fill.background()
    
    # 장식 포인트 라인
    dec_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(1.15), Inches(13.333), Inches(0.04))
    dec_line.fill.solid()
    dec_line.fill.fore_color.rgb = COLOR_ACCENT_CYAN
    dec_line.line.fill.background()
    
    # 서브타이틀 (카테고리)
    sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.18), Inches(10), Inches(0.3))
    tf_sub = sub_box.text_frame
    tf_sub.word_wrap = True
    p_sub = tf_sub.paragraphs[0]
    p_sub.text = subtitle_text.upper()
    p_sub.font.name = "Malgun Gothic"
    p_sub.font.size = Pt(9.5)
    p_sub.font.bold = True
    p_sub.font.color.rgb = COLOR_ACCENT_CYAN
    
    # 메인 타이틀
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.42), Inches(10), Inches(0.6))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.name = "Malgun Gothic"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    
    # 우측 브랜드 태그
    brand_box = slide.shapes.add_textbox(Inches(10.2), Inches(0.35), Inches(2.3), Inches(0.5))
    tf_b = brand_box.text_frame
    p_b = tf_b.paragraphs[0]
    p_b.text = "SPORTS HUB PIPELINE"
    p_b.font.name = "Malgun Gothic"
    p_b.font.size = Pt(11)
    p_b.font.bold = True
    p_b.font.color.rgb = RGBColor(148, 163, 184)
    p_b.alignment = PP_ALIGN.RIGHT
    
    return slide

def add_card(slide, left_in, top_in, width_in, height_in, border_color=COLOR_CARD_BORDER, bg_color=COLOR_CARD_BG):
    """둥근 모서리 카드 쉐이프 추가"""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left_in), Inches(top_in), Inches(width_in), Inches(height_in))
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1.2)
    return card

# ==============================================================================
# Slide 1: 표지 (Cover Slide)
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)

bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
bg1.fill.solid()
bg1.fill.fore_color.rgb = COLOR_NAVY
bg1.line.fill.background()

# 좌측 블루 인디케이터
dec = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.2), Inches(1.8), Inches(0.12), Inches(3.4))
dec.fill.solid()
dec.fill.fore_color.rgb = COLOR_ACCENT_CYAN
dec.line.fill.background()

title_box = s1.shapes.add_textbox(Inches(1.5), Inches(1.7), Inches(10.8), Inches(3.6))
tf1 = title_box.text_frame
tf1.word_wrap = True

p1 = tf1.paragraphs[0]
p1.text = "END-TO-END DEPLOYMENT & CLOUD OPERATIONS GUIDE"
p1.font.name = "Malgun Gothic"
p1.font.size = Pt(13)
p1.font.bold = True
p1.font.color.rgb = RGBColor(56, 189, 248) # Sky 400

p2 = tf1.add_paragraph()
p2.text = "SPORTS HUB 배포 및 운영 프로세스 흐름도"
p2.font.name = "Malgun Gothic"
p2.font.size = Pt(32)
p2.font.bold = True
p2.font.color.rgb = COLOR_WHITE
p2.space_before = Pt(12)

p3 = tf1.add_paragraph()
p3.text = "로컬 소스 개발부터 GitHub 푸시, Render 호스트 서버 배포 및 대시보드 실시간 모니터링까지"
p3.font.name = "Malgun Gothic"
p3.font.size = Pt(16)
p3.font.color.rgb = RGBColor(226, 232, 240)
p3.space_before = Pt(14)

# 하단 정보 카드
meta_box = s1.shapes.add_textbox(Inches(1.5), Inches(5.4), Inches(10.8), Inches(1.4))
tf_meta = meta_box.text_frame
p_meta1 = tf_meta.paragraphs[0]
p_meta1.text = "• 프로젝트 저장소: https://github.com/th0501park-tech/master2  (Branch: main)"
p_meta1.font.name = "Malgun Gothic"
p_meta1.font.size = Pt(11)
p_meta1.font.color.rgb = RGBColor(148, 163, 184)

p_meta2 = tf_meta.add_paragraph()
p_meta2.text = "• 클라우드 호스트: Render.com Web Service  |  모니터링: https://dashboard.render.com/"
p_meta2.font.name = "Malgun Gothic"
p_meta2.font.size = Pt(11)
p_meta2.font.color.rgb = RGBColor(148, 163, 184)
p_meta2.space_before = Pt(4)

p_meta3 = tf_meta.add_paragraph()
p_meta3.text = "• 작성 버전: v2.3.0 (스마트 캐시 & LIVE 안전 판정 & 중계 모달 고도화)  |  작성일: 2026-09-20"
p_meta3.font.name = "Malgun Gothic"
p_meta3.font.size = Pt(11)
p_meta3.font.color.rgb = RGBColor(148, 163, 184)
p_meta3.space_before = Pt(4)


# ==============================================================================
# Slide 2: E2E 파이프라인 전체 프로세스 맵
# ==============================================================================
s2 = create_base_slide("엔드투엔드(E2E) 배포 및 운영 파이프라인 개요", "01. PIPELINE OVERVIEW")

pipe_steps = [
    ("Phase 1", "💻 소스 개발 및 로컬 검증", RGBColor(37, 99, 235), 
     "• 로컬 개발 환경 구성\n• python run.py 서버 기동\n• 4대 스포츠 실시간 데이터 검증\n• 문자중계 모달 및 SPA 동작 확인\n• 캐시 파일 무결성 체크"),
    ("Phase 2", "🐙 GitHub 소스 푸시", RGBColor(139, 92, 246), 
     "• Git 변경사항 스테이징(add)\n• 작업 단위 커밋(commit)\n• 원격 저장소 푸시(push origin main)\n• GitHub master2 브랜치 동기화\n• Render 자동 배포 Webhook 트리거"),
    ("Phase 3", "☁️ Render 호스트 배포", RGBColor(16, 185, 129), 
     "• Web Service 인스턴스 프로비저닝\n• pip install -r requirements.txt\n• Procfile / Start Command 실행\n• uvicorn app.main:app 기동\n• 글로벌 CDN & HTTPS 자동 활성화"),
    ("Phase 4", "📊 Render 실시간 모니터링", RGBColor(245, 158, 11), 
     "• dashboard.render.com 접속\n• 실시간 Logs 스트리밍 확인\n• CPU / Memory 사용률 모니터링\n• HTTP Status(2xx/4xx/5xx) 관제\n• 수동 배포 및 캐시 초기화 관리")
]

for idx, (pnum, ptitle, pcolor, pdesc) in enumerate(pipe_steps):
    cx = 0.8 + idx * 2.98
    add_card(s2, cx, 1.65, 2.78, 5.0, border_color=pcolor)
    
    # 상단 컬러 바 태그
    hbar = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(cx + 0.05), Inches(1.7), Inches(2.68), Inches(0.45))
    hbar.fill.solid()
    hbar.fill.fore_color.rgb = pcolor
    hbar.line.fill.background()
    
    tb_h = s2.shapes.add_textbox(Inches(cx + 0.1), Inches(1.72), Inches(2.58), Inches(0.4))
    tf_h = tb_h.text_frame
    p_th = tf_h.paragraphs[0]
    p_th.text = pnum
    p_th.font.name = "Malgun Gothic"
    p_th.font.size = Pt(11)
    p_th.font.bold = True
    p_th.font.color.rgb = COLOR_WHITE
    p_th.alignment = PP_ALIGN.CENTER
    
    # 본문 박스
    tb = s2.shapes.add_textbox(Inches(cx + 0.15), Inches(2.25), Inches(2.48), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p_t = tf.paragraphs[0]
    p_t.text = ptitle
    p_t.font.name = "Malgun Gothic"
    p_t.font.size = Pt(12)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_NAVY
    
    p_d = tf.add_paragraph()
    p_d.text = pdesc
    p_d.font.name = "Malgun Gothic"
    p_d.font.size = Pt(9)
    p_d.font.color.rgb = COLOR_TEXT_MAIN
    p_d.space_before = Pt(10)


# ==============================================================================
# Slide 3: Phase 1 - 소스 구조 및 로컬 개발/테스트 환경
# ==============================================================================
s3 = create_base_slide("Phase 1: 소스 구조 분석 및 로컬 개발/검증 절차", "02. LOCAL DEVELOPMENT")

# 좌측: 핵심 파일 구조 카드
add_card(s3, 0.8, 1.65, 5.6, 5.0)
tb_s3_l = s3.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.6))
tf_l = tb_s3_l.text_frame
tf_l.word_wrap = True

p = tf_l.paragraphs[0]
p.text = "📂 프로젝트 소스 핵심 구조 및 파일 역할"
p.font.name = "Malgun Gothic"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = COLOR_PRIMARY_BLUE

struct_text = (
    "• app/main.py : FastAPI 엔트리포인트, 라우트 바인딩 및 정적 파일 마운트\n"
    "• app/services/ : 4대 스포츠 실시간 데이터 수집 및 비즈니스 로직\n"
    "   - kbo_service.py : KBO 스코어보드, 경기상태, 선발/결정투수, 순위\n"
    "   - kleague_service.py : 네이버 K리그 API + 공식포털 연동, 라이브 분\n"
    "   - overseas_soccer_service.py : ESPN API 연동, KST 시간 보정\n"
    "   - mlb_service.py : MLB Stats API, 실시간 이닝, 투수 결정기록\n"
    "• app/templates/index.html : SSR 대시보드 템플릿 및 문자중계 모달\n"
    "• app/static/js/main.js : SPA 필터링, 모달 팝업, Facade 비디오 제어\n"
    "• Procfile & render.yaml : Render.com 배포 정의 인프라 설정\n"
    "• requirements.txt : FastAPI, Uvicorn, Requests, Jinja2 의존성 명세"
)
p_desc = tf_l.add_paragraph()
p_desc.text = struct_text
p_desc.font.name = "Consolas"
p_desc.font.size = Pt(8.5)
p_desc.font.color.rgb = COLOR_TEXT_MAIN
p_desc.space_before = Pt(8)

# 우측: 로컬 실행 및 검증 절차 카드
add_card(s3, 6.7, 1.65, 5.8, 5.0)
tb_s3_r = s3.shapes.add_textbox(Inches(6.9), Inches(1.8), Inches(5.4), Inches(4.6))
tf_r = tb_s3_r.text_frame
tf_r.word_wrap = True

p_r = tf_r.paragraphs[0]
p_r.text = "⚙️ 로컬 서버 실행 및 사전 검증 절차"
p_r.font.name = "Malgun Gothic"
p_r.font.size = Pt(13)
p_r.font.bold = True
p_r.font.color.rgb = COLOR_PRIMARY_BLUE

local_run_text = (
    "1. 가상환경 및 의존성 패키지 설치 확인:\n"
    "   $ pip install -r requirements.txt\n\n"
    "2. 로컬 개발 서버 실행 (run.py):\n"
    "   $ python run.py\n"
    "   → INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)\n\n"
    "3. 브라우저 접속 및 주요 기능 사전 테스트:\n"
    "   • http://127.0.0.1:8000 접속 확인\n"
    "   • [🔴 LIVE] 필터 클릭 시 실시간 경기 정상 노출 여부\n"
    "   • LIVE 경기 하단 [⚡ 실시간 중계확인] 클릭 → 네이버 문자중계 모달 검증\n"
    "   • 마이팀(선호구단) 별표 클릭 시 최상단 고정 및 유지 확인\n\n"
    "4. 로컬 캐시 무결성 검증:\n"
    "   • cache/ 폴더 내 4개 JSON 파일 정상 생성 및 데이터 필드 확인"
)
p_r_desc = tf_r.add_paragraph()
p_r_desc.text = local_run_text
p_r_desc.font.name = "Consolas"
p_r_desc.font.size = Pt(8.5)
p_r_desc.font.color.rgb = COLOR_TEXT_MAIN
p_r_desc.space_before = Pt(8)


# ==============================================================================
# Slide 4: Phase 2 - Git 버전 관리 및 GitHub 배포
# ==============================================================================
s4 = create_base_slide("Phase 2: Git 버전 관리 및 GitHub 원격 저장소 배포", "03. GITHUB DEPLOYMENT")

git_cards = [
    ("1️⃣ Git 상태 확인 및 스테이징 (Stage)", "git status & git add",
     "• 작업 디렉토리의 변경된 파일 목록 확인:\n"
     "   $ git status\n"
     "• 수정된 소스, 템플릿, 스크립트, 산출물 문서 전체 스테이징:\n"
     "   $ git add .\n"
     "• 불필요한 임시 파일(__pycache__, .DS_Store)은 .gitignore로 자동 제외"),
    ("2️⃣ 의미 있는 커밋 생성 (Commit)", "git commit -m \"message\"",
     "• 기능 단위 및 표준 커밋 컨벤션(Conventional Commits) 준수:\n"
     "   $ git commit -m \"feat: 실시간 중계확인 모달 및 K리그 라이브 동기화\"\n"
     "   $ git commit -m \"docs: 산출물 문서 및 배포 프로세스 PPT 업데이트\"\n"
     "• 커밋 메시지에 명확한 변경 사유와 범위 기재하여 이력 추적성 확보"),
    ("3️⃣ 원격 메인 브랜치 푸시 (Push)", "git push origin main",
     "• 원격 GitHub 저장소(th0501park-tech/master2)로 최종 반영:\n"
     "   $ git push origin main\n"
     "• 푸시 성공 시 GitHub 저장소 커밋 해시(SHA) 생성\n"
     "• 원격 저장소의 main 브랜치가 갱신되면서 Render 배포 트리거 자동 발송"),
    ("4️⃣ GitHub 저장소 확인 및 Webhook", "https://github.com/.../master2",
     "• 웹 브라우저로 저장소 방문하여 최신 커밋 반영 상태 확인\n"
     "• GitHub Repository Settings → Webhooks 항목에서 Render 연동 상태 확인\n"
     "• push 이벤트 발생 시 Render.com으로 Payload가 자동 전송되어 빌드 시작")
]

for idx, (gtitle, gcmd, gdesc) in enumerate(git_cards):
    col = idx % 2
    row = idx // 2
    cx = 0.8 + col * 5.9
    cy = 1.65 + row * 2.55
    add_card(s4, cx, cy, 5.6, 2.38)
    tb = s4.shapes.add_textbox(Inches(cx + 0.2), Inches(cy + 0.15), Inches(5.2), Inches(2.05))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = gtitle
    p.font.name = "Malgun Gothic"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE

    p_c = tf.add_paragraph()
    p_c.text = gcmd
    p_c.font.name = "Consolas"
    p_c.font.size = Pt(9.5)
    p_c.font.bold = True
    p_c.font.color.rgb = COLOR_TEXT_MUTED
    p_c.space_before = Pt(2)

    p_d = tf.add_paragraph()
    p_d.text = gdesc
    p_d.font.name = "Malgun Gothic"
    p_d.font.size = Pt(8.8)
    p_d.font.color.rgb = COLOR_TEXT_MAIN
    p_d.space_before = Pt(6)


# ==============================================================================
# Slide 5: Phase 3 - Render.com 호스트 서버 디플로이 설정
# ==============================================================================
s5 = create_base_slide("Phase 3: Render.com 호스트 서버 배포 설정 및 구성", "04. RENDER DEPLOY SETUP")

# 좌측: 신규 웹 서비스 생성 가이드
add_card(s5, 0.8, 1.65, 5.6, 5.0)
tb_s5_l = s5.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.6))
tf_s5_l = tb_s5_l.text_frame
tf_s5_l.word_wrap = True

p_s5_1 = tf_s5_l.paragraphs[0]
p_s5_1.text = "🚀 Render.com Web Service 등록 4단계"
p_s5_1.font.name = "Malgun Gothic"
p_s5_1.font.size = Pt(13)
p_s5_1.font.bold = True
p_s5_1.font.color.rgb = COLOR_PRIMARY_BLUE

render_steps = (
    "Step 1: Render 가입 및 대시보드 진입\n"
    "• https://render.com 접속 → GitHub 계정으로 간편 로그인\n"
    "• 우측 상단 [+ New] 버튼 클릭 → [Web Service] 선택\n\n"
    "Step 2: GitHub Repository 연결 (Connect)\n"
    "• [Connect a repository] 목록에서 'master2' 저장소 선택\n"
    "• 권한 미부여 시 [Configure access on GitHub]로 저장소 승인\n\n"
    "Step 3: 기본 배포 사양 구성\n"
    "• Name: sports-hub-dashboard (원하는 서비스명 입력)\n"
    "• Region: Singapore (국내 사용자 접속 시 지연 최소화)\n"
    "• Branch: main (배포 기준 브랜치 지정)\n"
    "• Runtime: Python 3\n\n"
    "Step 4: 인스턴스 플랜 선택 및 생성 완료\n"
    "• Instance Type: Free ($0/month) 또는 Starter\n"
    "• [Create Web Service] 버튼 클릭하여 초기 빌드 개시"
)
p_s5_1_desc = tf_s5_l.add_paragraph()
p_s5_1_desc.text = render_steps
p_s5_1_desc.font.name = "Malgun Gothic"
p_s5_1_desc.font.size = Pt(8.8)
p_s5_1_desc.font.color.rgb = COLOR_TEXT_MAIN
p_s5_1_desc.space_before = Pt(8)

# 우측: 핵심 빌드/실행 명령어 및 IaC 구성
add_card(s5, 6.7, 1.65, 5.8, 5.0)
tb_s5_r = s5.shapes.add_textbox(Inches(6.9), Inches(1.8), Inches(5.4), Inches(4.6))
tf_s5_r = tb_s5_r.text_frame
tf_s5_r.word_wrap = True

p_s5_2 = tf_s5_r.paragraphs[0]
p_s5_2.text = "⚡ 빌드 & 실행 커맨드 및 Procfile 명세"
p_s5_2.font.name = "Malgun Gothic"
p_s5_2.font.size = Pt(13)
p_s5_2.font.bold = True
p_s5_2.font.color.rgb = COLOR_PRIMARY_BLUE

render_cmd_desc = (
    "■ Build Command (빌드 시 의존성 패키지 설치):\n"
    "   pip install -r requirements.txt\n"
    "   • FastAPI, Uvicorn, Jinja2, Requests 등 핵심 라이브러리 설치\n\n"
    "■ Start Command (웹 애플리케이션 기동):\n"
    "   uvicorn app.main:app --host 0.0.0.0 --port $PORT\n"
    "   • Render가 동적으로 할당하는 $PORT 환경변수에 바인딩\n\n"
    "■ Procfile 지원 (프로젝트 루트에 기포함):\n"
    "   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT\n"
    "   • Start Command 생략 시 Procfile에 정의된 web 프로세스 자동 실행\n\n"
    "■ render.yaml (Infrastructure as Code 지원):\n"
    "   services:\n"
    "     - type: web\n"
    "       name: sports-hub\n"
    "       env: python\n"
    "       plan: free\n"
    "       buildCommand: pip install -r requirements.txt\n"
    "       startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT"
)
p_s5_2_desc = tf_s5_r.add_paragraph()
p_s5_2_desc.text = render_cmd_desc
p_s5_2_desc.font.name = "Consolas"
p_s5_2_desc.font.size = Pt(8.2)
p_s5_2_desc.font.color.rgb = COLOR_TEXT_MAIN
p_s5_2_desc.space_before = Pt(8)


# ==============================================================================
# Slide 6: Phase 4 - 자동 빌드 및 릴리즈 파이프라인 수명주기
# ==============================================================================
s6 = create_base_slide("Phase 4: 자동 빌드 및 릴리즈 수명주기 (Lifecycle)", "05. BUILD & RELEASE LIFECYCLE")

lifecycle_steps = [
    ("Step 1. Webhook 감지", "GitHub Push 이벤트 수신",
     "• 로컬에서 git push origin main 실행\n"
     "• GitHub이 Render Webhook API로 신규 커밋 페이로드 전송\n"
     "• Render 대시보드 상태: 'Deploy in progress' 표시"),
    ("Step 2. 컨테이너 빌드", "환경 구축 및 패키지 설치",
     "• 격리된 Linux 컨테이너 환경 프로비저닝\n"
     "• Python 3.10+ 런타임 환경 활성화\n"
     "• pip install -r requirements.txt 실행 및 캐시 빌드"),
    ("Step 3. 서버 헬스체크", "Uvicorn 기동 및 포트 바인딩",
     "• uvicorn app.main:app --host 0.0.0.0 --port $PORT 실행\n"
     "• 백엔드 캐시 엔진 및 라우터 초기화\n"
     "• Render 로드밸런서의 포트 응답 헬스체크 통과"),
    ("Step 4. 트래픽 무중단 전환", "Live 배포 완료 및 SSL 적용",
     "• 새 컨테이너로 실시간 트래픽 무중단 라우팅 전환\n"
     "• 무료 자동 갱신 Let's Encrypt SSL/TLS 인증서 적용\n"
     "• 최종 서비스 상태: 'Live' (온라인 정상 서비스)")
]

for idx, (ltitle, lsub, ldesc) in enumerate(lifecycle_steps):
    cx = 0.8 + idx * 2.98
    add_card(s6, cx, 1.65, 2.78, 5.0)
    
    # 상단 넘버링 헤더
    nh = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(cx + 0.05), Inches(1.7), Inches(2.68), Inches(0.45))
    nh.fill.solid()
    nh.fill.fore_color.rgb = COLOR_DARK_BLUE
    nh.line.fill.background()
    
    tb_nh = s6.shapes.add_textbox(Inches(cx + 0.1), Inches(1.72), Inches(2.58), Inches(0.4))
    tf_nh = tb_nh.text_frame
    p_nh = tf_nh.paragraphs[0]
    p_nh.text = ltitle
    p_nh.font.name = "Malgun Gothic"
    p_nh.font.size = Pt(10)
    p_nh.font.bold = True
    p_nh.font.color.rgb = COLOR_WHITE
    p_nh.alignment = PP_ALIGN.CENTER
    
    # 본문
    tb = s6.shapes.add_textbox(Inches(cx + 0.15), Inches(2.25), Inches(2.48), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p_s = tf.paragraphs[0]
    p_s.text = lsub
    p_s.font.name = "Malgun Gothic"
    p_s.font.size = Pt(11.5)
    p_s.font.bold = True
    p_s.font.color.rgb = COLOR_PRIMARY_BLUE
    
    p_d = tf.add_paragraph()
    p_d.text = ldesc
    p_d.font.name = "Malgun Gothic"
    p_d.font.size = Pt(9)
    p_d.font.color.rgb = COLOR_TEXT_MAIN
    p_d.space_before = Pt(10)


# ==============================================================================
# Slide 7: Phase 5 - https://dashboard.render.com/ 실시간 모니터링 가이드
# ==============================================================================
s7 = create_base_slide("Phase 5: https://dashboard.render.com/ 에서 내 페이지 모니터링", "06. DASHBOARD MONITORING")

monitor_cards = [
    ("📜 1. Logs (실시간 스트리밍 로그)", "https://dashboard.render.com/web/.../logs",
     "• Uvicorn 서버 상태: 'Application startup complete.', 'Uvicorn running on ...'\n"
     "• HTTP 요청 추적: IP, Method, URI, 응답코드(200 OK), 처리속도 실시간 출력\n"
     "• 캐시 갱신 확인: 백엔드 크롤러의 데이터 갱신 및 에러 로그 실시간 감지\n"
     "• 필터 및 검색: 검색창을 통해 'ERROR', '404', 'Started' 키워드 즉시 필터링"),
    ("📈 2. Metrics (서버 리소스 & 성능 지표)", "https://dashboard.render.com/web/.../metrics",
     "• CPU Usage: CPU 사용률 그래프 실시간 모니터링 (과도한 연산 및 스파이크 감지)\n"
     "• Memory Usage: RAM 점유율 추적 (Free Tier 512MB 한도 초과 여부 감시)\n"
     "• HTTP Status Codes: 2xx(정상), 4xx(클라이언트오류), 5xx(서버장애) 발생 비율\n"
     "• Response Times: P50 / P95 / P99 응답 지연 시간 그래프 제공"),
    ("🕒 3. Events (배포 및 인프라 이벤트 이력)", "https://dashboard.render.com/web/.../events",
     "• Git 커밋별 배포 이력: 커밋 해시(Commit SHA), 작성자, 변경 내용 표시\n"
     "• 배포 라이프사이클 이력: Deploy started → Build successful → Service live\n"
     "• 서비스 재시작(Restart) 및 슬립 모드(Instance spun down) 타임스탬프 기록\n"
     "• 배포 실패(Deploy failed) 시 상세 원인 파악 및 이전 버전 원클릭 롤백"),
    ("⚙️ 4. Environment & Settings", "https://dashboard.render.com/web/.../settings",
     "• Environment Variables: HOST, PORT, LOG_LEVEL 등 런타임 환경변수 즉시 수정\n"
     "• Auto Deploy 토글: GitHub Push 시 자동 배포 On/Off 제어\n"
     "• Custom Domains: 보유 도메인 연결 및 CNAME 레코드/자동 SSL 인증서 관리\n"
     "• Suspend / Delete: 서비스 임시 중단 및 영구 삭제 제어")
]

for idx, (mtitle, murl, mdesc) in enumerate(monitor_cards):
    col = idx % 2
    row = idx // 2
    cx = 0.8 + col * 5.9
    cy = 1.65 + row * 2.55
    add_card(s7, cx, cy, 5.6, 2.38)
    tb = s7.shapes.add_textbox(Inches(cx + 0.2), Inches(cy + 0.15), Inches(5.2), Inches(2.05))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = mtitle
    p.font.name = "Malgun Gothic"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE

    p_u = tf.add_paragraph()
    p_u.text = murl
    p_u.font.name = "Consolas"
    p_u.font.size = Pt(8.5)
    p_u.font.bold = True
    p_u.font.color.rgb = COLOR_TEXT_MUTED
    p_u.space_before = Pt(2)

    p_d = tf.add_paragraph()
    p_d.text = mdesc
    p_d.font.name = "Malgun Gothic"
    p_d.font.size = Pt(8.8)
    p_d.font.color.rgb = COLOR_TEXT_MAIN
    p_d.space_before = Pt(6)


# ==============================================================================
# Slide 8: Phase 6 - 실전 운영 팁, 문제 해결 및 슬립 모드 대응
# ==============================================================================
s8 = create_base_slide("Phase 6: 실전 운영 팁, 슬립 모드 대응 및 문제 해결", "07. OPERATIONS & TROUBLESHOOTING")

tips_cards = [
    ("💤 Render Free Tier 슬립 모드 대응", 
     "• 특징: 15분 동안 외부 HTTP 트래픽이 없으면 인스턴스가 슬립(Spin-down) 상태 전환\n"
     "• 영향: 슬립 후 첫 접속 시 서버 기동(Spin-up)에 약 30~50초의 대기 지연 발생\n"
     "• 상시 유지 팁 (Keep-Alive Ping):\n"
     "   1. 무료 모니터링 도구(UptimeRobot, Cron-job.org) 가입\n"
     "   2. Render 서비스 URL(https://<app-name>.onrender.com)을 10분 간격 HTTP 핑 등록\n"
     "   3. 24시간 슬립 없이 즉각적인 0.5초 응답 속도 유지 가능"),
    ("🔄 수동 재배포 및 캐시 초기화 (Clear Cache)", 
     "• 상황: requirements.txt 패키지 충돌 또는 기존 빌드 캐시로 인한 오류 발생 시\n"
     "• 해결 절차:\n"
     "   1. Render 대시보드 진입 → 대상 Web Service 선택\n"
     "   2. 우측 상단 [Manual Deploy] 드롭다운 버튼 클릭\n"
     "   3. [Clear build cache & deploy] 선택 실행\n"
     "   4. 기존 캐시를 완전히 삭제하고 깨끗한 환경에서 신규 빌드 진행"),
    ("⏪ 이전 안정 버전 원클릭 롤백 (Rollback)", 
     "• 상황: 신규 기능 푸시 후 예기치 못한 프로덕션 런타임 오류 발생 시\n"
     "• 해결 절차:\n"
     "   1. 대시보드 좌측 메뉴에서 [Events] 또는 [Deploys] 클릭\n"
     "   2. 이전에 정상 작동했던 커밋 항목의 우측 [···] 메뉴 클릭\n"
     "   3. [Rollback to this deploy] 클릭\n"
     "   4. 1초 이내에 이전 안정 버전으로 즉각 복구되어 무장애 연속성 확보"),
    ("🔍 배포 에러(Build Failed) 시 체크리스트", 
     "• 1. requirements.txt 오타 또는 미지원 버전 명시 여부 점검\n"
     "• 2. Start Command 포트 변수 점검 (--port $PORT 가 정확히 기재되었는지)\n"
     "• 3. Python 버전 호환성 점검 (Render 기본 Python 3.10+ 환경)\n"
     "• 4. 로컬 환경에서 python run.py가 오류 없이 실행되는지 재확인\n"
     "• 5. .gitignore에 필수 코드 파일이 실수로 포함되어 누락되었는지 확인")
]

for idx, (ttitle, tdesc) in enumerate(tips_cards):
    col = idx % 2
    row = idx // 2
    cx = 0.8 + col * 5.9
    cy = 1.65 + row * 2.55
    add_card(s8, cx, cy, 5.6, 2.38)
    tb = s8.shapes.add_textbox(Inches(cx + 0.2), Inches(cy + 0.15), Inches(5.2), Inches(2.05))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = ttitle
    p.font.name = "Malgun Gothic"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY_BLUE

    p_d = tf.add_paragraph()
    p_d.text = tdesc
    p_d.font.name = "Malgun Gothic"
    p_d.font.size = Pt(8.8)
    p_d.font.color.rgb = COLOR_TEXT_MAIN
    p_d.space_before = Pt(6)


# ==============================================================================
# Slide 9: 전체 배포 & 모니터링 체크리스트 및 최종 요약
# ==============================================================================
s9 = create_base_slide("전체 배포 & 모니터링 종합 체크리스트 및 가이드 요약", "08. CHECKLIST & SUMMARY")

# 종합 체크리스트 테이블형 카드
add_card(s9, 0.8, 1.65, 11.7, 5.0)
tb_s9 = s9.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(4.6))
tf_s9 = tb_s9.text_frame
tf_s9.word_wrap = True

p_s9_t = tf_s9.paragraphs[0]
p_s9_t.text = "📋 단계별 배포 및 모니터링 검증 체크리스트"
p_s9_t.font.name = "Malgun Gothic"
p_s9_t.font.size = Pt(13)
p_s9_t.font.bold = True
p_s9_t.font.color.rgb = COLOR_PRIMARY_BLUE

chk_text = (
    "구분          단계 및 수행 작업                            확인 방법 및 기대 결과                                 상태\n"
    "──────────────────────────────────────────────────────────────────────────────────────────\n"
    "로컬 검증     1. 로컬 가상환경 및 서버 기동                python run.py 실행 시 http://127.0.0.1:8000 정상 기동  [ 완료 ]\n"
    "로컬 검증     2. 신규 기능 (문자중계/K리그 라이브) 점검    LIVE 경기 클릭 시 네이버 문자중계 모달 정상 팝업       [ 완료 ]\n"
    "Git 형상관리  3. 변경 코드 및 산출물 문서 스테이징         git add . 후 git status로 추적 파일 확인               [ 완료 ]\n"
    "Git 형상관리  4. 커밋 생성 및 원격 메인 푸시               git commit & git push origin main 성공                 [ 완료 ]\n"
    "Render 배포   5. Render Web Service Webhook 트리거         dashboard.render.com 에서 'Deploy in progress' 확인    [ 대기/자동 ]\n"
    "Render 배포   6. 의존성 빌드 및 Uvicorn 기동               pip install 성공 및 Uvicorn Running 포트 바인딩 확인   [ 대기/자동 ]\n"
    "대시보드 관제 7. Logs 탭 실시간 로그 스트리밍 확인         GET 200 OK 응답 및 에러 로그 부재 확인                 [ 상시 모니터링 ]\n"
    "대시보드 관제 8. Metrics 탭 CPU/RAM 지표 점검              RAM 사용량 < 512MB 및 정상 CPU 점유율 확인             [ 상시 모니터링 ]\n"
    "실서비스 검증 9. 프로덕션 도메인 접속 테스트               https://<app>.onrender.com 브라우저 접속 및 기능 점검  [ 완료 ]\n"
    "무중단 운영   10. 슬립 방지 UptimeRobot 설정               10분 주기 핑 등록으로 상시 응답 속도 확보              [ 권장 설정 ]\n"
    "──────────────────────────────────────────────────────────────────────────────────────────\n"
    "★ 핵심 요약: 소스 수정 후 'git push origin main' 한 줄로 클라우드 자동 배포가 완료되며,\n"
    "   dashboard.render.com의 Logs 및 Metrics 탭에서 실시간 가동 상태를 24시간 완벽하게 관제할 수 있습니다."
)
p_chk = tf_s9.add_paragraph()
p_chk.text = chk_text
p_chk.font.name = "Consolas"
p_chk.font.size = Pt(8.5)
p_chk.font.color.rgb = COLOR_TEXT_MAIN
p_chk.space_before = Pt(8)

output_deploy_ppt_path = "/Users/소스/WEB_SPORTS/SPORTS_HUB_배포_및_운영_프로세스_흐름도.pptx"
prs.save(output_deploy_ppt_path)
print(f"Deployment Pipeline PowerPoint successfully generated at: {output_deploy_ppt_path}")
