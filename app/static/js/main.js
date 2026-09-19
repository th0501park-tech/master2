/**
 * SPORTS HUB - 프론트엔드 메인 인터랙션 스크립트
 */

// 전역 상태
let currentSport = "kbo";
let currentViewMode = "standings"; // 'standings' | 'leaders' | 'teamhub'
let currentKLeagueSub = "k1";
let currentOverseasSub = "epl";
let currentMLBSub = "overall";
let searchDebounceTimer = null;

// 스포츠별 메타데이터
const SPORT_META = {
    kbo: { title: "2026 KBO 한국야구", icon: "⚾", badge: "정규시즌" },
    kleague: { title: "2026 K리그 (K LEAGUE)", icon: "⚽", badge: "프로축구" },
    overseas: { title: "해외 축구 (European Football)", icon: "🌍", badge: "5대 빅리그 & 유럽대항전" },
    mlb: { title: "2026 MLB 메이저리그", icon: "🧢", badge: "공식 Stats" }
};

// ========================================================
// 초기화
// ========================================================
document.addEventListener("DOMContentLoaded", () => {
    initTheme();

    // 초기 스포츠 탭 설정
    const initialSport = window.INITIAL_DATA ? window.INITIAL_DATA.activeTab : "kbo";
    switchMainSport(initialSport || "kbo", false);

    // K리그 초기 렌더링
    renderKLeague();

    // 해외축구 초기 렌더링
    renderOverseas();

    // MLB 초기 렌더링
    renderMLB();

    // KBO 구단허브 초기 첫번째 팀 선택
    if (window.INITIAL_DATA?.kbo?.teams?.length > 0) {
        renderTeamHubDetails("kbo", window.INITIAL_DATA.kbo.teams[0].team);
    }

    // 단축키 설정 (Ctrl+K or Cmd+K 로 검색 열기)
    document.addEventListener("keydown", (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === "k") {
            e.preventDefault();
            openSearchModal();
        } else if (e.key === "Escape") {
            closeSearchModal();
        }
    });

    // 검색 인풋 이벤트
    const searchInput = document.getElementById("search-input");
    if (searchInput) {
        searchInput.addEventListener("input", (e) => {
            clearTimeout(searchDebounceTimer);
            const q = e.target.value.trim();
            if (q.length === 0) {
                renderSearchEmpty();
                return;
            }
            searchDebounceTimer = setTimeout(() => {
                performSearch(q);
            }, 250);
        });
    }
});

// ========================================================
// 1. 메인 스포츠 탭 전환
// ========================================================
function switchMainSport(sportKey, updateUrl = true) {
    if (!SPORT_META[sportKey]) sportKey = "kbo";
    currentSport = sportKey;

    // 네비게이션 버튼 활성화 토글 (데스크톱, 모바일 상단, 모바일 하단 바)
    document.querySelectorAll(".main-nav-btn").forEach(btn => btn.classList.remove("active"));
    document.querySelectorAll(".m-main-nav-btn").forEach(btn => btn.classList.remove("active"));
    document.querySelectorAll(".b-main-nav-btn").forEach(btn => btn.classList.remove("active"));

    const dBtn = document.getElementById(`nav-btn-${sportKey}`);
    const mBtn = document.getElementById(`m-nav-btn-${sportKey}`);
    const bBtn = document.getElementById(`b-nav-btn-${sportKey}`);
    if (dBtn) dBtn.classList.add("active");
    if (mBtn) mBtn.classList.add("active");
    if (bBtn) bBtn.classList.add("active");

    // 모바일 상단 탭 스크롤 위치 이동
    if (mBtn && mBtn.scrollIntoView) {
        mBtn.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
    }

    // 헤더 타이틀 및 메타 변경
    const meta = SPORT_META[sportKey];
    document.getElementById("sport-title").innerText = meta.title;
    document.getElementById("sport-icon").innerText = meta.icon;
    document.getElementById("sport-badge").innerText = meta.badge;

    // 업데이트 시각 표시
    updateLastUpdatedTime(sportKey);

    // 모든 스포츠 섹션 숨기고 해당 섹션 표시
    document.querySelectorAll(".sport-section").forEach(sec => sec.classList.add("hidden"));
    const activeSec = document.getElementById(`sport-section-${sportKey}`);
    if (activeSec) activeSec.classList.remove("hidden");

    // 기본 뷰모드 적용
    switchViewMode(currentViewMode);

    if (updateUrl && history.pushState) {
        history.pushState(null, "", `/${sportKey}`);
    }
}

function updateLastUpdatedTime(sportKey) {
    const data = window.INITIAL_DATA ? window.INITIAL_DATA[sportKey] : null;
    const timeEl = document.getElementById("sport-updated-at");
    if (timeEl && data && data.updated_at) {
        timeEl.innerHTML = `<i class="fa-regular fa-clock"></i> <span>최종 갱신: ${data.updated_at}</span>`;
    }
}

// ========================================================
// 2. 뷰 모드 전환 (팀순위 / 개인순위 / 구단별 몰아보기)
// ========================================================
function switchViewMode(mode) {
    currentViewMode = mode;

    // 버튼 액티브 토글
    document.querySelectorAll(".view-mode-btn").forEach(btn => btn.classList.remove("active"));
    const activeBtn = document.getElementById(`view-btn-${mode}`);
    if (activeBtn) activeBtn.classList.add("active");

    // 현재 스포츠 섹션 안의 3개 뷰 토글
    const sec = document.getElementById(`sport-section-${currentSport}`);
    if (!sec) return;

    sec.querySelectorAll(".view-content").forEach(v => v.classList.add("hidden"));
    const targetView = document.getElementById(`${currentSport}-view-${mode}`);
    if (targetView) targetView.classList.remove("hidden");
}

// ========================================================
// 3. K리그 렌더링 및 인터랙션
// ========================================================
function switchKLeagueSub(subKey) {
    currentKLeagueSub = subKey;
    document.querySelectorAll(".kleague-sub-btn").forEach(btn => {
        btn.classList.remove("bg-blue-600", "text-white", "shadow-sm");
        btn.classList.add("text-gray-600", "dark:text-gray-400");
    });
    const activeBtn = document.getElementById(`kleague-sub-btn-${subKey}`);
    if (activeBtn) {
        activeBtn.classList.add("bg-blue-600", "text-white", "shadow-sm");
        activeBtn.classList.remove("text-gray-600", "dark:text-gray-400");
    }
    renderKLeague();
}

function renderKLeague() {
    const klData = window.INITIAL_DATA?.kleague;
    if (!klData) return;

    const subData = klData[currentKLeagueSub];
    if (!subData) return;

    // 1) 테이블 제목
    const tableTitle = document.getElementById("kleague-table-title");
    if (tableTitle) tableTitle.innerText = `🏆 ${subData.name} 팀 순위표`;

    // 2) 팀 순위 테이블
    const tbody = document.getElementById("kleague-table-body");
    if (tbody) {
        tbody.innerHTML = subData.teams.map((t, idx) => {
            const isTop = t.rank <= 3;
            const recentHtml = (t.recent || []).map(r => {
                let badgeClass = "bg-gray-100 text-gray-700 dark:bg-darkbg-700 dark:text-gray-300";
                if (r === "승") badgeClass = "bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-300 font-bold";
                else if (r === "패") badgeClass = "bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300";
                return `<span class="px-1.5 py-0.5 rounded text-[11px] ${badgeClass}">${r}</span>`;
            }).join(" ");

            return `
            <tr class="hover:bg-blue-50/40 dark:hover:bg-darkbg-700/50 transition-colors ${isTop ? 'border-l-4 border-l-emerald-500' : ''}">
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-4 text-center font-bold">
                    <span class="w-5 h-5 sm:w-6 sm:h-6 rounded-full inline-flex items-center justify-center text-[11px] sm:text-xs ${isTop ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 font-black' : 'text-gray-500 dark:text-gray-400'}">
                        ${t.rank}
                    </span>
                </td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-4 font-semibold text-gray-900 dark:text-white">
                    <div class="flex items-center space-x-2 sm:space-x-3">
                        ${t.emblem ? `<img src="${t.emblem}" alt="${t.team}" class="w-5 h-5 sm:w-7 sm:h-7 object-contain drop-shadow-sm" onerror="this.style.display='none'">` : ''}
                        <span class="hidden sm:inline">${t.fullName}</span>
                        <span class="sm:hidden font-bold">${t.team}</span>
                    </div>
                </td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center text-gray-600 dark:text-gray-300">${t.games}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center font-extrabold text-blue-600 dark:text-blue-400 text-xs sm:text-base">${t.points}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center font-bold text-gray-900 dark:text-white">${t.win}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center text-gray-600 dark:text-gray-300">${t.draw}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center text-gray-600 dark:text-gray-300">${t.loss}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center text-gray-600 dark:text-gray-300">${t.goalsFor}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center text-gray-600 dark:text-gray-300">${t.goalsAgainst}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center font-bold ${t.goalDiff > 0 ? 'text-green-600' : (t.goalDiff < 0 ? 'text-red-500' : 'text-gray-500')}">${t.goalDiff > 0 ? '+' + t.goalDiff : t.goalDiff}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center hidden md:table-cell space-x-1">${recentHtml}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-4 text-center">
                    <button type="button" onclick="selectTeamInHub('kleague', '${t.team}')" class="px-2 py-1 text-[11px] sm:text-xs font-semibold rounded-lg bg-gray-100 hover:bg-blue-600 hover:text-white dark:bg-darkbg-700 dark:hover:bg-blue-600 text-gray-700 dark:text-gray-200 transition-colors active:scale-95">
                        선수기록 ➔
                    </button>
                </td>
            </tr>
            `;
        }).join("");
    }

    // 3) 개인 순위 그리드 (득점, 도움 등)
    const leadersGrid = document.getElementById("kleague-leaders-grid");
    if (leadersGrid) {
        leadersGrid.innerHTML = (subData.players || []).map(cat => `
            <div class="bg-white dark:bg-darkbg-800 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm p-4 hover:shadow-md transition-shadow">
                <div class="flex items-center justify-between pb-3 border-b border-gray-100 dark:border-gray-700/60">
                    <div class="flex items-center space-x-2">
                        <i class="fa-solid ${cat.icon} text-emerald-500"></i>
                        <span class="font-bold text-gray-900 dark:text-white text-sm">${cat.category}</span>
                    </div>
                </div>
                ${cat.first_player ? `
                <div class="mt-3 p-3 rounded-xl bg-gradient-to-r from-emerald-500/10 to-teal-500/10 border border-emerald-500/20 flex items-center space-x-3">
                    <div class="w-12 h-12 rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 flex items-center justify-center font-black text-base shadow-sm">
                        1위
                    </div>
                    <div class="flex-grow">
                        <div class="flex items-center space-x-2">
                            <span class="font-bold text-gray-900 dark:text-white text-base">${cat.first_player.name}</span>
                            <span class="text-xs text-gray-500 dark:text-gray-400">(${cat.first_player.team})</span>
                        </div>
                        <div class="text-base font-extrabold text-emerald-600 dark:text-emerald-400 mt-0.5">${cat.first_player.value}</div>
                    </div>
                </div>
                ` : '<div class="py-4 text-xs text-gray-400 text-center">기록 준비중</div>'}
                
                <div class="mt-3 space-y-1.5 text-xs">
                    ${(cat.ranks || []).slice(1, 6).map(p => `
                    <div class="flex items-center justify-between py-1 px-2 rounded-lg hover:bg-gray-50 dark:hover:bg-darkbg-700/50">
                        <div class="flex items-center space-x-2">
                            <span class="w-4 text-center font-bold text-gray-400">${p.rank}</span>
                            <span class="font-semibold text-gray-800 dark:text-gray-200">${p.name}</span>
                            <span class="text-gray-400">(${p.team})</span>
                        </div>
                        <span class="font-bold text-gray-700 dark:text-gray-300">${p.value}</span>
                    </div>
                    `).join("")}
                </div>
            </div>
        `).join("");
    }

    // 4) 구단 선택자 렌더링
    const selectors = document.getElementById("kleague-hub-selectors");
    if (selectors) {
        selectors.innerHTML = subData.teams.map(t => `
            <button type="button" onclick="renderTeamHubDetails('kleague', '${t.team}')" id="kleague-hub-btn-${t.team}" 
                    class="team-hub-selector p-2 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-blue-500 flex items-center space-x-2 transition-all">
                ${t.emblem ? `<img src="${t.emblem}" alt="${t.team}" class="w-6 h-6 object-contain" onerror="this.style.display='none'">` : ''}
                <span class="text-xs font-bold text-gray-800 dark:text-gray-200">${t.team}</span>
            </button>
        `).join("");

        if (subData.teams.length > 0) {
            renderTeamHubDetails("kleague", subData.teams[0].team);
        }
    }
}

// ========================================================
// 4. 해외축구 렌더링 및 인터랙션
// ========================================================
function switchOverseasSub(leagueKey) {
    currentOverseasSub = leagueKey;
    document.querySelectorAll(".overseas-sub-btn").forEach(btn => {
        btn.classList.remove("bg-blue-600", "text-white", "shadow-sm");
        btn.classList.add("text-gray-600", "dark:text-gray-400");
    });
    const activeBtn = document.getElementById(`overseas-sub-btn-${leagueKey}`);
    if (activeBtn) {
        activeBtn.classList.add("bg-blue-600", "text-white", "shadow-sm");
        activeBtn.classList.remove("text-gray-600", "dark:text-gray-400");
    }
    renderOverseas();
}

function renderOverseas() {
    const socData = window.INITIAL_DATA?.overseas;
    if (!socData) return;

    const league = socData.leagues ? socData.leagues[currentOverseasSub] : null;
    if (!league) return;

    // 1) 테이블 제목
    const tableTitle = document.getElementById("overseas-table-title");
    if (tableTitle) tableTitle.innerText = `🏆 ${league.name} 순위표`;

    // 2) 팀 순위 테이블
    const tbody = document.getElementById("overseas-table-body");
    if (tbody) {
        tbody.innerHTML = (league.teams || []).map(t => {
            const isUcl = t.rank <= 4;
            return `
            <tr class="hover:bg-blue-50/40 dark:hover:bg-darkbg-700/50 transition-colors ${isUcl ? 'border-l-4 border-l-blue-600' : ''}">
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-4 text-center font-bold">
                    <span class="w-5 h-5 sm:w-6 sm:h-6 rounded-full inline-flex items-center justify-center text-[11px] sm:text-xs ${isUcl ? 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300 font-black' : 'text-gray-500 dark:text-gray-400'}">
                        ${t.rank}
                    </span>
                </td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-4 font-semibold text-gray-900 dark:text-white">
                    <div class="flex items-center space-x-2 sm:space-x-3">
                        ${t.emblem ? `<img src="${t.emblem}" alt="${t.team}" class="w-5 h-5 sm:w-7 sm:h-7 object-contain drop-shadow-sm" onerror="this.style.display='none'">` : ''}
                        <span class="font-bold">${t.team}</span>
                        ${t.teamEng && t.teamEng !== t.team ? `<span class="hidden sm:inline text-xs text-gray-400 font-normal">(${t.teamEng})</span>` : ''}
                    </div>
                </td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center text-gray-600 dark:text-gray-300">${t.games}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center font-extrabold text-blue-600 dark:text-blue-400 text-xs sm:text-base">${t.points}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center font-bold text-gray-900 dark:text-white">${t.win}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center text-gray-600 dark:text-gray-300">${t.draw}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center text-gray-600 dark:text-gray-300">${t.loss}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center text-gray-600 dark:text-gray-300">${t.goalsFor}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center text-gray-600 dark:text-gray-300">${t.goalsAgainst}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center font-bold ${t.goalDiff > 0 ? 'text-green-600' : (t.goalDiff < 0 ? 'text-red-500' : 'text-gray-500')}">${t.goalDiff > 0 ? '+' + t.goalDiff : t.goalDiff}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-4 text-center">
                    <button type="button" onclick="selectTeamInHub('overseas', '${t.team}')" class="px-2 py-1 text-[11px] sm:text-xs font-semibold rounded-lg bg-gray-100 hover:bg-blue-600 hover:text-white dark:bg-darkbg-700 dark:hover:bg-blue-600 text-gray-700 dark:text-gray-200 transition-colors active:scale-95">
                        선수기록 ➔
                    </button>
                </td>
            </tr>
            `;
        }).join("");
    }

    // 3) 개인 순위 (득점/도움)
    const leadersGrid = document.getElementById("overseas-leaders-grid");
    if (leadersGrid) {
        leadersGrid.innerHTML = (league.players || []).map(cat => `
            <div class="bg-white dark:bg-darkbg-800 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm p-5 hover:shadow-md transition-shadow">
                <div class="flex items-center justify-between pb-3 border-b border-gray-100 dark:border-gray-700/60">
                    <div class="flex items-center space-x-2">
                        <i class="fa-solid ${cat.icon} text-indigo-500 text-base"></i>
                        <span class="font-bold text-gray-900 dark:text-white text-base">${cat.category}</span>
                    </div>
                </div>
                ${cat.first_player ? `
                <div class="mt-4 p-3.5 rounded-xl bg-gradient-to-r from-indigo-500/10 to-purple-500/10 border border-indigo-500/20 flex items-center space-x-4">
                    ${cat.first_player.headshot ? `
                    <img src="${cat.first_player.headshot}" alt="${cat.first_player.name}" class="w-14 h-14 rounded-full object-cover border-2 border-indigo-400 bg-white shadow-sm" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>👤</text></svg>'">
                    ` : '<div class="w-14 h-14 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-lg">1위</div>'}
                    <div class="flex-grow">
                        <div class="flex items-center space-x-2">
                            <span class="text-xs font-black px-1.5 py-0.5 rounded bg-indigo-500 text-white">1위</span>
                            <span class="font-bold text-gray-900 dark:text-white text-base">${cat.first_player.name}</span>
                            <span class="text-xs text-gray-500 dark:text-gray-400">(${cat.first_player.team})</span>
                        </div>
                        <div class="text-lg font-extrabold text-indigo-600 dark:text-indigo-400 mt-1">${cat.first_player.value}</div>
                    </div>
                </div>
                ` : '<div class="py-6 text-xs text-gray-400 text-center">기록 준비중</div>'}
                
                <div class="mt-4 space-y-2 text-xs">
                    ${(cat.ranks || []).slice(1, 10).map(p => `
                    <div class="flex items-center justify-between py-1.5 px-2.5 rounded-lg hover:bg-gray-50 dark:hover:bg-darkbg-700/50">
                        <div class="flex items-center space-x-3">
                            <span class="w-4 text-center font-bold text-gray-400">${p.rank}</span>
                            <span class="font-semibold text-gray-800 dark:text-gray-200">${p.name}</span>
                            <span class="text-gray-400">(${p.team})</span>
                        </div>
                        <span class="font-bold text-gray-700 dark:text-gray-300">${p.value}</span>
                    </div>
                    `).join("")}
                </div>
            </div>
        `).join("");
    }

    // 4) 구단허브 선택자
    const selectors = document.getElementById("overseas-hub-selectors");
    if (selectors) {
        selectors.innerHTML = (league.teams || []).map(t => `
            <button type="button" onclick="renderTeamHubDetails('overseas', '${t.team}')" id="overseas-hub-btn-${t.team}" 
                    class="team-hub-selector p-2 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-blue-500 flex items-center space-x-2 transition-all">
                ${t.emblem ? `<img src="${t.emblem}" alt="${t.team}" class="w-6 h-6 object-contain" onerror="this.style.display='none'">` : ''}
                <span class="text-xs font-bold text-gray-800 dark:text-gray-200">${t.team}</span>
            </button>
        `).join("");

        if (league.teams?.length > 0) {
            renderTeamHubDetails("overseas", league.teams[0].team);
        }
    }
}

// ========================================================
// 5. MLB 메이저리그 렌더링 및 인터랙션
// ========================================================
function switchMLBSub(subKey) {
    currentMLBSub = subKey;
    document.querySelectorAll(".mlb-sub-btn").forEach(btn => {
        btn.classList.remove("bg-blue-600", "text-white", "shadow-sm");
        btn.classList.add("text-gray-600", "dark:text-gray-400");
    });
    const activeBtn = document.getElementById(`mlb-sub-btn-${subKey}`);
    if (activeBtn) {
        activeBtn.classList.add("bg-blue-600", "text-white", "shadow-sm");
        activeBtn.classList.remove("text-gray-600", "dark:text-gray-400");
    }

    const overallContainer = document.getElementById("mlb-overall-table-container");
    const divisionsContainer = document.getElementById("mlb-divisions-container");
    if (subKey === "overall") {
        overallContainer?.classList.remove("hidden");
        divisionsContainer?.classList.add("hidden");
    } else {
        overallContainer?.classList.add("hidden");
        divisionsContainer?.classList.remove("hidden");
    }
}

function renderMLB() {
    const mlbData = window.INITIAL_DATA?.mlb;
    if (!mlbData) return;

    // 1) 30개 구단 전체 순위표
    const tbody = document.getElementById("mlb-overall-tbody");
    if (tbody) {
        tbody.innerHTML = (mlbData.all_teams || []).map((t, idx) => `
            <tr class="hover:bg-blue-50/40 dark:hover:bg-darkbg-700/50 transition-colors ${idx < 12 ? 'border-l-4 border-l-blue-500' : ''}">
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-4 text-center font-bold">
                    <span class="w-5 h-5 sm:w-6 sm:h-6 rounded-full inline-flex items-center justify-center text-[11px] sm:text-xs ${idx < 12 ? 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300 font-bold' : 'text-gray-500'}">
                        ${t.overallRank || idx + 1}
                    </span>
                </td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-4 font-semibold text-gray-900 dark:text-white">
                    <div class="flex items-center space-x-2 sm:space-x-3">
                        ${t.emblem ? `<img src="${t.emblem}" alt="${t.team}" class="w-5 h-5 sm:w-7 sm:h-7 object-contain" onerror="this.style.display='none'">` : ''}
                        <span class="font-bold">${t.team}</span>
                        <span class="hidden sm:inline text-xs text-gray-400 font-normal">(${t.teamEng})</span>
                    </div>
                </td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center text-xs text-gray-500 dark:text-gray-400">${t.division}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center text-gray-600 dark:text-gray-300">${t.games}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center font-bold text-gray-900 dark:text-white">${t.win}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center text-gray-600 dark:text-gray-300">${t.loss}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center font-extrabold text-blue-600 dark:text-blue-400 text-xs sm:text-base">${t.rate}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center text-gray-600 dark:text-gray-300">${t.game_diff}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center text-xs hidden md:table-cell">${t.streak}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center text-xs text-gray-500 dark:text-gray-400 hidden md:table-cell">${t.recent10}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-4 text-center">
                    <button type="button" onclick="selectTeamInHub('mlb', '${t.team}')" class="px-2 py-1 text-[11px] sm:text-xs font-semibold rounded-lg bg-gray-100 hover:bg-blue-600 hover:text-white dark:bg-darkbg-700 dark:hover:bg-blue-600 text-gray-700 dark:text-gray-200 transition-colors active:scale-95">
                        선수기록 ➔
                    </button>
                </td>
            </tr>
        `).join("");
    }

    // 2) 6개 지구별 순위 카드
    const divContainer = document.getElementById("mlb-divisions-container");
    if (divContainer) {
        divContainer.innerHTML = (mlbData.divisions || []).map(d => `
            <div class="bg-white dark:bg-darkbg-800 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm overflow-hidden">
                <div class="px-4 py-3 bg-gray-50 dark:bg-darkbg-900/60 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between">
                    <span class="font-bold text-gray-900 dark:text-white text-sm">${d.divisionName}</span>
                    <span class="text-xs text-blue-600 dark:text-blue-400 font-semibold">${d.league}</span>
                </div>
                <div class="p-2">
                    <table class="w-full text-xs text-left">
                        <thead>
                            <tr class="text-gray-400 border-b border-gray-100 dark:border-gray-800">
                                <th class="p-2 text-center w-8">순위</th>
                                <th class="p-2">구단</th>
                                <th class="p-2 text-center">승</th>
                                <th class="p-2 text-center">패</th>
                                <th class="p-2 text-center">승률</th>
                                <th class="p-2 text-center">게임차</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-50 dark:divide-gray-800/50">
                            ${(d.teams || []).map(t => `
                            <tr class="hover:bg-gray-50 dark:hover:bg-darkbg-700/50">
                                <td class="p-2 text-center font-bold text-gray-500">${t.rank}</td>
                                <td class="p-2 font-semibold flex items-center space-x-2">
                                    <img src="${t.emblem}" alt="${t.team}" class="w-5 h-5 object-contain" onerror="this.style.display='none'">
                                    <span>${t.team}</span>
                                </td>
                                <td class="p-2 text-center font-bold">${t.win}</td>
                                <td class="p-2 text-center text-gray-500">${t.loss}</td>
                                <td class="p-2 text-center font-bold text-blue-600 dark:text-blue-400">${t.rate}</td>
                                <td class="p-2 text-center text-gray-500">${t.game_diff}</td>
                            </tr>
                            `).join("")}
                        </tbody>
                    </table>
                </div>
            </div>
        `).join("");
    }

    // 3) 타자 리더보드
    const hittersGrid = document.getElementById("mlb-hitters-grid");
    if (hittersGrid) {
        hittersGrid.innerHTML = (mlbData.hitters || []).map(cat => renderLeaderCard(cat, "amber")).join("");
    }

    // 4) 투수 리더보드
    const pitchersGrid = document.getElementById("mlb-pitchers-grid");
    if (pitchersGrid) {
        pitchersGrid.innerHTML = (mlbData.pitchers || []).map(cat => renderLeaderCard(cat, "blue")).join("");
    }

    // 5) 구단허브 선택자
    const hubSelectors = document.getElementById("mlb-hub-selectors");
    if (hubSelectors) {
        hubSelectors.innerHTML = (mlbData.all_teams || []).map(t => `
            <button type="button" onclick="renderTeamHubDetails('mlb', '${t.team}')" id="mlb-hub-btn-${t.team}" 
                    class="team-hub-selector p-2 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-blue-500 flex flex-col items-center justify-center transition-all">
                <img src="${t.emblem}" alt="${t.team}" class="w-7 h-7 object-contain mb-1" onerror="this.style.display='none'">
                <span class="text-[11px] font-bold text-gray-800 dark:text-gray-200 text-center truncate w-full">${t.team}</span>
            </button>
        `).join("");

        if (mlbData.all_teams?.length > 0) {
            renderTeamHubDetails("mlb", mlbData.all_teams[0].team);
        }
    }
}

function renderLeaderCard(cat, colorTheme) {
    const isAmber = colorTheme === "amber";
    return `
    <div class="bg-white dark:bg-darkbg-800 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm p-4 hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between pb-3 border-b border-gray-100 dark:border-gray-700/60">
            <div class="flex items-center space-x-2">
                <i class="fa-solid ${cat.icon} ${isAmber ? 'text-amber-500' : 'text-blue-500'}"></i>
                <span class="font-bold text-gray-900 dark:text-white text-sm">${cat.category}</span>
            </div>
        </div>
        ${cat.first_player ? `
        <div class="mt-3 p-3 rounded-xl bg-gradient-to-r ${isAmber ? 'from-amber-500/10 to-orange-500/10 border-amber-500/20' : 'from-blue-500/10 to-indigo-500/10 border-blue-500/20'} border flex items-center space-x-3">
            ${cat.first_player.photo ? `
            <img src="${cat.first_player.photo}" alt="${cat.first_player.name}" class="w-14 h-14 object-cover rounded-full border-2 ${isAmber ? 'border-amber-400' : 'border-blue-400'} bg-white shadow-sm" onerror="this.style.display='none'">
            ` : '<div class="w-14 h-14 rounded-full bg-gray-100 text-gray-700 flex items-center justify-center font-bold">1위</div>'}
            <div class="flex-grow">
                <div class="flex items-center space-x-2">
                    <span class="text-xs font-black px-1.5 py-0.5 rounded ${isAmber ? 'bg-amber-400 text-amber-950' : 'bg-blue-500 text-white'}">1위</span>
                    <span class="font-bold text-gray-900 dark:text-white text-base">${cat.first_player.name}</span>
                </div>
                <div class="text-xs text-gray-500 dark:text-gray-400">${cat.first_player.team}</div>
                <div class="text-lg font-extrabold ${isAmber ? 'text-amber-600 dark:text-amber-400' : 'text-blue-600 dark:text-blue-400'} mt-0.5">${cat.first_player.value}</div>
            </div>
        </div>
        ` : '<div class="py-4 text-xs text-gray-400 text-center">기록 없음</div>'}
        
        <div class="mt-3 space-y-1.5 text-xs">
            ${(cat.ranks || []).slice(1, 5).map(p => `
            <div class="flex items-center justify-between py-1 px-2 rounded-lg hover:bg-gray-50 dark:hover:bg-darkbg-700/50">
                <div class="flex items-center space-x-2">
                    <span class="w-4 text-center font-bold text-gray-400">${p.rank}</span>
                    <span class="font-semibold text-gray-800 dark:text-gray-200">${p.name}</span>
                    <span class="text-gray-400 text-[11px]">(${p.team})</span>
                </div>
                <span class="font-bold text-gray-700 dark:text-gray-300">${p.value}</span>
            </div>
            `).join("")}
        </div>
    </div>
    `;
}

// ========================================================
// 6. 구단별 몰아보기 상세 렌더러
// ========================================================
function selectTeamInHub(sportKey, teamKey) {
    switchMainSport(sportKey);
    switchViewMode("teamhub");
    setTimeout(() => {
        renderTeamHubDetails(sportKey, teamKey);
    }, 50);
}

function renderTeamHubDetails(sportKey, teamKey) {
    // 버튼 활성화 토글
    document.querySelectorAll(".team-hub-selector").forEach(b => b.classList.remove("active"));
    const btn = document.getElementById(`${sportKey}-hub-btn-${teamKey}`);
    if (btn) btn.classList.add("active");

    const cardContainer = document.getElementById(`${sportKey}-hub-detail-card`);
    if (!cardContainer) return;

    if (sportKey === "kbo") {
        const hubData = window.INITIAL_DATA?.kbo?.team_hub?.[teamKey];
        if (!hubData) return;
        const t = hubData.team;
        cardContainer.innerHTML = `
            <div class="bg-white dark:bg-darkbg-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-800 shadow-sm">
                <div class="flex flex-col sm:flex-row items-center justify-between gap-4 pb-6 border-b border-gray-100 dark:border-gray-700">
                    <div class="flex items-center space-x-4">
                        <img src="${t.emblem}" alt="${t.team}" class="w-16 h-16 object-contain drop-shadow-md">
                        <div>
                            <div class="flex items-center space-x-2">
                                <h3 class="text-2xl font-black text-gray-900 dark:text-white">${t.fullName}</h3>
                                <span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-100 text-blue-700 dark:bg-blue-900/60 dark:text-blue-300">${t.rank}위</span>
                            </div>
                            <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                                ${t.games}전 ${t.win}승 ${t.loss}패 ${t.draw}무 (승률 ${t.rate}) • 게임차 ${t.game_diff}
                            </p>
                        </div>
                    </div>
                    <div class="flex items-center space-x-6 text-center text-xs">
                        <div>
                            <span class="block text-gray-400 mb-1">최근 10경기</span>
                            <span class="font-bold text-sm text-gray-800 dark:text-gray-200">${t.recent10}</span>
                        </div>
                        <div>
                            <span class="block text-gray-400 mb-1">연속 기록</span>
                            <span class="font-bold text-sm text-gray-800 dark:text-gray-200">${t.streak}</span>
                        </div>
                        <div>
                            <span class="block text-gray-400 mb-1">홈 / 원정</span>
                            <span class="font-bold text-sm text-gray-800 dark:text-gray-200">${t.home} / ${t.away}</span>
                        </div>
                    </div>
                </div>

                <!-- 소속 순위권 선수들 -->
                <div class="mt-6">
                    <h4 class="text-base font-bold text-gray-900 dark:text-white mb-4 flex items-center space-x-2">
                        <span>🎖️ ${t.team} 소속 TOP 5 랭커 선수들</span>
                    </h4>
                    
                    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                        ${hubData.hitter_records.map(r => `
                        <div class="p-3.5 rounded-xl border border-amber-100 dark:border-amber-900/30 bg-amber-50/50 dark:bg-amber-950/20 flex items-center justify-between">
                            <div>
                                <span class="text-[11px] font-semibold text-amber-600 dark:text-amber-400 block">${r.category}</span>
                                <div class="flex items-center space-x-1.5 mt-0.5">
                                    <span class="font-black text-xs px-1.5 py-0.5 rounded bg-amber-200 text-amber-900">${r.rank}위</span>
                                    <span class="font-bold text-gray-900 dark:text-white text-sm">${r.name}</span>
                                </div>
                            </div>
                            <span class="font-extrabold text-base text-amber-700 dark:text-amber-300">${r.value}</span>
                        </div>
                        `).join("")}

                        ${hubData.pitcher_records.map(r => `
                        <div class="p-3.5 rounded-xl border border-blue-100 dark:border-blue-900/30 bg-blue-50/50 dark:bg-blue-950/20 flex items-center justify-between">
                            <div>
                                <span class="text-[11px] font-semibold text-blue-600 dark:text-blue-400 block">${r.category}</span>
                                <div class="flex items-center space-x-1.5 mt-0.5">
                                    <span class="font-black text-xs px-1.5 py-0.5 rounded bg-blue-200 text-blue-900">${r.rank}위</span>
                                    <span class="font-bold text-gray-900 dark:text-white text-sm">${r.name}</span>
                                </div>
                            </div>
                            <span class="font-extrabold text-base text-blue-700 dark:text-blue-300">${r.value}</span>
                        </div>
                        `).join("")}
                    </div>
                    ${hubData.hitter_records.length === 0 && hubData.pitcher_records.length === 0 ? '<p class="text-xs text-gray-400 py-4 text-center">현재 TOP 5 리더보드에 랭크된 선수가 없습니다.</p>' : ''}
                </div>
            </div>
        `;
    } else if (sportKey === "kleague") {
        const subData = window.INITIAL_DATA?.kleague?.[currentKLeagueSub];
        const hubData = subData?.team_hub?.[teamKey];
        if (!hubData) return;
        const t = hubData.team;
        cardContainer.innerHTML = `
            <div class="bg-white dark:bg-darkbg-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-800 shadow-sm">
                <div class="flex flex-col sm:flex-row items-center justify-between gap-4 pb-6 border-b border-gray-100 dark:border-gray-700">
                    <div class="flex items-center space-x-4">
                        ${t.emblem ? `<img src="${t.emblem}" alt="${t.team}" class="w-16 h-16 object-contain drop-shadow-md">` : ''}
                        <div>
                            <div class="flex items-center space-x-2">
                                <h3 class="text-2xl font-black text-gray-900 dark:text-white">${t.fullName}</h3>
                                <span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">${t.rank}위</span>
                            </div>
                            <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                                ${t.games}경기 ${t.win}승 ${t.draw}무 ${t.loss}패 • 승점 ${t.points} • 득실차 ${t.goalDiff}
                            </p>
                        </div>
                    </div>
                </div>

                <div class="mt-6">
                    <h4 class="text-base font-bold text-gray-900 dark:text-white mb-4">🎖️ ${t.team} 소속 순위권 선수들</h4>
                    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                        ${hubData.players.map(p => `
                        <div class="p-3.5 rounded-xl border border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-darkbg-900/50 flex items-center justify-between">
                            <div>
                                <span class="text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 block">${p.category}</span>
                                <div class="flex items-center space-x-1.5 mt-0.5">
                                    <span class="font-black text-xs px-1.5 py-0.5 rounded bg-emerald-200 text-emerald-900">${p.rank}위</span>
                                    <span class="font-bold text-gray-900 dark:text-white text-sm">${p.name}</span>
                                </div>
                            </div>
                            <span class="font-extrabold text-sm text-gray-800 dark:text-gray-200">${p.value}</span>
                        </div>
                        `).join("")}
                    </div>
                    ${hubData.players.length === 0 ? '<p class="text-xs text-gray-400 py-4 text-center">순위권 등록 선수가 없습니다.</p>' : ''}
                </div>
            </div>
        `;
    } else if (sportKey === "overseas") {
        const league = window.INITIAL_DATA?.overseas?.leagues?.[currentOverseasSub];
        const hubData = league?.team_hub?.[teamKey];
        if (!hubData) return;
        const t = hubData.team;
        cardContainer.innerHTML = `
            <div class="bg-white dark:bg-darkbg-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-800 shadow-sm">
                <div class="flex flex-col sm:flex-row items-center justify-between gap-4 pb-6 border-b border-gray-100 dark:border-gray-700">
                    <div class="flex items-center space-x-4">
                        ${t.emblem ? `<img src="${t.emblem}" alt="${t.team}" class="w-16 h-16 object-contain drop-shadow-md">` : ''}
                        <div>
                            <div class="flex items-center space-x-2">
                                <h3 class="text-2xl font-black text-gray-900 dark:text-white">${t.team}</h3>
                                <span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-100 text-blue-700 dark:bg-blue-900/60 dark:text-blue-300">${t.rank}위</span>
                            </div>
                            <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                                ${t.games}경기 ${t.win}승 ${t.draw}무 ${t.loss}패 • 승점 ${t.points}점
                            </p>
                        </div>
                    </div>
                </div>

                <div class="mt-6">
                    <h4 class="text-base font-bold text-gray-900 dark:text-white mb-4">🎖️ ${t.team} 소속 득점/도움 순위권 선수</h4>
                    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                        ${hubData.players.map(p => `
                        <div class="p-3.5 rounded-xl border border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-darkbg-900/50 flex items-center justify-between">
                            <div>
                                <span class="text-[11px] font-semibold text-indigo-600 dark:text-indigo-400 block">${p.category}</span>
                                <div class="flex items-center space-x-1.5 mt-0.5">
                                    <span class="font-black text-xs px-1.5 py-0.5 rounded bg-indigo-200 text-indigo-900">${p.rank}위</span>
                                    <span class="font-bold text-gray-900 dark:text-white text-sm">${p.name}</span>
                                </div>
                            </div>
                            <span class="font-extrabold text-sm text-gray-800 dark:text-gray-200">${p.value}</span>
                        </div>
                        `).join("")}
                    </div>
                    ${hubData.players.length === 0 ? '<p class="text-xs text-gray-400 py-4 text-center">등록된 상위 선수가 없습니다.</p>' : ''}
                </div>
            </div>
        `;
    } else if (sportKey === "mlb") {
        const hubData = window.INITIAL_DATA?.mlb?.team_hub?.[teamKey];
        if (!hubData) return;
        const t = hubData.team;
        cardContainer.innerHTML = `
            <div class="bg-white dark:bg-darkbg-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-800 shadow-sm">
                <div class="flex flex-col sm:flex-row items-center justify-between gap-4 pb-6 border-b border-gray-100 dark:border-gray-700">
                    <div class="flex items-center space-x-4">
                        <img src="${t.emblem}" alt="${t.team}" class="w-16 h-16 object-contain drop-shadow-md">
                        <div>
                            <div class="flex items-center space-x-2">
                                <h3 class="text-2xl font-black text-gray-900 dark:text-white">${t.team}</h3>
                                <span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-100 text-blue-700 dark:bg-blue-900/60 dark:text-blue-300">${t.division} ${t.rank}위</span>
                            </div>
                            <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                                ${t.win}승 ${t.loss}패 (승률 ${t.rate}) • 게임차 ${t.game_diff} • 연속 ${t.streak}
                            </p>
                        </div>
                    </div>
                </div>

                <div class="mt-6">
                    <h4 class="text-base font-bold text-gray-900 dark:text-white mb-4">🎖️ ${t.team} 소속 리더보드 선수</h4>
                    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                        ${hubData.hitters.map(h => `
                        <div class="p-3.5 rounded-xl border border-amber-100 dark:border-amber-900/30 bg-amber-50/50 dark:bg-amber-950/20 flex items-center justify-between">
                            <div>
                                <span class="text-[11px] font-semibold text-amber-600 dark:text-amber-400 block">${h.category}</span>
                                <div class="flex items-center space-x-1.5 mt-0.5">
                                    <span class="font-black text-xs px-1.5 py-0.5 rounded bg-amber-200 text-amber-900">${h.rank}위</span>
                                    <span class="font-bold text-gray-900 dark:text-white text-sm">${h.name}</span>
                                </div>
                            </div>
                            <span class="font-extrabold text-sm text-amber-700 dark:text-amber-300">${h.value}</span>
                        </div>
                        `).join("")}

                        ${hubData.pitchers.map(p => `
                        <div class="p-3.5 rounded-xl border border-blue-100 dark:border-blue-900/30 bg-blue-50/50 dark:bg-blue-950/20 flex items-center justify-between">
                            <div>
                                <span class="text-[11px] font-semibold text-blue-600 dark:text-blue-400 block">${p.category}</span>
                                <div class="flex items-center space-x-1.5 mt-0.5">
                                    <span class="font-black text-xs px-1.5 py-0.5 rounded bg-blue-200 text-blue-900">${p.rank}위</span>
                                    <span class="font-bold text-gray-900 dark:text-white text-sm">${p.name}</span>
                                </div>
                            </div>
                            <span class="font-extrabold text-sm text-blue-700 dark:text-blue-300">${p.value}</span>
                        </div>
                        `).join("")}
                    </div>
                    ${hubData.hitters.length === 0 && hubData.pitchers.length === 0 ? '<p class="text-xs text-gray-400 py-4 text-center">등록된 상위 선수가 없습니다.</p>' : ''}
                </div>
            </div>
        `;
    }
}

// ========================================================
// 7. 실시간 새로고침 (AJAX)
// ========================================================
async function refreshCurrentSport() {
    const btn = document.getElementById("refresh-btn");
    const icon = document.getElementById("refresh-icon");
    if (!btn || !icon) return;

    btn.disabled = true;
    icon.classList.add("spin-animate");

    try {
        const resp = await fetch(`/api/refresh?sport=${currentSport}`, { method: "POST" });
        const result = await resp.json();

        if (result.success) {
            // 전역 캐시 업데이트
            window.INITIAL_DATA[currentSport] = result.data;
            updateLastUpdatedTime(currentSport);

            // 해당 종목 재렌더링
            if (currentSport === "kbo") {
                // KBO 테이블 및 리더스 갱신은 페이지 reload 또는 DOM 갱신
                window.location.reload();
            } else if (currentSport === "kleague") {
                renderKLeague();
            } else if (currentSport === "overseas") {
                renderOverseas();
            } else if (currentSport === "mlb") {
                renderMLB();
            }
            showToast(`${SPORT_META[currentSport].title} 최신 데이터가 갱신되었습니다!`);
        }
    } catch (e) {
        console.error("새로고침 실패:", e);
        showToast("데이터 갱신 중 문제가 발생했습니다.", true);
    } finally {
        btn.disabled = false;
        icon.classList.remove("spin-animate");
    }
}

// ========================================================
// 8. 통합 검색 모달 및 로직
// ========================================================
function openSearchModal() {
    const modal = document.getElementById("search-modal");
    const input = document.getElementById("search-input");
    if (modal) modal.classList.remove("hidden");
    if (input) {
        input.value = "";
        input.focus();
    }
    renderSearchEmpty();
}

function closeSearchModal() {
    const modal = document.getElementById("search-modal");
    if (modal) modal.classList.add("hidden");
}

function renderSearchEmpty() {
    const results = document.getElementById("search-results");
    if (results) {
        results.innerHTML = `
            <div class="text-center py-8 text-gray-400 dark:text-gray-500 text-sm">
                <i class="fa-regular fa-compass text-3xl mb-2"></i>
                <p>4대 스포츠(KBO, K리그, 해외축구, MLB)의 팀과 선수를 실시간으로 검색합니다.</p>
            </div>
        `;
    }
}

async function performSearch(query) {
    const resultsContainer = document.getElementById("search-results");
    if (!resultsContainer) return;

    resultsContainer.innerHTML = `
        <div class="text-center py-8 text-gray-400">
            <i class="fa-solid fa-spinner spin-animate text-2xl mb-2"></i>
            <p class="text-xs">검색 중입니다...</p>
        </div>
    `;

    try {
        const resp = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        const data = await resp.json();
        const teams = data.results.teams || [];
        const players = data.results.players || [];

        if (teams.length === 0 && players.length === 0) {
            resultsContainer.innerHTML = `
                <div class="text-center py-8 text-gray-400 text-sm">
                    <p>‘${query}’ 에 대한 검색 결과가 없습니다.</p>
                </div>
            `;
            return;
        }

        let html = "";

        // 구단 결과
        if (teams.length > 0) {
            html += `
                <div>
                    <h5 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">구단 (${teams.length})</h5>
                    <div class="space-y-1.5">
                        ${teams.map(t => `
                        <div onclick="selectSearchResult('${t.sportKey}', '${t.shortName || t.name}')" 
                             class="p-2.5 rounded-xl hover:bg-gray-100 dark:hover:bg-darkbg-700 cursor-pointer flex items-center justify-between transition-colors">
                            <div class="flex items-center space-x-3">
                                ${t.emblem ? `<img src="${t.emblem}" class="w-6 h-6 object-contain">` : '<i class="fa-solid fa-shield text-gray-400"></i>'}
                                <div>
                                    <span class="font-bold text-sm text-gray-900 dark:text-white">${t.name}</span>
                                    <span class="text-xs text-gray-400 ml-1.5">[${t.sport}]</span>
                                </div>
                            </div>
                            <span class="text-xs font-bold text-blue-600 dark:text-blue-400">${t.rank} (${t.info})</span>
                        </div>
                        `).join("")}
                    </div>
                </div>
            `;
        }

        // 선수 결과
        if (players.length > 0) {
            html += `
                <div class="pt-2">
                    <h5 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">선수 (${players.length})</h5>
                    <div class="space-y-1.5">
                        ${players.map(p => `
                        <div onclick="selectSearchResult('${p.sportKey}', '${p.team}')" 
                             class="p-2.5 rounded-xl hover:bg-gray-100 dark:hover:bg-darkbg-700 cursor-pointer flex items-center justify-between transition-colors">
                            <div class="flex items-center space-x-3">
                                <span class="w-6 h-6 rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 text-xs flex items-center justify-center font-bold">
                                    ${p.rank.replace('위', '')}
                                </span>
                                <div>
                                    <span class="font-bold text-sm text-gray-900 dark:text-white">${p.name}</span>
                                    <span class="text-xs text-gray-400 ml-1">(${p.team} • ${p.sport})</span>
                                </div>
                            </div>
                            <span class="text-xs font-bold text-gray-700 dark:text-gray-300">${p.category}: ${p.value}</span>
                        </div>
                        `).join("")}
                    </div>
                </div>
            `;
        }

        resultsContainer.innerHTML = html;
    } catch (e) {
        console.error("검색 요청 오류:", e);
    }
}

function selectSearchResult(sportKey, teamName) {
    closeSearchModal();
    selectTeamInHub(sportKey, teamName);
}

// ========================================================
// 9. 테마 토글 및 토스트 알림
// ========================================================
function initTheme() {
    const isDark = localStorage.getItem("theme") !== "light";
    if (isDark) {
        document.documentElement.classList.add("dark");
    } else {
        document.documentElement.classList.remove("dark");
    }
    updateThemeIcon(isDark);
}

function toggleTheme() {
    const isDark = document.documentElement.classList.toggle("dark");
    localStorage.setItem("theme", isDark ? "dark" : "light");
    updateThemeIcon(isDark);
}

function updateThemeIcon(isDark) {
    const icon = document.getElementById("theme-icon");
    if (icon) {
        icon.className = isDark ? "fa-solid fa-sun text-lg text-amber-400" : "fa-solid fa-moon text-lg text-gray-600";
    }
}

function showToast(message, isError = false) {
    const toast = document.getElementById("toast");
    const msg = document.getElementById("toast-message");
    const icon = document.getElementById("toast-icon");
    if (!toast || !msg || !icon) return;

    msg.innerText = message;
    if (isError) {
        icon.className = "fa-solid fa-triangle-exclamation text-red-400";
    } else {
        icon.className = "fa-solid fa-circle-check text-green-400";
    }

    toast.classList.remove("translate-y-20", "opacity-0");
    setTimeout(() => {
        toast.classList.add("translate-y-20", "opacity-0");
    }, 3000);
}
