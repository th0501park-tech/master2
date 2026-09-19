# 🏆 SPORTS HUB - 프로그램 명세서 및 시스템 설계서

> **버전**: v2.2.0  
> **작성일**: 2026-09-19  
> **저장소**: [https://github.com/th0501park-tech/master2](https://github.com/th0501park-tech/master2)  
> **산출물 파일**:
> - 📊 Excel 문서: [SPORTS_HUB_프로그램명세서_및_설계서.xlsx](file:///Users/소스/WEB_SPORTS/SPORTS_HUB_프로그램명세서_및_설계서.xlsx)
> - 📑 PowerPoint 프레젠테이션 (아키텍처 및 명세): [SPORTS_HUB_프로젝트_설계_및_명세서.pptx](file:///Users/소스/WEB_SPORTS/SPORTS_HUB_프로젝트_설계_및_명세서.pptx)
> - 📑 PowerPoint 프레젠테이션 (배포 및 운영 흐름도): [SPORTS_HUB_배포_및_운영_프로세스_흐름도.pptx](file:///Users/소스/WEB_SPORTS/SPORTS_HUB_배포_및_운영_프로세스_흐름도.pptx)

---

## 1. 프로젝트 개요

**SPORTS HUB**는 대한민국 4대 인기 스포츠(KBO 프로야구, K리그 1·2, 유럽 5대 축구리그, MLB 메이저리그)의 실시간 경기 스코어, 리그 순위, 선수 개인기록, 공식 하이라이트 영상 및 네이버스포츠 실시간 문자중계를 단일 웹 허브에서 통합 제공하는 올인원 대시보드 플랫폼입니다.

### 핵심 가치 및 특징
1. **상단 경기결과 / 하단 공식 영상 레이아웃**: 사이트 접속 시 실시간 경기 스코어와 오늘/내일 일정을 최상단에서 즉시 확인 가능.
2. **실시간(LIVE) 문자중계 모달 (`live-relay-modal`)**:
   - 경기가 실시간(LIVE)으로 진행 중일 경우 하단 `하이라이트` 버튼이 **`[⚡ 실시간 중계확인]`** 버튼으로 자동 전환.
   - 클릭 시 네이버스포츠 실시간 문자중계 페이지(`https://m.sports.naver.com/game/{game_id}/relay`)를 모달 팝업으로 직접 렌더링하여 볼카운트, 투구 추적, 이닝별 타석 결과를 페이지 이탈 없이 실시간 확인 가능.
   - 상단 [새 창으로 보기] 외부 링크 버튼 및 `ESC` 키/배경 클릭 닫기 지원.
3. **야구 (KBO / MLB)**: 실시간 이닝 및 마운드 투수 정보, 최근 경기 승·패·세이브 결정투수, 오늘/내일 선발투수 예고 지원.
4. **축구 (K리그 / 해외축구)**:
   - K리그 공식 API 상태코드(`1S`, `2S`, `HT`, `ET`, `PK`) 및 네이버 스포츠 실시간 축구 API(`kfootball`) 연동으로 실시간 LIVE 스코어, 전·후반 진행 분 정보, 네이버 `gameId` 매핑.
   - 해외축구 UTC 시간의 한국 표준시(KST, UTC+9) 자동 변환 표기.
5. **상태별 원클릭 필터 칩**: `[전체]`, `[🔴 LIVE]`, `[최근 결과]`, `[금주/내일 예정]` 원클릭 필터링.
6. **마이팀(선호 구단) 개인화**: 브라우저 로컬스토리지에 응원팀을 등록하여 최상단 우선 노출 및 골드 하이라이트.
7. **고성능 캐싱 & Facade 영상 지연 로딩**: 외부 API 호출 쿼터를 아끼고 초기 로딩 속도 0.5초 이내 유지.

---

## 2. 시스템 아키텍처 (4-Tier Layered Architecture)

```mermaid
graph TD
    Client["브라우저 (HTML5 / TailwindCSS / Vanilla JS)"]
    
    subgraph "Application Layer"
        FastAPI["FastAPI Web Server (run.py / app.main)"]
        Jinja2["Jinja2 SSR Template Engine (index.html)"]
    end

    subgraph "Business / Service Layer"
        KBO["KBO Service (kbo_service.py)"]
        KL["K-League Service (kleague_service.py)"]
        MLB["MLB Service (mlb_service.py)"]
        SOC["Overseas Soccer Service (overseas_soccer_service.py)"]
    end

    subgraph "Persistence / Cache Layer"
        JSONCache["File-based JSON Cache (cache/*.json, TTL 5~15m)"]
    end

    subgraph "External API Layer"
        NaverAPI["네이버 스포츠 KBO API"]
        KLPortal["K리그 공식 데이터 포털"]
        MLBApi["MLB Stats Official API"]
        ESPNApi["ESPN Soccer Scoreboard API"]
    end

    Client <-->|HTTP / JSON| FastAPI
    FastAPI --> Jinja2
    FastAPI --> KBO & KL & MLB & SOC
    KBO & KL & MLB & SOC <--> JSONCache
    KBO -.->|API Fallback| NaverAPI
    KL -.->|POST Schedule| KLPortal
    MLB -.->|Hydrate API| MLBApi
    SOC -.->|Calendar API| ESPNApi
```

---

## 3. 프로그램 모듈별 상세 명세서

| 모듈 경로 | 프로그램명 | 주요 함수 / 컴포넌트 | 기능 및 동작 설명 |
| :--- | :--- | :--- | :--- |
| `run.py` | 웹서버 엔트리포인트 | `main` | Uvicorn ASGI 서버 기동 (로컬 127.0.0.1:8000, 핫리로드) |
| `app/main.py` | FastAPI 컨트롤러 | `index_page`, `health_check` | 4대 스포츠 데이터 종합 로드 및 Jinja2 SSR 렌더링 |
| `app/services/kbo_service.py` | KBO 수집 엔진 | `get_kbo_data`, `fetch_kbo_recent_matches` | 실시간 이닝, 승·패전투수, 선발예고, 네이버 gameId 매핑, 10개 구단 순위 수집 |
| `app/services/kleague_service.py` | K리그 수집 엔진 | `get_kleague_data`, `fetch_kleague_recent_matches`, `fetch_naver_kfootball_map` | K리그 공식 상태코드(1S/2S/HT/ET/PK) 판별 및 네이버 kfootball 실시간 API 연동(gameId, 실시간 스코어/분 매핑) |
| `app/services/mlb_service.py` | MLB 수집 엔진 | `get_mlb_data`, `fetch_mlb_recent_matches` | 실시간 이닝, 승·패·세이브 투수, 선발예고, game_id 매핑, 30개 구단 순위 |
| `app/services/overseas_soccer_service.py` | 해외축구 수집 엔진 | `get_overseas_soccer_data`, `fetch_soccer_recent_matches` | 5대리그 순위, UTC->KST 시간 자동 변환, 전·후반 진행시간, 팀명 한글화 |
| `app/templates/index.html` | 메인 뷰 템플릿 | Jinja2 SSR 마크업 & 모달 | 상단 스코어보드 그리드, 실시간 중계확인 버튼 분기, live-relay-modal, 하단 영상 플레이어 |
| `app/static/js/main.js` | 클라이언트 SPA 스크립트 | `switchSport`, `setMatchFilter`, `openLiveRelayModal`, `closeLiveRelayModal` | 원클릭 상태 필터링, 마이팀 로컬스토리지 저장, 네이버스포츠 실시간 문자중계 모달 제어 |
| `app/static/css/style.css` | 스타일시트 | CSS Rules, Tailwind Helpers | 필터 칩 스타일, 라이브 펄스 애니메이션, 다크모드 대응 |

---

## 4. 프로세스 흐름도 (End-to-End Flow)

```mermaid
sequenceDiagram
    autonumber
    actor User as 사용자 (브라우저)
    participant Server as FastAPI (app.main)
    participant Service as 스포츠 서비스 모듈
    participant Cache as 로컬 JSON 캐시
    participant External as 외부 스포츠 API (네이버/K리그/MLB/ESPN)

    User->>Server: 1. GET / 메인 페이지 접속 요청
    Server->>Service: 2. get_*_data() 데이터 조회 요청
    Service->>Cache: 3. 캐시 유효성 검사 (TTL 확인)
    alt 캐시 만료 또는 미존재
        Service->>External: 4-A. 외부 공식 API 호출 (네이버, K리그 포털, MLB Stats, ESPN)
        External-->>Service: 4-B. 최신 데이터 응답 (JSON)
        Service->>Cache: 4-C. 가공 데이터 JSON 파일 저장 (game_id, 실시간 상태 동기화)
    else 캐시 유효
        Cache-->>Service: 4-D. 저장된 캐시 데이터 반환
    end
    Service-->>Server: 5. 4대 스포츠 종합 데이터 전달
    Server->>User: 6. Jinja2 SSR HTML 초기 렌더링 전송
    User->>User: 7. 클라이언트 Hydration & 마이팀(로컬스토리지) 동기화
    User->>User: 8. 상태 필터 칩 클릭 ([🔴 LIVE], [최근 결과] 등)
    alt 실시간 LIVE 경기 카드
        User->>User: 9-A. [⚡ 실시간 중계확인] 클릭 -> 네이버스포츠 실시간 문자중계 모달 렌더링
    else 종료된 경기 카드
        User->>User: 9-B. [하이라이트] 클릭 -> Facade 포스터 -> 비디오 Iframe 동적 재생
    end
```

---

## 5. 외부 API 연동 명세

| 종목 | 제공 기관 | 엔드포인트 URL | 파라미터 규격 | 수집 데이터 |
| :--- | :--- | :--- | :--- | :--- |
| **KBO** | 네이버 스포츠 | `https://api-gw.sports.naver.com/schedule/games` | `fields=basic,baseball&fromDate,toDate&size=100&upperCategoryId=kbaseball` | 실시간 이닝, gameId, statusCode, 승·패전투수, 선발예고 |
| **MLB** | MLB Stats API | `https://statsapi.mlb.com/api/v1/schedule` | `sportId=1&startDate,endDate&hydrate=linescore,decisions,probablePitcher` | 실시간 이닝, game_pk, 승·패·세이브 결정투수, 선발투수 |
| **K리그** | K리그 포털 & 네이버 | `https://www.kleague.com/getScheduleList.do`<br>`https://api-gw.sports.naver.com/schedule/games` | `leagueId=1 or 2&year,month`<br>`upperCategoryId=kfootball` | K리그 공식 상태(1S/2S/HT/ET/PK), 네이버 실시간 스코어, 진행 분, gameId |
| **해외축구** | ESPN Soccer | `https://site.web.api.espn.com/apis/site/v2/sports/soccer/{code}/scoreboard` | `dates=YYYYMMDD` (캘린더 동적 연동) | KST 시간 변환, 실시간 스코어, displayClock(분), 금주/지난주 경기 |

---

## 6. 실행 및 배포 가이드

- **로컬 실행**:
  ```bash
  python run.py
  # 로컬 접속 주소: http://127.0.0.1:8000
  ```
- **클라우드 배포 (Render.com)**:
  - `Procfile`: `web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`
  - `render.yaml`을 통한 자동 빌드 및 배포 지원.
