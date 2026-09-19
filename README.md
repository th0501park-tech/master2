# 🏆 SPORTS HUB - 실시간 스포츠 종합 순위 & 기록 대시보드

> **버전**: v2.2.0  
> **공식 저장소**: [https://github.com/th0501park-tech/master2](https://github.com/th0501park-tech/master2)  
> **클라우드 배포 호스트**: [Render.com](https://render.com) (대시보드: [https://dashboard.render.com/](https://dashboard.render.com/))

---

## 📌 1. 프로젝트 소개

**SPORTS HUB**는 대한민국 4대 인기 스포츠의 실시간 스코어보드, 리그별 구단 순위, 선수 개인기록(타격/투수/득점/도움 등), 공식 하이라이트 영상 및 **네이버스포츠 실시간 문자중계**를 단일 화면에서 원스톱으로 제공하는 올인원 웹 대시보드 플랫폼입니다.

### ⚾ 지원 종목 및 리그
1. **KBO 프로야구**: 10개 구단 순위, 실시간 이닝/마운드 투수, 승·패전 결정투수, 오늘/내일 선발투수 예고, 네이버스포츠 실시간 문자중계
2. **K리그 (K1 · K2)**: K리그 1·2 전 구단 순위, 실시간 LIVE(전·후반 진행 분), 실시간 스코어, 득점/도움/무실점 개인기록, 네이버스포츠 실시간 문자중계
3. **해외축구 5대 리그**: 프리미어리그(EPL), 라리가, 분데스리가, 챔피언스리그(UCL), 유로파리그(UEL) 실시간 경기, KST 한국시간 자동 변환 일정, 리그별 순위
4. **MLB 메이저리그**: AL/NL 30개 구단 디비전 순위, 실시간 이닝, 승·패·세이브 투수, 선발 매치업, 타자/투수 리더보드, Film Room 공식 하이라이트

---

## ✨ 2. 핵심 기능

- **실시간(LIVE) 문자중계 팝업 모달 (`live-relay-modal`)**:
  - 경기가 실시간(LIVE)으로 진행 중일 경우 하단 `하이라이트` 버튼이 **`[⚡ 실시간 중계확인]`** 버튼으로 자동 전환
  - 클릭 시 네이버스포츠 공식 실시간 문자중계 페이지가 인라인 모달로 즉시 렌더링되어 볼카운트, 투구 추적, 이닝별 상세 결과를 페이지 이탈 없이 확인 가능
  - 상단 [새 창으로 보기] 외부 링크 및 ESC/배경 클릭 닫기 지원
- **상단 경기결과 / 하단 공식 영상 혁신 레이아웃**:
  - 접속 시 실시간 경기 스코어와 오늘/내일 일정을 상단에서 최우선 노출
- **원클릭 상태 필터 칩**:
  - `[전체]`, `[🔴 LIVE]`, `[최근 결과]`, `[금주/내일 예정]` 칩 클릭으로 원하는 경기만 즉시 필터링
- **마이팀(선호 구단) 개인화**:
  - 구단별 별표(★) 클릭 시 브라우저 `localStorage`에 영구 저장되어 해당 팀 경기 최상단 우선 배치 및 골드 강조
- **고성능 파일 캐싱 & Facade 영상 지연 로딩**:
  - 로컬 JSON 캐싱 엔진으로 외부 API 호출 쿼터 절약 및 0.5초 이내 초고속 페이지 로딩 유지

---

## 🏛️ 3. 시스템 아키텍처 (4-Tier)

```
[ 클라이언트 브라우저 ]
  │  HTML5 + TailwindCSS + Vanilla JS (SPA 인터랙션 & 모달 뷰어)
  ▼
[ 웹 애플리케이션 계층 ]
  │  run.py (Uvicorn ASGI) ── app/main.py (FastAPI) ── app/templates/index.html (Jinja2 SSR)
  ▼
[ 도메인 비즈니스 계층 ]
  │  kbo_service.py  │  kleague_service.py  │  mlb_service.py  │  overseas_soccer_service.py
  ▼
[ 영속성 캐시 & 외부 API 연동 계층 ]
  ├─ cache/*.json (로컬 파일 기반 영속성 캐시)
  └─ 네이버 스포츠 API, K리그 공식 포털, MLB Stats API, ESPN Soccer Scoreboard API
```

---

## 🚀 4. 로컬 실행 방법

### 요구 사항
- Python 3.10 이상 (Python 3.14 권장)
- pip 패키지 매니저

### 설치 및 실행
```bash
# 1. 저장소 클론
git clone https://github.com/th0501park-tech/master2.git
cd master2

# 2. 의존성 패키지 설치
pip install -r requirements.txt

# 3. 로컬 서버 기동
python run.py
```
- 브라우저 접속 주소: **`http://127.0.0.1:8000`**
- 환경 변수 지원:
  - `HOST`: 바인딩 IP (기본값: `127.0.0.1`)
  - `PORT`: 포트 번호 (기본값: `8000`)
  - `RELOAD`: 자동 리로드 여부 (기본값: `true`)

---

## ☁️ 5. Render.com 클라우드 배포 및 모니터링 가이드

본 프로젝트는 클라우드 호스팅 서비스인 [Render.com](https://render.com)에 원클릭으로 배포할 수 있도록 `Procfile` 및 `render.yaml`이 구성되어 있습니다.

### 5-1. Render.com에 배포하는 방법
1. **GitHub 푸시**:
   - 로컬 작업 완료 후 `main` 브랜치에 푸시합니다.
   ```bash
   git add .
   git commit -m "feat: 업데이트 내용"
   git push origin main
   ```
2. **Render.com 웹 서비스 생성**:
   - [Render 대시보드](https://dashboard.render.com/) 로그인 후 **[New +] -> [Web Service]** 클릭
   - GitHub 저장소 `th0501park-tech/master2` 연결 및 선택
3. **빌드 및 실행 명령어 설정**:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Auto-Deploy**: `Yes` (GitHub에 푸시할 때마다 자동 배포)
4. **배포 시작**:
   - [Create Web Service] 클릭 후 약 1~2분 내에 빌드 및 배포 완료!

### 5-2. Render 대시보드에서 모니터링하는 방법
- **대시보드 URL**: [https://dashboard.render.com/](https://dashboard.render.com/)
1. **Logs (실시간 로그 추적)**:
   - 좌측 메뉴 **[Logs]** 탭에서 Uvicorn ASGI 기동 로그, 클라이언트 HTTP 요청, 외부 API 응답 및 크롤링 상태를 실시간 스트리밍으로 확인합니다.
2. **Metrics (서버 리소스 모니터링)**:
   - 좌측 메뉴 **[Metrics]** 탭에서 CPU 사용률, Memory 사용량, HTTP 응답 상태 코드(2xx/4xx/5xx) 및 응답 지연 시간(Latency) 그래프를 실시간 모니터링합니다.
3. **Events (배포 이력 확인)**:
   - 좌측 메뉴 **[Events]** 탭에서 Git 커밋별 배포 시작, 빌드 성공/실패 이력을 확인합니다.
4. **Manual Deploy (수동 재배포 & 캐시 무효화)**:
   - 우측 상단 **[Manual Deploy] -> [Clear build cache & deploy]**를 통해 필요 시 캐시를 비우고 즉시 재빌드할 수 있습니다.

---

## 📑 6. 산출물 문서 목록

- 📑 **프로그램 명세서 및 시스템 설계서**: [`docs/PROGRAM_SPECIFICATION.md`](docs/PROGRAM_SPECIFICATION.md)
- 📊 **프로그램 명세서 Excel 문서**: [`SPORTS_HUB_프로그램명세서_및_설계서.xlsx`](SPORTS_HUB_프로그램명세서_및_설계서.xlsx)
- 📑 **시스템 설계 및 프로그램 명세서 PPT**: [`SPORTS_HUB_프로젝트_설계_및_명세서.pptx`](SPORTS_HUB_프로젝트_설계_및_명세서.pptx)
- 📑 **전체 프로세스 흐름도 및 배포·운영 PPT**: [`SPORTS_HUB_배포_및_운영_프로세스_흐름도.pptx`](SPORTS_HUB_배포_및_운영_프로세스_흐름도.pptx)