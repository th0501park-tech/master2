/**
 * SPORTS HUB - 프론트엔드 메인 인터랙션 스크립트
 */

// 전역 상태
let currentSport = "kbo";
let currentViewMode = "matches"; // 'matches' | 'standings' | 'leaders' | 'teamhub'
let currentMatchFilter = "all"; // 'all' | 'live' | 'finished' | 'upcoming'
let currentKLeagueSub = "k1";
let currentOverseasSub = "epl";
let currentMLBSub = "overall";
let searchDebounceTimer = null;

// 경기 상태 필터 (전체 / 🔴 LIVE / 최근 결과 / 예정 경기)
function setMatchFilter(filterType) {
    currentMatchFilter = filterType || "all";
    document.querySelectorAll(".match-filter-chip").forEach(chip => {
        if (chip.id.endsWith(`-${currentMatchFilter}`)) {
            chip.classList.add("active");
        } else {
            chip.classList.remove("active");
        }
    });

    if (currentSport === "kbo") renderKboMatches();
    else if (currentSport === "kleague") renderKLeague();
    else if (currentSport === "overseas") renderOverseas();
    else if (currentSport === "mlb") renderMlbMatches();
}

function filterMatchesByStatus(matches) {
    if (!matches) return [];
    if (currentMatchFilter === "live") {
        return matches.filter(m => m.is_live || m.status === "LIVE" || (m.status_info && (m.status_info.includes("회") || m.status_info.includes("전반") || m.status_info.includes("후반") || m.status_info.includes("HT") || m.status_info.includes("진행중")) && !m.status_info.includes("종료")));
    } else if (currentMatchFilter === "finished") {
        return matches.filter(m => m.is_finished || m.status === "종료" || (m.status_info && m.status_info.includes("종료")));
    } else if (currentMatchFilter === "upcoming") {
        return matches.filter(m => m.is_upcoming || m.status === "예정" || (m.status_info && (m.status_info.includes("예정") || m.status_info.includes("Scheduled"))));
    }
    return matches;
}

// 선호 구단(마이팀) 상태 관리
const FAVORITES_STORAGE_KEY = "sports_hub_favorites";
let isMyTeamOnlyFilter = false;

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
    currentSport = initialSport || "kbo";

    // 상단 마이팀 배너 초기화
    updateMyTeamBanner();

    // 4대 스포츠 경기 및 영상 렌더링
    renderKboMatches();
    renderKboHighlights();
    renderKboStandings();
    renderKLeague();
    renderOverseas();
    renderMLB();
    renderMlbMatches();
    renderMlbHighlights();

    // 초기 탭 활성화
    switchMainSport(currentSport, false);

    // KBO 구단허브 초기 첫번째 팀 선택
    if (window.INITIAL_DATA?.kbo?.teams?.length > 0) {
        const fav = getFavoriteTeam("kbo");
        renderTeamHubDetails("kbo", fav || window.INITIAL_DATA.kbo.teams[0].team);
    }

    // 모달 배경 클릭 시 닫기
    const modal = document.getElementById("favorite-team-modal");
    if (modal) {
        modal.addEventListener("click", (e) => {
            if (e.target === modal) closeFavoriteTeamModal();
        });
    }

    // 단축키 설정 (Ctrl+K or Cmd+K 로 검색 열기, ESC 로 모달 닫기)
    document.addEventListener("keydown", (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === "k") {
            e.preventDefault();
            openSearchModal();
        } else if (e.key === "Escape") {
            closeSearchModal();
            closeFavoriteTeamModal();
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
// 마이팀 (선호 구단) 핵심 로직
// ========================================================
function getFavoriteTeams() {
    try {
        const stored = localStorage.getItem(FAVORITES_STORAGE_KEY);
        return stored ? JSON.parse(stored) : {};
    } catch (e) {
        return {};
    }
}

let currentModalSubKey = null;

function getFavoriteTeam(sportKey = currentSport, leagueKey = null) {
    const favs = getFavoriteTeams();
    if (sportKey === "overseas") {
        const sub = leagueKey || currentOverseasSub || "epl";
        return favs[`overseas_${sub}`] || (sub === "epl" ? favs["overseas"] : null) || null;
    } else if (sportKey === "kleague") {
        const sub = leagueKey || currentKLeagueSub || "k1";
        let team = favs[`kleague_${sub}`] || null;
        if (!team && favs["kleague"]) {
            // 하위 호환: 기존에 단일 kleague 키로 저장된 구단이 있을 경우 해당 리그 팀인지 확인
            const teams = getAllTeamsForSport("kleague", sub);
            if (teams.some(t => isTeamMatch(t.id, favs["kleague"]) || isTeamMatch(t.name, favs["kleague"]))) {
                team = favs["kleague"];
            }
        }
        return team;
    }
    return favs[sportKey] || null;
}

function setFavoriteTeam(sportKey, teamName, leagueKey = null) {
    if (!sportKey || !teamName) return;
    const favs = getFavoriteTeams();
    let storageKey = sportKey;
    if (sportKey === "overseas") {
        storageKey = `overseas_${leagueKey || currentOverseasSub || 'epl'}`;
    } else if (sportKey === "kleague") {
        storageKey = `kleague_${leagueKey || currentKLeagueSub || 'k1'}`;
        delete favs["kleague"]; // 이전 단일 키 정리
    }
    favs[storageKey] = teamName;
    try {
        localStorage.setItem(FAVORITES_STORAGE_KEY, JSON.stringify(favs));
    } catch (e) {}

    showToast(`⭐ [${teamName}] 선호 구단으로 등록되었습니다!`);
    closeFavoriteTeamModal();
    updateMyTeamBanner();
    refreshCurrentSportViews();
}

function clearFavoriteTeam(sportKey = currentSport, leagueKey = null) {
    const favs = getFavoriteTeams();
    if (sportKey === "overseas") {
        const sub = leagueKey || currentModalSubKey || currentOverseasSub || "epl";
        delete favs[`overseas_${sub}`];
        if (sub === "epl") delete favs["overseas"];
    } else if (sportKey === "kleague") {
        const sub = leagueKey || (currentModalSubKey && currentModalSubKey !== "all" ? currentModalSubKey : null) || currentKLeagueSub || "k1";
        delete favs[`kleague_${sub}`];
        delete favs["kleague"];
    } else {
        delete favs[sportKey];
    }
    try {
        localStorage.setItem(FAVORITES_STORAGE_KEY, JSON.stringify(favs));
    } catch (e) {}

    isMyTeamOnlyFilter = false;
    showToast(`선호 구단 설정이 해제되었습니다.`);
    closeFavoriteTeamModal();
    updateMyTeamBanner();
    refreshCurrentSportViews();
}

function toggleFavoriteTeam(sportKey, teamName, leagueKey = null) {
    const currentFav = getFavoriteTeam(sportKey, leagueKey);
    if (currentFav && isTeamMatch(currentFav, teamName)) {
        clearFavoriteTeam(sportKey, leagueKey);
    } else {
        setFavoriteTeam(sportKey, teamName, leagueKey);
    }
}

function toggleMyTeamFilter() {
    let subKey = null;
    if (currentSport === "overseas") subKey = currentOverseasSub;
    else if (currentSport === "kleague") subKey = currentKLeagueSub;
    const fav = getFavoriteTeam(currentSport, subKey);
    if (!fav) {
        openFavoriteTeamModal();
        return;
    }
    isMyTeamOnlyFilter = !isMyTeamOnlyFilter;
    updateMyTeamBanner();
    refreshCurrentSportViews();
    showToast(isMyTeamOnlyFilter ? `🔍 [${fav}] 경기만 필터링합니다` : "📋 모든 경기를 표시합니다");
}

function isTeamMatch(teamStr, targetStr) {
    if (!teamStr || !targetStr) return false;
    const s1 = String(teamStr).toLowerCase().replace(/[\s\-_]/g, "");
    const s2 = String(targetStr).toLowerCase().replace(/[\s\-_]/g, "");

    // 1. 수원삼성 vs 수원FC 철저 분리
    const isSuwonSamsung1 = s1.includes("수원삼성") || s1.includes("블루윙즈") || s1 === "수원";
    const isSuwonSamsung2 = s2.includes("수원삼성") || s2.includes("블루윙즈") || s2 === "수원";
    const isSuwonFC1 = s1.includes("수원fc") || s1.includes("suwonfc");
    const isSuwonFC2 = s2.includes("수원fc") || s2.includes("suwonfc");
    if ((isSuwonSamsung1 && isSuwonFC2) || (isSuwonFC1 && isSuwonSamsung2)) return false;

    // 2. 맨체스터 시티 vs 맨체스터 유나이티드 철저 분리
    const isManCity1 = s1.includes("맨시티") || s1.includes("mancity") || (s1.includes("맨체스터") && s1.includes("시티"));
    const isManCity2 = s2.includes("맨시티") || s2.includes("mancity") || (s2.includes("맨체스터") && s2.includes("시티"));
    const isManUtd1 = s1.includes("맨유") || s1.includes("manutd") || (s1.includes("맨체스터") && s1.includes("유나이티드"));
    const isManUtd2 = s2.includes("맨유") || s2.includes("manutd") || (s2.includes("맨체스터") && s2.includes("유나이티드"));
    if ((isManCity1 && isManUtd2) || (isManUtd1 && isManCity2)) return false;

    // 3. 레알 마드리드 vs 아틀레티코 마드리드 분리
    const isRealMadrid1 = s1.includes("레알마드리드") || s1.includes("realmadrid") || (s1.includes("레알") && !s1.includes("베티스") && !s1.includes("소시에다드"));
    const isRealMadrid2 = s2.includes("레알마드리드") || s2.includes("realmadrid") || (s2.includes("레알") && !s2.includes("베티스") && !s2.includes("소시에다드"));
    const isAtleti1 = s1.includes("아틀레티코") || s1.includes("atletico") || s1.includes("atm");
    const isAtleti2 = s2.includes("아틀레티코") || s2.includes("atletico") || s2.includes("atm");
    if ((isRealMadrid1 && isAtleti2) || (isAtleti1 && isRealMadrid2)) return false;

    if (s1 === s2) return true;
    return s1.includes(s2) || s2.includes(s1);
}

function getAllTeamsForSport(sportKey, subKey = null) {
    const d = window.INITIAL_DATA;
    if (!d) return [];

    if (sportKey === "kbo") {
        return (d.kbo?.teams || []).map(t => ({
            id: t.team,
            name: t.fullName || t.team,
            emblem: t.emblem,
            sub: "KBO 정규리그",
            subKey: "kbo"
        }));
    } else if (sportKey === "kleague") {
        const k1 = (d.kleague?.k1?.teams || []).map(t => ({ 
            id: t.team, 
            name: t.fullName || t.team, 
            emblem: t.emblem, 
            sub: "K리그 1",
            subKey: "k1" 
        }));
        const k2 = (d.kleague?.k2?.teams || []).map(t => ({ 
            id: t.team, 
            name: t.fullName || t.team, 
            emblem: t.emblem, 
            sub: "K리그 2",
            subKey: "k2" 
        }));
        if (subKey === "k1") return k1;
        if (subKey === "k2") return k2;
        return [...k1, ...k2];
    } else if (sportKey === "overseas") {
        const leagues = d.overseas?.leagues || {};
        if (subKey && leagues[subKey]) {
            return (leagues[subKey].teams || []).map(t => ({
                id: t.team,
                name: t.team,
                teamEng: t.teamEng,
                emblem: t.emblem,
                sub: leagues[subKey].shortName || leagues[subKey].name,
                subKey: subKey
            }));
        }
        const all = [];
        for (const [lKey, lVal] of Object.entries(leagues)) {
            (lVal.teams || []).forEach(t => {
                all.push({ 
                    id: t.team, 
                    name: t.team, 
                    teamEng: t.teamEng,
                    emblem: t.emblem, 
                    sub: lVal.shortName || lVal.name || lKey.toUpperCase(),
                    subKey: lKey 
                });
            });
        }
        return all;
    } else if (sportKey === "mlb") {
        const all = (d.mlb?.all_teams || []).map(t => {
            const isAl = (t.division || "").includes("아메리칸") || (t.division || "").includes("AL");
            return {
                id: t.team,
                name: `${t.team} (${t.teamEng || ''})`,
                emblem: t.emblem,
                sub: t.division || "MLB",
                subKey: isAl ? "al" : "nl"
            };
        });
        if (subKey === "al") return all.filter(t => t.subKey === "al");
        if (subKey === "nl") return all.filter(t => t.subKey === "nl");
        return all;
    }
    return [];
}

function findTeamInfo(sportKey, teamName, subKey = null) {
    if (!teamName) return null;
    const teams = getAllTeamsForSport(sportKey, subKey);
    let found = teams.find(t => isTeamMatch(t.id, teamName) || isTeamMatch(t.name, teamName));
    if (!found && subKey) {
        const allTeams = getAllTeamsForSport(sportKey, null);
        found = allTeams.find(t => isTeamMatch(t.id, teamName) || isTeamMatch(t.name, teamName));
    }
    return found || { id: teamName, name: teamName, emblem: null };
}

function updateMyTeamBanner() {
    const banner = document.getElementById("my-team-banner");
    const emblemContainer = document.getElementById("my-team-badge-icon");
    const sportLabel = document.getElementById("my-team-sport-label");
    const displayName = document.getElementById("my-team-display-name");
    const filterBtn = document.getElementById("my-team-filter-btn");
    const filterText = document.getElementById("my-team-filter-text");
    const actionBtnText = document.getElementById("my-team-action-btn-text");
    if (!banner) return;

    let fav = null;
    let labelText = currentSport.toUpperCase();
    let subTitlePrefix = "";

    if (currentSport === "overseas") {
        const league = window.INITIAL_DATA?.overseas?.leagues?.[currentOverseasSub];
        const leagueShort = league?.shortName || currentOverseasSub.toUpperCase();
        labelText = `해외축구 • ${leagueShort}`;
        subTitlePrefix = `${league?.name || '해외축구'} `;
        fav = getFavoriteTeam("overseas", currentOverseasSub);
    } else if (currentSport === "kleague") {
        const leagueName = currentKLeagueSub === "k2" ? "K리그 2" : "K리그 1";
        labelText = `K LEAGUE • ${currentKLeagueSub.toUpperCase()}`;
        subTitlePrefix = `${leagueName} `;
        fav = getFavoriteTeam("kleague", currentKLeagueSub);
    } else {
        fav = getFavoriteTeam(currentSport);
        if (currentSport === "kbo") labelText = "KBO";
        else if (currentSport === "mlb") labelText = "MLB";
    }

    if (sportLabel) {
        sportLabel.innerText = labelText;
    }

    if (fav) {
        const subForFind = currentSport === "overseas" ? currentOverseasSub : (currentSport === "kleague" ? currentKLeagueSub : null);
        const teamInfo = findTeamInfo(currentSport, fav, subForFind);
        if (emblemContainer) {
            if (teamInfo?.emblem) {
                emblemContainer.innerHTML = `
                    <div class="relative w-8 h-8 flex items-center justify-center">
                        <img src="${teamInfo.emblem}" alt="${fav}" class="w-8 h-8 object-contain drop-shadow-sm" onerror="this.style.display='none'; if (this.nextElementSibling) this.nextElementSibling.classList.remove('hidden');">
                        <span class="w-8 h-8 rounded-full bg-amber-400 text-amber-950 flex items-center justify-center text-sm font-black shadow-xs hidden"><i class="fa-solid fa-star"></i></span>
                    </div>
                `;
            } else {
                emblemContainer.innerHTML = `<span class="w-8 h-8 rounded-full bg-amber-400 text-amber-950 flex items-center justify-center text-sm font-black shadow-xs"><i class="fa-solid fa-star"></i></span>`;
            }
        }

        if (displayName) {
            displayName.innerHTML = `
                <div class="flex items-center space-x-1.5 flex-wrap">
                    <span class="px-2 py-0.5 rounded-full text-[11px] font-black bg-amber-400 text-amber-950 shadow-xs flex items-center space-x-1">
                        <i class="fa-solid fa-star text-[9px]"></i><span>MY TEAM</span>
                    </span>
                    <span class="text-sm sm:text-base font-black text-gray-900 dark:text-white">${teamInfo?.name || fav}</span>
                    <span class="text-[11px] text-gray-500 dark:text-gray-400 hidden md:inline">• 하이라이트 & 경기 결과 최우선 노출 중</span>
                </div>
            `;
        }

        if (actionBtnText) actionBtnText.innerText = "구단 변경";

        if (filterBtn) {
            filterBtn.classList.remove("hidden");
            if (isMyTeamOnlyFilter) {
                filterBtn.className = "px-2.5 py-1.5 rounded-xl text-xs font-bold border border-amber-500 bg-amber-500 text-white shadow-sm transition-all flex items-center space-x-1.5 active:scale-95";
                if (filterText) filterText.innerText = "전체 경기 보기";
            } else {
                filterBtn.className = "px-2.5 py-1.5 rounded-xl text-xs font-bold border border-amber-300 dark:border-amber-700/60 bg-amber-50 hover:bg-amber-100 text-amber-800 dark:bg-amber-950/40 dark:hover:bg-amber-900/60 dark:text-amber-300 transition-all flex items-center space-x-1.5 active:scale-95";
                if (filterText) filterText.innerText = "내 구단 경기만";
            }
        }
    } else {
        if (emblemContainer) {
            emblemContainer.innerHTML = `<span class="w-8 h-8 rounded-full bg-amber-100 dark:bg-amber-900/40 flex items-center justify-center text-amber-600 dark:text-amber-400 text-sm font-black"><i class="fa-regular fa-star"></i></span>`;
        }
        if (displayName) {
            displayName.innerText = `${subTitlePrefix}선호 구단을 설정하면 해당 구단의 경기와 영상이 최우선으로 배치됩니다`;
        }
        if (actionBtnText) actionBtnText.innerText = "선호 구단 선택";
        if (filterBtn) filterBtn.classList.add("hidden");
        isMyTeamOnlyFilter = false;
    }
}

function openFavoriteTeamModal(targetSubKey = null) {
    const modal = document.getElementById("favorite-team-modal");
    if (!modal) return;

    if (currentSport === "overseas") {
        currentModalSubKey = targetSubKey || currentOverseasSub || "epl";
    } else if (currentSport === "kleague") {
        currentModalSubKey = targetSubKey || currentKLeagueSub || "k1";
    } else if (currentSport === "mlb") {
        currentModalSubKey = targetSubKey || "all";
    } else {
        currentModalSubKey = "all";
    }

    renderModalSubTabs();
    renderModalTeamGrid();
    modal.classList.remove("hidden");
}

function renderModalSubTabs() {
    const subtabsContainer = document.getElementById("fav-modal-subtabs");
    const title = document.getElementById("fav-modal-title");
    if (!subtabsContainer) return;

    const meta = SPORT_META[currentSport] || { title: currentSport.toUpperCase() };
    if (title) {
        if (currentSport === "overseas") {
            title.innerText = "해외축구 리그별 선호 구단 선택";
        } else if (currentSport === "kleague") {
            title.innerText = "K리그 (K1 / K2) 리그별 선호 구단 선택";
        } else {
            title.innerText = `${meta.title} 선호 구단 선택`;
        }
    }

    let tabs = [];
    if (currentSport === "overseas") {
        const leagues = window.INITIAL_DATA?.overseas?.leagues || {};
        tabs = Object.entries(leagues).map(([lKey, lVal]) => {
            const hasFav = !!getFavoriteTeam("overseas", lKey);
            return {
                id: lKey,
                label: lVal.shortName || lKey.toUpperCase(),
                hasFav: hasFav
            };
        });
    } else if (currentSport === "kleague") {
        const hasK1 = !!getFavoriteTeam("kleague", "k1");
        const hasK2 = !!getFavoriteTeam("kleague", "k2");
        tabs = [
            { id: "k1", label: "K리그 1", hasFav: hasK1 },
            { id: "k2", label: "K리그 2", hasFav: hasK2 },
            { id: "all", label: "전체 K리그", hasFav: hasK1 || hasK2 }
        ];
    } else if (currentSport === "mlb") {
        tabs = [
            { id: "all", label: "전체 30구단", hasFav: false },
            { id: "al", label: "AL (아메리칸)", hasFav: false },
            { id: "nl", label: "NL (내셔널)", hasFav: false }
        ];
    }

    if (tabs.length === 0) {
        subtabsContainer.classList.add("hidden");
        subtabsContainer.innerHTML = "";
    } else {
        subtabsContainer.classList.remove("hidden");
        subtabsContainer.innerHTML = tabs.map(t => {
            const isActive = currentModalSubKey === t.id;
            return `
                <button type="button" onclick="switchModalSub('${t.id}')" 
                        class="whitespace-nowrap px-3 py-1.5 rounded-xl text-xs font-bold transition-all active:scale-95 flex items-center space-x-1 ${
                            isActive 
                            ? 'bg-blue-600 text-white shadow-xs' 
                            : 'bg-gray-100 hover:bg-gray-200 dark:bg-darkbg-700 dark:hover:bg-darkbg-600 text-gray-700 dark:text-gray-300'
                        }">
                    <span>${t.label}</span>
                    ${t.hasFav ? '<span class="text-amber-300 text-[10px]">⭐</span>' : ''}
                </button>
            `;
        }).join("");
    }
}

function switchModalSub(subKey) {
    currentModalSubKey = subKey;
    renderModalSubTabs();
    renderModalTeamGrid();
}

function renderModalTeamGrid() {
    const grid = document.getElementById("fav-modal-team-grid");
    if (!grid) return;

    const querySub = currentModalSubKey === "all" ? null : currentModalSubKey;
    const teams = getAllTeamsForSport(currentSport, querySub);

    if (teams.length === 0) {
        grid.innerHTML = `<div class="col-span-full py-8 text-center text-xs text-gray-400">등록된 구단 정보가 없습니다.</div>`;
        return;
    }

    grid.innerHTML = teams.map(t => {
        let isSelected = false;
        let targetSubArg = null;

        if (currentSport === "overseas") {
            targetSubArg = t.subKey || currentModalSubKey;
            const favForSub = getFavoriteTeam("overseas", targetSubArg);
            isSelected = favForSub && (isTeamMatch(t.id, favForSub) || isTeamMatch(t.name, favForSub));
        } else if (currentSport === "kleague") {
            targetSubArg = t.subKey || (currentModalSubKey !== "all" ? currentModalSubKey : (t.sub?.includes("2") ? "k2" : "k1"));
            const favForSub = getFavoriteTeam("kleague", targetSubArg);
            isSelected = favForSub && (isTeamMatch(t.id, favForSub) || isTeamMatch(t.name, favForSub));
        } else {
            const currentFav = getFavoriteTeam(currentSport);
            isSelected = currentFav && (isTeamMatch(t.id, currentFav) || isTeamMatch(t.name, currentFav));
        }

        const setFnCall = targetSubArg 
            ? `setFavoriteTeam('${currentSport}', '${escapeHtml(t.id)}', '${targetSubArg}')`
            : `setFavoriteTeam('${currentSport}', '${escapeHtml(t.id)}')`;

        return `
            <button type="button" onclick="${setFnCall}" 
                    class="p-2.5 sm:p-3 rounded-xl border text-left flex items-center space-x-2.5 transition-all active:scale-95 group ${
                        isSelected 
                        ? 'border-amber-400 bg-amber-50 dark:bg-amber-950/40 ring-2 ring-amber-400 shadow-sm' 
                        : 'border-gray-200 dark:border-gray-700 bg-white hover:bg-gray-50 dark:bg-darkbg-700 dark:hover:bg-darkbg-600'
                    }">
                <div class="w-8 h-8 flex-shrink-0 flex items-center justify-center">
                    ${t.emblem ? `<img src="${t.emblem}" alt="${t.name}" class="w-8 h-8 object-contain" onerror="this.style.display='none'; if(this.nextElementSibling) this.nextElementSibling.classList.remove('hidden');"><div class="w-8 h-8 rounded-full bg-gray-100 dark:bg-darkbg-600 flex items-center justify-center text-xs hidden">⚽</div>` : '<div class="w-8 h-8 rounded-full bg-gray-100 dark:bg-darkbg-600 flex items-center justify-center text-xs">⚽</div>'}
                </div>
                <div class="flex-grow min-w-0">
                    <div class="flex items-center justify-between">
                        <span class="text-xs sm:text-sm font-bold text-gray-900 dark:text-white truncate ${isSelected ? 'text-amber-900 dark:text-amber-200' : ''}">${t.name}</span>
                        ${isSelected ? '<span class="text-[10px] font-black px-1.5 py-0.2 rounded bg-amber-400 text-amber-950 ml-1">선택됨</span>' : ''}
                    </div>
                    <span class="text-[10px] text-gray-400 block truncate">${t.sub}</span>
                </div>
            </button>
        `;
    }).join("");
}

function closeFavoriteTeamModal() {
    const modal = document.getElementById("favorite-team-modal");
    if (modal) modal.classList.add("hidden");
}

function refreshCurrentSportViews() {
    if (currentSport === "kbo") {
        renderKboMatches();
        renderKboHighlights();
        renderKboStandings();
    } else if (currentSport === "kleague") {
        renderKLeague();
    } else if (currentSport === "overseas") {
        renderOverseas();
    } else if (currentSport === "mlb") {
        renderMLB();
        renderMlbMatches();
        renderMlbHighlights();
    }
}

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

    // 상단 마이팀 배너 갱신
    updateMyTeamBanner();

    // 모든 스포츠 섹션 숨기고 해당 섹션 표시
    document.querySelectorAll(".sport-section").forEach(sec => sec.classList.add("hidden"));
    const activeSec = document.getElementById(`sport-section-${sportKey}`);
    if (activeSec) activeSec.classList.remove("hidden");

    // 기본 뷰모드 적용
    switchViewMode(currentViewMode);

    // 해당 스포츠 뷰 갱신
    refreshCurrentSportViews();

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
// 2. 뷰 모드 전환 (경기·영상 / 팀순위 / 개인순위 / 구단별 몰아보기)
// ========================================================
function switchViewMode(mode) {
    currentViewMode = mode;

    // 버튼 액티브 토글
    document.querySelectorAll(".view-mode-btn").forEach(btn => btn.classList.remove("active"));
    const activeBtn = document.getElementById(`view-btn-${mode}`);
    if (activeBtn) activeBtn.classList.add("active");

    // 현재 스포츠 섹션 안의 뷰 토글
    const sec = document.getElementById(`sport-section-${currentSport}`);
    if (!sec) return;

    sec.querySelectorAll(".view-content").forEach(v => v.classList.add("hidden"));
    const targetView = document.getElementById(`${currentSport}-view-${mode}`);
    if (targetView) targetView.classList.remove("hidden");

    // 구단별 몰아보기로 이동 시 선호 구단이 있으면 자동으로 해당 구단 허브 열기
    if (mode === "teamhub") {
        const fav = getFavoriteTeam(currentSport);
        if (fav) {
            renderTeamHubDetails(currentSport, fav);
        }
    }
}

// ========================================================
// 2-1. KBO 최근 경기 결과 & 공식 하이라이트 영상 렌더링 (마이팀 연동)
// ========================================================
function renderKboMatches() {
    const kboData = window.INITIAL_DATA?.kbo;
    const grid = document.getElementById("kbo-matches-grid");
    if (!grid || !kboData) return;

    const fav = getFavoriteTeam("kbo");
    let matches = [...(kboData.recent_matches || [])];

    matches.forEach(m => {
        m.isFav = fav && (
            isTeamMatch(m.away_team, fav) ||
            isTeamMatch(m.home_team, fav) ||
            isTeamMatch(m.away_full_name, fav) ||
            isTeamMatch(m.home_full_name, fav)
        );
    });

    if (isMyTeamOnlyFilter && fav) {
        matches = matches.filter(m => m.isFav);
    } else {
        matches.sort((a, b) => (b.isFav ? 1 : 0) - (a.isFav ? 1 : 0));
    }

    // 상태 필터 적용 (전체 / LIVE / 최근 결과 / 예정 경기)
    matches = filterMatchesByStatus(matches);

    if (matches.length === 0) {
        grid.innerHTML = `
            <div class="col-span-full py-10 text-center bg-white dark:bg-darkbg-800 rounded-2xl border border-gray-200 dark:border-gray-800">
                <p class="text-xs sm:text-sm font-bold text-gray-500 dark:text-gray-400">
                    ${isMyTeamOnlyFilter ? `선호 구단 [${fav}]의 해당 조건 경기 일정이 없습니다.` : '해당 조건의 경기 일정이 없습니다.'}
                </p>
                ${(isMyTeamOnlyFilter || currentMatchFilter !== 'all') ? `<button type="button" onclick="setMatchFilter('all'); if (isMyTeamOnlyFilter) toggleMyTeamFilter();" class="mt-3 px-3 py-1.5 rounded-xl bg-blue-50 text-blue-600 dark:bg-blue-950 dark:text-blue-300 text-xs font-bold active:scale-95 transition-all">전체 경기 보기</button>` : ''}
            </div>
        `;
        return;
    }

    grid.innerHTML = matches.map(m => {
        const isLive = m.is_live || m.status === 'LIVE';
        const isFinished = m.is_finished || m.status === '종료';
        const isUpcoming = m.is_upcoming || m.status === '예정';

        let statusBadgeHtml = '';
        if (isLive) {
            statusBadgeHtml = `
                <span class="px-2 py-0.5 rounded text-[10px] font-black bg-red-500 text-white flex items-center space-x-1 shadow-xs animate-pulse">
                    <span class="w-1.5 h-1.5 rounded-full bg-white animate-ping"></span>
                    <span>LIVE ${m.status_info || '진행중'}</span>
                </span>
            `;
        } else if (isFinished) {
            statusBadgeHtml = `
                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-300">
                    종료
                </span>
            `;
        } else {
            statusBadgeHtml = `
                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-700 dark:bg-blue-900/60 dark:text-blue-300">
                    ${m.status_info || '예정'}
                </span>
            `;
        }

        // 투수 정보 박스
        let pitcherInfoHtml = '';
        if (m.win_pitcher || m.lose_pitcher) {
            pitcherInfoHtml = `
                <div class="px-2.5 py-1.5 rounded-xl bg-gray-50 dark:bg-darkbg-900 border border-gray-100 dark:border-gray-800 text-[11px] mb-2 flex items-center justify-between truncate">
                    <div class="flex items-center space-x-2 truncate">
                        ${m.win_pitcher ? `<span class="text-blue-600 dark:text-blue-400 font-extrabold"><span class="px-1 py-0.2 rounded bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300 text-[9px] mr-1">승</span>${m.win_pitcher}</span>` : ''}
                        ${m.lose_pitcher ? `<span class="text-red-500 dark:text-red-400 font-bold"><span class="px-1 py-0.2 rounded bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300 text-[9px] mr-1">패</span>${m.lose_pitcher}</span>` : ''}
                    </div>
                    <span class="text-[10px] text-gray-400 ml-1 flex-shrink-0">결정투수</span>
                </div>
            `;
        } else if (isLive && m.current_pitcher) {
            pitcherInfoHtml = `
                <div class="px-2.5 py-1.5 rounded-xl bg-red-50/60 dark:bg-red-950/30 border border-red-200/60 dark:border-red-800/40 text-[11px] mb-2 flex items-center justify-between truncate">
                    <span class="font-bold text-red-700 dark:text-red-300 truncate">
                        <span class="px-1.5 py-0.2 rounded bg-red-500 text-white font-black text-[9px] mr-1">투수</span>${m.current_pitcher}
                    </span>
                    <span class="text-[10px] text-red-500 font-bold ml-1 flex-shrink-0">${m.status_info || '실시간'}</span>
                </div>
            `;
        } else if (isUpcoming && (m.home_starter || m.away_starter || m.starter_note)) {
            pitcherInfoHtml = `
                <div class="px-2.5 py-1.5 rounded-xl bg-blue-50/60 dark:bg-blue-950/30 border border-blue-200/60 dark:border-blue-800/40 text-[11px] mb-2 flex items-center justify-between truncate">
                    <span class="font-bold text-blue-700 dark:text-blue-300 truncate">
                        ${m.starter_note || `선발: ${m.away_starter || '미정'} vs ${m.home_starter || '미정'}`}
                    </span>
                    <span class="text-[10px] text-blue-500 font-bold ml-1 flex-shrink-0">선발예고</span>
                </div>
            `;
        } else if (m.pitcher_note) {
            pitcherInfoHtml = `
                <div class="px-2.5 py-1.5 rounded-xl bg-gray-50 dark:bg-darkbg-900 border border-gray-100 dark:border-gray-800 text-[11px] mb-2 flex items-center justify-between truncate">
                    <span class="font-medium text-gray-600 dark:text-gray-300 truncate">${m.pitcher_note}</span>
                    <span class="text-[10px] text-gray-400 ml-1 flex-shrink-0">경기정보</span>
                </div>
            `;
        }

        return `
            <div class="bg-white dark:bg-darkbg-800 rounded-2xl border ${isLive ? 'border-red-400 dark:border-red-500 ring-2 ring-red-400/30' : (m.isFav ? 'border-amber-400 dark:border-amber-500 ring-2 ring-amber-400/30 my-team-card' : 'border-gray-200 dark:border-gray-800')} p-3.5 sm:p-4 shadow-sm hover:shadow-md transition-all">
                <div class="flex items-center justify-between pb-2.5 border-b border-gray-100 dark:border-gray-700/60 text-xs">
                    <div class="flex items-center space-x-1.5 text-gray-500 dark:text-gray-400 font-medium">
                        <i class="fa-regular fa-calendar text-[11px]"></i>
                        <span>${m.date}</span>
                        ${m.time ? `<span class="text-[10px] text-gray-400">(${m.time})</span>` : ''}
                    </div>
                    <div class="flex items-center space-x-1.5">
                        ${m.isFav ? `
                        <span class="px-1.5 py-0.2 rounded text-[10px] font-black bg-amber-400 text-amber-950 shadow-xs flex items-center space-x-1">
                            <i class="fa-solid fa-star text-[9px]"></i><span>MY TEAM</span>
                        </span>
                        ` : ''}
                        ${m.stadium ? `
                        <span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-gray-100 dark:bg-darkbg-700 text-gray-600 dark:text-gray-300">
                            ${m.stadium}
                        </span>` : ''}
                        ${statusBadgeHtml}
                    </div>
                </div>

                <div class="py-3 space-y-2">
                    <!-- 원정팀 -->
                    <div class="flex items-center justify-between ${m.away_win ? 'font-black text-gray-900 dark:text-white' : 'text-gray-500 dark:text-gray-400'}">
                        <div class="flex items-center space-x-2.5 truncate">
                            ${m.away_emblem ? `<img src="${m.away_emblem}" alt="${m.away_team}" class="w-6 h-6 object-contain" onerror="this.style.display='none'">` : ''}
                            <span class="text-xs sm:text-sm truncate font-semibold">${m.away_full_name || m.away_team}</span>
                            ${m.away_win ? `<span class="px-1.5 py-0.2 rounded text-[10px] font-bold bg-blue-100 text-blue-700 dark:bg-blue-900/60 dark:text-blue-300">승</span>` : ''}
                            <button type="button" onclick="toggleFavoriteTeam('kbo', '${m.away_team}')" title="선호 구단 등록/해제" 
                                    class="fav-star-btn text-xs ${fav && isTeamMatch(m.away_team, fav) ? 'text-amber-500 font-black' : 'text-gray-300 hover:text-amber-400'} ml-0.5">
                                ★
                            </button>
                        </div>
                        <span class="text-base sm:text-lg ${m.away_win ? 'text-blue-600 dark:text-blue-400 font-black' : (isLive ? 'text-red-600 font-black' : '')}">
                            ${m.away_score}
                        </span>
                    </div>

                    <!-- 홈팀 -->
                    <div class="flex items-center justify-between ${m.home_win ? 'font-black text-gray-900 dark:text-white' : 'text-gray-500 dark:text-gray-400'}">
                        <div class="flex items-center space-x-2.5 truncate">
                            ${m.home_emblem ? `<img src="${m.home_emblem}" alt="${m.home_team}" class="w-6 h-6 object-contain" onerror="this.style.display='none'">` : ''}
                            <span class="text-xs sm:text-sm truncate font-semibold">${m.home_full_name || m.home_team}</span>
                            ${m.home_win ? `<span class="px-1.5 py-0.2 rounded text-[10px] font-bold bg-blue-100 text-blue-700 dark:bg-blue-900/60 dark:text-blue-300">승</span>` : ''}
                            <button type="button" onclick="toggleFavoriteTeam('kbo', '${m.home_team}')" title="선호 구단 등록/해제" 
                                    class="fav-star-btn text-xs ${fav && isTeamMatch(m.home_team, fav) ? 'text-amber-500 font-black' : 'text-gray-300 hover:text-amber-400'} ml-0.5">
                                ★
                            </button>
                        </div>
                        <span class="text-base sm:text-lg ${m.home_win ? 'text-blue-600 dark:text-blue-400 font-black' : (isLive ? 'text-red-600 font-black' : '')}">
                            ${m.home_score}
                        </span>
                    </div>
                </div>

                <!-- 투수 정보 (승리/패전 또는 선발투수) -->
                ${pitcherInfoHtml}

                <div class="pt-2 border-t border-gray-100 dark:border-gray-700/60 flex items-center justify-between text-[11px]">
                    <span class="text-gray-400 truncate">${m.broadcast || '공식 중계'}</span>
                    <button type="button" onclick="focusKboHighlight('${m.away_team}', '${m.home_team}')" 
                            class="px-2.5 py-1 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-600 dark:bg-blue-950/60 dark:hover:bg-blue-900/80 dark:text-blue-300 font-bold flex items-center space-x-1 active:scale-95 transition-all">
                        <i class="fa-solid fa-play text-[9px]"></i>
                        <span>하이라이트</span>
                    </button>
                </div>
            </div>
        `;
    }).join("");
}

function renderKboHighlights() {
    const kboData = window.INITIAL_DATA?.kbo;
    const hlList = document.getElementById("kbo-highlight-list");
    if (!hlList || !kboData) return;

    const fav = getFavoriteTeam("kbo");
    let highlights = [...(kboData.highlights || [])];

    highlights.forEach(h => {
        h.isFav = fav && (isTeamMatch(h.title, fav) || isTeamMatch(h.match, fav));
    });

    highlights.sort((a, b) => (b.isFav ? 1 : 0) - (a.isFav ? 1 : 0));

    // 선호 구단 영상이 1순위로 있으면 상단 플레이어 프리뷰에 해당 영상 기본 세팅
    if (highlights.length > 0 && highlights[0].isFav) {
        const frame = document.getElementById("kbo-video-frame");
        const thumbEl = document.getElementById("kbo-facade-thumb");
        const titleEl = document.getElementById("kbo-current-video-title");
        const dateEl = document.getElementById("kbo-current-video-date");
        const tagEl = document.getElementById("kbo-current-video-tag");
        if (frame) {
            frame.dataset.src = `${highlights[0].embed_url}?rel=0`;
        }
        if (thumbEl && highlights[0].thumbnail) {
            thumbEl.src = highlights[0].thumbnail;
        }
        if (titleEl) titleEl.innerText = highlights[0].title;
        if (dateEl) dateEl.innerText = highlights[0].date;
        if (tagEl) tagEl.innerText = `★ ${fav} 공식 영상`;
    }

    hlList.innerHTML = `
        <span class="text-xs font-bold text-gray-400 block mb-1">
            ${fav ? `선호 구단 [${fav}] 영상 우선 배치됨 (클릭 시 바로 재생)` : '최신 공식 하이라이트 영상 목록 (클릭 시 바로 재생)'}
        </span>
        ${highlights.map(hl => `
            <div onclick="playKboVideo('${hl.embed_url}', '${escapeHtml(hl.title)}', '${hl.date}')" 
                 class="kbo-hl-card cursor-pointer p-2 rounded-xl border ${hl.isFav ? 'border-amber-400 bg-amber-50/40 dark:bg-amber-950/40 shadow-xs' : 'border-gray-100 dark:border-gray-700/60 bg-white dark:bg-darkbg-800'} hover:bg-blue-50/50 dark:hover:bg-darkbg-700 transition-all flex items-center space-x-3 active:scale-98 group shadow-xs">
                <div class="relative w-28 h-16 sm:w-32 sm:h-18 rounded-lg overflow-hidden flex-shrink-0 bg-gray-200 dark:bg-gray-800">
                    <img src="${hl.thumbnail}" alt="${hl.title}" class="w-full h-full object-cover group-hover:scale-105 transition-transform" onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1508344928928-7165b67de128?w=640&auto=format&fit=crop&q=80'">
                    <div class="absolute inset-0 bg-black/30 flex items-center justify-center opacity-80 group-hover:opacity-100 transition-opacity">
                        <span class="w-7 h-7 rounded-full bg-red-600 text-white flex items-center justify-center shadow-md">
                            <i class="fa-solid fa-play text-[10px] ml-0.5"></i>
                        </span>
                    </div>
                </div>
                <div class="flex-grow min-w-0">
                    <div class="flex items-center space-x-1 mb-0.5">
                        ${hl.isFav ? `<span class="px-1.5 py-0.2 rounded text-[9px] font-black bg-amber-400 text-amber-950 flex-shrink-0">MY TEAM</span>` : ''}
                        <h4 class="text-xs font-bold text-gray-900 dark:text-white line-clamp-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 leading-snug">
                            ${hl.title}
                        </h4>
                    </div>
                    <div class="flex items-center justify-between text-[11px] text-gray-400 mt-1">
                        <span class="font-medium truncate">${hl.match || 'KBO'}</span>
                        <span class="ml-1 text-[10px]">${hl.date}</span>
                    </div>
                </div>
            </div>
        `).join("")}
    `;
}

function renderKboStandings() {
    const kboData = window.INITIAL_DATA?.kbo;
    const tbody = document.getElementById("kbo-table-body");
    if (!tbody || !kboData) return;

    const fav = getFavoriteTeam("kbo");
    const teams = kboData.teams || [];

    tbody.innerHTML = teams.map(t => {
        const isFavTeam = fav && isTeamMatch(t.team, fav);
        return `
            <tr class="hover:bg-blue-50/40 dark:hover:bg-darkbg-700/50 transition-colors ${isFavTeam ? 'bg-amber-50/30 dark:bg-amber-950/20 border-l-4 border-l-amber-500' : (t.rank <= 5 ? 'border-l-4 border-l-blue-500' : '')}">
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-4 text-center font-bold">
                    <span class="w-5 h-5 sm:w-6 sm:h-6 rounded-full inline-flex items-center justify-center text-[11px] sm:text-xs
                        ${isFavTeam ? 'bg-amber-400 text-amber-950 font-black' : (t.rank === 1 ? 'bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-300 font-black' : (t.rank <= 3 ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300' : (t.rank <= 5 ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300' : 'text-gray-500 dark:text-gray-400')))}">
                        ${t.rank}
                    </span>
                </td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-4 font-semibold text-gray-900 dark:text-white">
                    <div class="flex items-center space-x-2 sm:space-x-3">
                        ${t.emblem ? `<img src="${t.emblem}" alt="${t.team}" class="w-5 h-5 sm:w-7 sm:h-7 object-contain drop-shadow-sm" onerror="this.style.display='none'">` : ''}
                        <span class="hidden sm:inline ${isFavTeam ? 'font-black text-amber-900 dark:text-amber-200' : ''}">${t.fullName}</span>
                        <span class="sm:hidden font-bold ${isFavTeam ? 'font-black text-amber-900 dark:text-amber-200' : ''}">${t.team}</span>
                        <button type="button" onclick="toggleFavoriteTeam('kbo', '${t.team}')" title="선호 구단 등록/해제" 
                                class="fav-star-btn text-xs ${isFavTeam ? 'text-amber-500 font-black' : 'text-gray-300 hover:text-amber-400'} ml-0.5">
                            ★
                        </button>
                    </div>
                </td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center text-gray-600 dark:text-gray-300">${t.games}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center font-bold text-gray-900 dark:text-white">${t.win}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center text-gray-600 dark:text-gray-300">${t.loss}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center text-gray-600 dark:text-gray-300">${t.draw}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center font-extrabold text-blue-600 dark:text-blue-400 text-xs sm:text-sm">${t.rate}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center text-gray-600 dark:text-gray-300">${t.game_diff}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center text-xs text-gray-500 dark:text-gray-400 hidden md:table-cell">${t.recent10}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center text-xs hidden sm:table-cell">
                    <span class="px-1.5 py-0.5 rounded-full text-[11px] font-semibold ${t.streak && t.streak.includes('승') ? 'bg-red-50 text-red-600 dark:bg-red-950/60 dark:text-red-400' : 'bg-gray-100 text-gray-600 dark:bg-darkbg-700 dark:text-gray-300'}">
                        ${t.streak}
                    </span>
                </td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center text-xs text-gray-500 dark:text-gray-400 hidden lg:table-cell">${t.home}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-3 text-center text-xs text-gray-500 dark:text-gray-400 hidden lg:table-cell">${t.away}</td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-4 text-center">
                    <button type="button" onclick="selectTeamInHub('kbo', '${t.team}')" class="px-2 py-1 text-[11px] sm:text-xs font-semibold rounded-lg bg-gray-100 hover:bg-blue-600 hover:text-white dark:bg-darkbg-700 dark:hover:bg-blue-600 text-gray-700 dark:text-gray-200 transition-colors active:scale-95">
                        선수기록 ➔
                    </button>
                </td>
            </tr>
        `;
    }).join("");
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
    updateMyTeamBanner();
    renderKLeague();
}

function renderKLeague() {
    const klData = window.INITIAL_DATA?.kleague;
    if (!klData) return;

    const subData = klData[currentKLeagueSub];
    if (!subData) return;

    const fav = getFavoriteTeam("kleague", currentKLeagueSub);

    // 0-1) K리그 최근 경기 결과 렌더링
    const matchesTitle = document.getElementById("kleague-matches-title");
    if (matchesTitle) matchesTitle.innerText = `2026 ${subData.name} 최근 경기 결과`;

    const matchesGrid = document.getElementById("kleague-matches-grid");
    if (matchesGrid) {
        let recentMatches = [...(subData.recent_matches || [])];
        recentMatches.forEach(m => {
            m.isFav = fav && (isTeamMatch(m.home_team, fav) || isTeamMatch(m.away_team, fav));
        });

        if (isMyTeamOnlyFilter && fav) {
            recentMatches = recentMatches.filter(m => m.isFav);
        } else {
            recentMatches.sort((a, b) => (b.isFav ? 1 : 0) - (a.isFav ? 1 : 0));
        }

        // 상태 필터 적용 (전체 / LIVE / 최근 결과 / 예정 경기)
        recentMatches = filterMatchesByStatus(recentMatches);

        if (recentMatches.length === 0) {
            matchesGrid.innerHTML = `
                <div class="col-span-full py-10 text-center bg-white dark:bg-darkbg-800 rounded-2xl border border-gray-200 dark:border-gray-800">
                    <p class="text-xs sm:text-sm font-bold text-gray-500 dark:text-gray-400">
                        ${isMyTeamOnlyFilter ? `선호 구단 [${fav}]의 해당 조건 경기 일정이 없습니다.` : '해당 조건의 경기 일정이 없습니다.'}
                    </p>
                    ${(isMyTeamOnlyFilter || currentMatchFilter !== 'all') ? `<button type="button" onclick="setMatchFilter('all'); if (isMyTeamOnlyFilter) toggleMyTeamFilter();" class="mt-3 px-3 py-1.5 rounded-xl bg-blue-50 text-blue-600 dark:bg-blue-950 dark:text-blue-300 text-xs font-bold active:scale-95 transition-all">전체 경기 보기</button>` : ''}
                </div>
            `;
        } else {
            matchesGrid.innerHTML = recentMatches.map(m => {
                const isLive = m.is_live || m.status === 'LIVE' || (typeof m.status === 'string' && m.status.includes('LIVE'));
                const isFinished = m.is_finished || m.status === '종료';
                const isUpcoming = m.is_upcoming || m.status === '예정';

                let statusBadgeHtml = '';
                if (isLive) {
                    statusBadgeHtml = `
                        <span class="px-2 py-0.5 rounded text-[10px] font-black bg-red-500 text-white flex items-center space-x-1 shadow-xs animate-pulse">
                            <span class="w-1.5 h-1.5 rounded-full bg-white animate-ping"></span>
                            <span>LIVE ${m.status_info || '진행중'}</span>
                        </span>
                    `;
                } else if (isFinished) {
                    statusBadgeHtml = `
                        <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-300">
                            종료
                        </span>
                    `;
                } else {
                    statusBadgeHtml = `
                        <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-700 dark:bg-blue-900/60 dark:text-blue-300">
                            금주 예정
                        </span>
                    `;
                }

                // 라이브 진행 정보
                let liveNoticeHtml = '';
                if (isLive && m.status_info) {
                    liveNoticeHtml = `
                        <div class="px-2.5 py-1 rounded-xl bg-red-50/60 dark:bg-red-950/30 border border-red-200/60 dark:border-red-800/40 text-[11px] mb-2 flex items-center justify-between text-red-600 dark:text-red-400 font-bold">
                            <span class="flex items-center space-x-1.5 truncate">
                                <i class="fa-regular fa-clock text-[10px]"></i>
                                <span>경기 진행 중 (${m.status_info})</span>
                            </span>
                            <span class="text-[10px] px-1.5 py-0.2 rounded bg-red-100 dark:bg-red-900/60 font-black flex-shrink-0">실시간 스코어</span>
                        </div>
                    `;
                }

                const homeScoreDisplay = isUpcoming ? '-' : (m.home_goal !== null && m.home_goal !== undefined ? m.home_goal : '-');
                const awayScoreDisplay = isUpcoming ? '-' : (m.away_goal !== null && m.away_goal !== undefined ? m.away_goal : '-');

                return `
                <div class="bg-white dark:bg-darkbg-800 rounded-2xl border ${isLive ? 'border-red-400 dark:border-red-500 ring-2 ring-red-400/30' : (m.isFav ? 'border-amber-400 dark:border-amber-500 ring-2 ring-amber-400/30 my-team-card' : 'border-gray-200 dark:border-gray-800')} p-3.5 sm:p-4 shadow-sm hover:shadow-md transition-all">
                    <div class="flex items-center justify-between pb-2.5 border-b border-gray-100 dark:border-gray-700/60 text-xs">
                        <div class="flex items-center space-x-1.5 text-gray-500 dark:text-gray-400 font-medium">
                            <i class="fa-regular fa-calendar text-[11px]"></i>
                            <span>${m.game_date || m.date || ''}</span>
                            ${m.game_time ? `<span class="text-[10px] text-gray-400">(${m.game_time})</span>` : ''}
                        </div>
                        <div class="flex items-center space-x-1.5">
                            ${m.isFav ? `
                            <span class="px-1.5 py-0.2 rounded text-[10px] font-black bg-amber-400 text-amber-950 shadow-xs flex items-center space-x-1">
                                <i class="fa-solid fa-star text-[9px]"></i><span>MY TEAM</span>
                            </span>
                            ` : ''}
                            ${m.round ? `<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300">${m.round}</span>` : ''}
                            ${statusBadgeHtml}
                        </div>
                    </div>
                    <div class="py-3 space-y-2">
                        <!-- 홈팀 -->
                        <div class="flex items-center justify-between ${m.home_win ? 'font-black text-gray-900 dark:text-white' : 'text-gray-500 dark:text-gray-400'}">
                            <div class="flex items-center space-x-2.5 truncate">
                                ${m.home_emblem ? `<img src="${m.home_emblem}" alt="${m.home_team}" class="w-6 h-6 object-contain" onerror="this.style.display='none'">` : ''}
                                <span class="text-xs sm:text-sm truncate font-semibold">${m.home_team}</span>
                                ${m.home_win ? `<span class="px-1.5 py-0.2 rounded text-[10px] font-bold bg-blue-100 text-blue-700 dark:bg-blue-900/60 dark:text-blue-300">승</span>` : ''}
                                <button type="button" onclick="toggleFavoriteTeam('kleague', '${m.home_team}', '${currentKLeagueSub}')" title="선호 구단 등록/해제" 
                                        class="fav-star-btn text-xs ${fav && isTeamMatch(m.home_team, fav) ? 'text-amber-500 font-black' : 'text-gray-300 hover:text-amber-400'} ml-0.5">
                                    ★
                                </button>
                            </div>
                            <span class="text-base sm:text-lg ${m.home_win ? 'text-blue-600 dark:text-blue-400 font-black' : (isLive ? 'text-red-600 dark:text-red-400 font-black' : '')}">${homeScoreDisplay}</span>
                        </div>
                        <!-- 원정팀 -->
                        <div class="flex items-center justify-between ${m.away_win ? 'font-black text-gray-900 dark:text-white' : 'text-gray-500 dark:text-gray-400'}">
                            <div class="flex items-center space-x-2.5 truncate">
                                ${m.away_emblem ? `<img src="${m.away_emblem}" alt="${m.away_team}" class="w-6 h-6 object-contain" onerror="this.style.display='none'">` : ''}
                                <span class="text-xs sm:text-sm truncate font-semibold">${m.away_team}</span>
                                ${m.away_win ? `<span class="px-1.5 py-0.2 rounded text-[10px] font-bold bg-blue-100 text-blue-700 dark:bg-blue-900/60 dark:text-blue-300">승</span>` : ''}
                                <button type="button" onclick="toggleFavoriteTeam('kleague', '${m.away_team}', '${currentKLeagueSub}')" title="선호 구단 등록/해제" 
                                        class="fav-star-btn text-xs ${fav && isTeamMatch(m.away_team, fav) ? 'text-amber-500 font-black' : 'text-gray-300 hover:text-amber-400'} ml-0.5">
                                    ★
                                </button>
                            </div>
                            <span class="text-base sm:text-lg ${m.away_win ? 'text-blue-600 dark:text-blue-400 font-black' : (isLive ? 'text-red-600 dark:text-red-400 font-black' : '')}">${awayScoreDisplay}</span>
                        </div>
                    </div>
                    ${liveNoticeHtml}
                    <div class="pt-2 border-t border-gray-100 dark:border-gray-700/60 flex items-center justify-between text-[11px]">
                        <span class="text-gray-400 truncate">${m.field_name || '경기장'}</span>
                        <button type="button" onclick="focusKleagueHighlight('${m.home_team}', '${m.away_team}')" 
                                class="px-2.5 py-1 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-600 dark:bg-blue-950/60 dark:hover:bg-blue-900/80 dark:text-blue-300 font-bold flex items-center space-x-1 active:scale-95 transition-all">
                            <i class="fa-solid fa-play text-[9px]"></i>
                            <span>하이라이트</span>
                        </button>
                    </div>
                </div>
                `;
            }).join("");
        }
    }

    // 0-2) K리그 하이라이트 영상 목록 렌더링 (K1 / K2 리그별 완전 분리)
    const hlSectionTitle = document.getElementById("kleague-video-section-title");
    if (hlSectionTitle) hlSectionTitle.innerText = `2026 ${subData.name} 공식 하이라이트 & 30분 경기영상`;

    const hlList = document.getElementById("kleague-highlight-list");
    if (hlList) {
        let highlights = [...(subData.highlights || [])];
        if (highlights.length === 0) {
            highlights = [...(klData.highlights || [])];
        }
        highlights.forEach(h => {
            h.isFav = fav && isTeamMatch(h.title, fav);
        });

        highlights.sort((a, b) => (b.isFav ? 1 : 0) - (a.isFav ? 1 : 0));

        // 리그 전환 시 해당 리그 1순위(선호구단 우선) 영상 플레이어 프리뷰 세팅
        if (highlights.length > 0) {
            const topVideo = highlights[0];
            const frame = document.getElementById("kleague-video-frame");
            const thumbEl = document.getElementById("kleague-facade-thumb");
            const titleEl = document.getElementById("kleague-current-video-title");
            const dateEl = document.getElementById("kleague-current-video-date");
            const tagEl = document.getElementById("kleague-current-video-tag");
            if (frame) {
                frame.dataset.src = `${topVideo.embed_url}?rel=0`;
            }
            if (thumbEl && topVideo.thumbnail) {
                thumbEl.src = topVideo.thumbnail;
            }
            if (titleEl) titleEl.innerText = topVideo.title;
            if (dateEl) dateEl.innerText = topVideo.date;
            if (tagEl) tagEl.innerText = topVideo.isFav ? `★ ${fav} 공식 영상` : `${subData.name} 공식`;
        }

        hlList.innerHTML = `
            <span class="text-xs font-bold text-gray-400 block mb-1">
                ${fav ? `선호 구단 [${fav}] 영상 우선 배치됨 (클릭 시 바로 재생)` : `${subData.name} 30분 하이라이트 목록 (클릭 시 바로 재생)`}
            </span>
            ${highlights.map(hl => `
                <div onclick="playKleagueVideo('${hl.embed_url}', '${escapeHtml(hl.title)}', '${hl.date}')" 
                     class="kleague-hl-card cursor-pointer p-2 rounded-xl border ${hl.isFav ? 'border-amber-400 bg-amber-50/40 dark:bg-amber-950/40 shadow-xs' : 'border-gray-100 dark:border-gray-700/60 bg-white dark:bg-darkbg-800'} hover:bg-blue-50/50 dark:hover:bg-darkbg-700 transition-all flex items-center space-x-3 active:scale-98 group shadow-xs">
                    <div class="relative w-28 h-16 sm:w-32 sm:h-18 rounded-lg overflow-hidden flex-shrink-0 bg-gray-200 dark:bg-gray-800">
                        <img src="${hl.thumbnail}" alt="${hl.title}" class="w-full h-full object-cover group-hover:scale-105 transition-transform" onerror="this.onerror=null; this.src='https://img.youtube.com/vi/${hl.youtube_id}/hqdefault.jpg'">
                        <div class="absolute inset-0 bg-black/30 flex items-center justify-center opacity-80 group-hover:opacity-100 transition-opacity">
                            <span class="w-7 h-7 rounded-full bg-red-600 text-white flex items-center justify-center shadow-md">
                                <i class="fa-solid fa-play text-[10px] ml-0.5"></i>
                            </span>
                        </div>
                    </div>
                    <div class="flex-grow min-w-0">
                        <div class="flex items-center space-x-1 mb-0.5">
                            ${hl.isFav ? `<span class="px-1.5 py-0.2 rounded text-[9px] font-black bg-amber-400 text-amber-950 flex-shrink-0">MY TEAM</span>` : ''}
                            <h4 class="text-xs font-bold text-gray-900 dark:text-white line-clamp-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 leading-snug">
                                ${hl.title}
                            </h4>
                        </div>
                        <div class="flex items-center justify-between text-[11px] text-gray-400 mt-1">
                            <span class="font-medium truncate">${hl.source || (subData.name + ' 공식')}</span>
                            <span class="ml-1 text-[10px]">${hl.date}</span>
                        </div>
                    </div>
                </div>
            `).join("")}
        `;
    }

    // 1) 테이블 제목
    const tableTitle = document.getElementById("kleague-table-title");
    if (tableTitle) tableTitle.innerText = `🏆 ${subData.name} 팀 순위표`;

    // 2) 팀 순위 테이블
    const tbody = document.getElementById("kleague-table-body");
    if (tbody) {
        tbody.innerHTML = subData.teams.map((t, idx) => {
            const isTop = t.rank <= 3;
            const isFavTeam = fav && isTeamMatch(t.team, fav);
            const recentHtml = (t.recent || []).map(r => {
                let badgeClass = "bg-gray-100 text-gray-700 dark:bg-darkbg-700 dark:text-gray-300";
                if (r === "승") badgeClass = "bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-300 font-bold";
                else if (r === "패") badgeClass = "bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300";
                return `<span class="px-1.5 py-0.5 rounded text-[11px] ${badgeClass}">${r}</span>`;
            }).join(" ");

            return `
            <tr class="hover:bg-blue-50/40 dark:hover:bg-darkbg-700/50 transition-colors ${isFavTeam ? 'bg-amber-50/30 dark:bg-amber-950/20 border-l-4 border-l-amber-500' : (isTop ? 'border-l-4 border-l-emerald-500' : '')}">
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-4 text-center font-bold">
                    <span class="w-5 h-5 sm:w-6 sm:h-6 rounded-full inline-flex items-center justify-center text-[11px] sm:text-xs ${isFavTeam ? 'bg-amber-400 text-amber-950 font-black' : (isTop ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 font-black' : 'text-gray-500 dark:text-gray-400')}">
                        ${t.rank}
                    </span>
                </td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-4 font-semibold text-gray-900 dark:text-white">
                    <div class="flex items-center space-x-2 sm:space-x-3">
                        ${t.emblem ? `<img src="${t.emblem}" alt="${t.team}" class="w-5 h-5 sm:w-7 sm:h-7 object-contain drop-shadow-sm" onerror="this.style.display='none'">` : ''}
                        <span class="hidden sm:inline ${isFavTeam ? 'font-black text-amber-900 dark:text-amber-200' : ''}">${t.fullName}</span>
                        <span class="sm:hidden font-bold ${isFavTeam ? 'font-black text-amber-900 dark:text-amber-200' : ''}">${t.team}</span>
                        <button type="button" onclick="toggleFavoriteTeam('kleague', '${t.team}', '${currentKLeagueSub}')" title="선호 구단 등록/해제" 
                                class="fav-star-btn text-xs ${isFavTeam ? 'text-amber-500 font-black' : 'text-gray-300 hover:text-amber-400'}">
                            ★
                        </button>
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
            const initialHubTeam = fav && subData.teams.find(t => isTeamMatch(t.team, fav)) ? fav : subData.teams[0].team;
            renderTeamHubDetails("kleague", initialHubTeam);
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
    updateMyTeamBanner();
    renderOverseas();
}

function renderOverseas() {
    const socData = window.INITIAL_DATA?.overseas;
    if (!socData) return;

    const league = socData.leagues ? socData.leagues[currentOverseasSub] : null;
    if (!league) return;

    const fav = getFavoriteTeam("overseas", currentOverseasSub);

    // 0-1) 해외축구 최근 경기 결과 렌더링
    const matchesTitle = document.getElementById("overseas-matches-title");
    if (matchesTitle) matchesTitle.innerText = `${league.name} 최근 경기 결과`;

    const matchesGrid = document.getElementById("overseas-matches-grid");
    if (matchesGrid) {
        let recentMatches = [...(league.recent_matches || [])];
        recentMatches.forEach(m => {
            m.isFav = fav && (
                isTeamMatch(m.home_team, fav) || 
                isTeamMatch(m.away_team, fav) ||
                isTeamMatch(m.home_short, fav) ||
                isTeamMatch(m.away_short, fav)
            );
        });

        if (isMyTeamOnlyFilter && fav) {
            recentMatches = recentMatches.filter(m => m.isFav);
        } else {
            recentMatches.sort((a, b) => (b.isFav ? 1 : 0) - (a.isFav ? 1 : 0));
        }

        // 상태 필터 적용 (전체 / LIVE / 최근 결과 / 예정 경기)
        recentMatches = filterMatchesByStatus(recentMatches);

        if (recentMatches.length === 0) {
            matchesGrid.innerHTML = `
                <div class="col-span-full py-10 text-center bg-white dark:bg-darkbg-800 rounded-2xl border border-gray-200 dark:border-gray-800">
                    <p class="text-xs sm:text-sm font-bold text-gray-500 dark:text-gray-400">
                        ${isMyTeamOnlyFilter ? `선호 구단 [${fav}]의 해당 조건 경기 일정이 없습니다.` : '해당 조건의 경기 일정이 없습니다.'}
                    </p>
                    ${(isMyTeamOnlyFilter || currentMatchFilter !== 'all') ? `<button type="button" onclick="setMatchFilter('all'); if (isMyTeamOnlyFilter) toggleMyTeamFilter();" class="mt-3 px-3 py-1.5 rounded-xl bg-blue-50 text-blue-600 dark:bg-blue-950 dark:text-blue-300 text-xs font-bold active:scale-95 transition-all">전체 경기 보기</button>` : ''}
                </div>
            `;
        } else {
            matchesGrid.innerHTML = recentMatches.map(m => {
                const isLive = m.is_live || m.status === 'LIVE' || (typeof m.status === 'string' && m.status.includes('LIVE'));
                const isFinished = m.is_finished || m.status === '종료';
                const isUpcoming = m.is_upcoming || m.status === '예정';

                let statusBadgeHtml = '';
                if (isLive) {
                    statusBadgeHtml = `
                        <span class="px-2 py-0.5 rounded text-[10px] font-black bg-red-500 text-white flex items-center space-x-1 shadow-xs animate-pulse">
                            <span class="w-1.5 h-1.5 rounded-full bg-white animate-ping"></span>
                            <span>LIVE ${m.status_info || m.display_clock || '진행중'}</span>
                        </span>
                    `;
                } else if (isFinished) {
                    statusBadgeHtml = `
                        <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-300">
                            종료
                        </span>
                    `;
                } else {
                    statusBadgeHtml = `
                        <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-700 dark:bg-blue-900/60 dark:text-blue-300">
                            금주 예정
                        </span>
                    `;
                }

                // 라이브 진행 정보
                let liveNoticeHtml = '';
                if (isLive && (m.status_info || m.display_clock)) {
                    liveNoticeHtml = `
                        <div class="px-2.5 py-1 rounded-xl bg-red-50/60 dark:bg-red-950/30 border border-red-200/60 dark:border-red-800/40 text-[11px] mb-2 flex items-center justify-between text-red-600 dark:text-red-400 font-bold">
                            <span class="flex items-center space-x-1.5 truncate">
                                <i class="fa-regular fa-clock text-[10px]"></i>
                                <span>실시간 진행 (${m.status_info || m.display_clock})</span>
                            </span>
                            <span class="text-[10px] px-1.5 py-0.2 rounded bg-red-100 dark:bg-red-900/60 font-black flex-shrink-0">실시간 스코어</span>
                        </div>
                    `;
                }

                const homeScoreDisplay = isUpcoming ? '-' : (m.home_score !== null && m.home_score !== undefined ? m.home_score : '-');
                const awayScoreDisplay = isUpcoming ? '-' : (m.away_score !== null && m.away_score !== undefined ? m.away_score : '-');

                return `
                <div class="bg-white dark:bg-darkbg-800 rounded-2xl border ${isLive ? 'border-red-400 dark:border-red-500 ring-2 ring-red-400/30' : (m.isFav ? 'border-amber-400 dark:border-amber-500 ring-2 ring-amber-400/30 my-team-card' : 'border-gray-200 dark:border-gray-800')} p-3.5 sm:p-4 shadow-sm hover:shadow-md transition-all">
                    <div class="flex items-center justify-between pb-2.5 border-b border-gray-100 dark:border-gray-700/60 text-xs">
                        <div class="flex items-center space-x-1.5 text-gray-500 dark:text-gray-400 font-medium">
                            <i class="fa-regular fa-calendar text-[11px]"></i>
                            <span>${m.date}</span>
                            ${m.time ? `<span class="text-[10px] text-gray-400">(${m.time})</span>` : ''}
                        </div>
                        <div class="flex items-center space-x-1.5">
                            ${m.isFav ? `
                            <span class="px-1.5 py-0.2 rounded text-[10px] font-black bg-amber-400 text-amber-950 shadow-xs flex items-center space-x-1">
                                <i class="fa-solid fa-star text-[9px]"></i><span>MY TEAM</span>
                            </span>
                            ` : ''}
                            ${statusBadgeHtml}
                        </div>
                    </div>
                    <div class="py-3 space-y-2">
                        <!-- 홈팀 -->
                        <div class="flex items-center justify-between ${m.home_win ? 'font-black text-gray-900 dark:text-white' : 'text-gray-500 dark:text-gray-400'}">
                            <div class="flex items-center space-x-2.5 truncate">
                                ${m.home_emblem ? `<img src="${m.home_emblem}" alt="${m.home_team}" class="w-6 h-6 object-contain" onerror="this.style.display='none'">` : ''}
                                <span class="text-xs sm:text-sm truncate font-semibold">${m.home_short || m.home_team}</span>
                                ${m.home_win ? `<span class="px-1.5 py-0.2 rounded text-[10px] font-bold bg-blue-100 text-blue-700 dark:bg-blue-900/60 dark:text-blue-300">승</span>` : ''}
                                <button type="button" onclick="toggleFavoriteTeam('overseas', '${m.home_short || m.home_team}', '${currentOverseasSub}')" title="선호 구단 등록/해제" 
                                        class="fav-star-btn text-xs ${fav && isTeamMatch(m.home_team, fav) ? 'text-amber-500 font-black' : 'text-gray-300 hover:text-amber-400'} ml-0.5">
                                    ★
                                </button>
                            </div>
                            <span class="text-base sm:text-lg ${m.home_win ? 'text-blue-600 dark:text-blue-400 font-black' : (isLive ? 'text-red-600 dark:text-red-400 font-black' : '')}">${homeScoreDisplay}</span>
                        </div>
                        <!-- 원정팀 -->
                        <div class="flex items-center justify-between ${m.away_win ? 'font-black text-gray-900 dark:text-white' : 'text-gray-500 dark:text-gray-400'}">
                            <div class="flex items-center space-x-2.5 truncate">
                                ${m.away_emblem ? `<img src="${m.away_emblem}" alt="${m.away_team}" class="w-6 h-6 object-contain" onerror="this.style.display='none'">` : ''}
                                <span class="text-xs sm:text-sm truncate font-semibold">${m.away_short || m.away_team}</span>
                                ${m.away_win ? `<span class="px-1.5 py-0.2 rounded text-[10px] font-bold bg-blue-100 text-blue-700 dark:bg-blue-900/60 dark:text-blue-300">승</span>` : ''}
                                <button type="button" onclick="toggleFavoriteTeam('overseas', '${m.away_short || m.away_team}', '${currentOverseasSub}')" title="선호 구단 등록/해제" 
                                        class="fav-star-btn text-xs ${fav && isTeamMatch(m.away_team, fav) ? 'text-amber-500 font-black' : 'text-gray-300 hover:text-amber-400'} ml-0.5">
                                    ★
                                </button>
                            </div>
                            <span class="text-base sm:text-lg ${m.away_win ? 'text-blue-600 dark:text-blue-400 font-black' : (isLive ? 'text-red-600 dark:text-red-400 font-black' : '')}">${awayScoreDisplay}</span>
                        </div>
                    </div>
                    ${liveNoticeHtml}
                    <div class="pt-2 border-t border-gray-100 dark:border-gray-700/60 flex items-center justify-between text-[11px]">
                        <span class="text-gray-400 truncate">${m.venue || '경기장'}</span>
                        <button type="button" onclick="focusOverseasHighlight('${m.home_team}', '${m.away_team}')" 
                                class="px-2.5 py-1 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-600 dark:bg-blue-950/60 dark:hover:bg-blue-900/80 dark:text-blue-300 font-bold flex items-center space-x-1 active:scale-95 transition-all">
                            <i class="fa-solid fa-play text-[9px]"></i>
                            <span>하이라이트</span>
                        </button>
                    </div>
                </div>
                `;
            }).join("");
        }
    }

    // 0-2) 해외축구 하이라이트 영상 목록 렌더링
    const videoSectionTitle = document.getElementById("overseas-video-section-title");
    if (videoSectionTitle) videoSectionTitle.innerText = `${league.name} 공식 하이라이트 & 골 장면`;

    const hlList = document.getElementById("overseas-highlight-list");
    if (hlList) {
        let highlights = [...(league.highlights || [])];
        highlights.forEach(h => {
            h.isFav = fav && (isTeamMatch(h.title, fav) || isTeamMatch(h.match, fav));
        });

        highlights.sort((a, b) => (b.isFav ? 1 : 0) - (a.isFav ? 1 : 0));

        if (highlights.length > 0) {
            setOverseasDefaultVideo(highlights[0]);
        }

        hlList.innerHTML = `
            <span class="text-xs font-bold text-gray-400 block mb-1">
                ${fav ? `선호 구단 [${fav}] 영상 우선 배치됨 (클릭 시 바로 재생)` : '공식 하이라이트 영상 목록 (클릭 시 바로 재생)'}
            </span>
            ${highlights.map((hl, idx) => `
                <div onclick="playOverseasVideo('${hl.type}', '${hl.video_url || ''}', '${hl.embed_url || ''}', '${escapeHtml(hl.title)}', '${hl.date}')" 
                     class="overseas-hl-card cursor-pointer p-2 rounded-xl border ${hl.isFav ? 'border-amber-400 bg-amber-50/40 dark:bg-amber-950/40 shadow-xs' : 'border-gray-100 dark:border-gray-700/60 bg-white dark:bg-darkbg-800'} hover:bg-blue-50/50 dark:hover:bg-darkbg-700 transition-all flex items-center space-x-3 active:scale-98 group shadow-xs">
                    <div class="relative w-28 h-16 sm:w-32 sm:h-18 rounded-lg overflow-hidden flex-shrink-0 bg-gray-200 dark:bg-gray-800">
                        <img src="${hl.thumbnail}" alt="${hl.title}" class="w-full h-full object-cover group-hover:scale-105 transition-transform" onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=640&auto=format&fit=crop&q=80'">
                        <div class="absolute inset-0 bg-black/30 flex items-center justify-center opacity-80 group-hover:opacity-100 transition-opacity">
                            <span class="w-7 h-7 rounded-full bg-red-600 text-white flex items-center justify-center shadow-md">
                                <i class="fa-solid fa-play text-[10px] ml-0.5"></i>
                            </span>
                        </div>
                    </div>
                    <div class="flex-grow min-w-0">
                        <div class="flex items-center space-x-1 mb-0.5">
                            ${hl.isFav ? `<span class="px-1.5 py-0.2 rounded text-[9px] font-black bg-amber-400 text-amber-950 flex-shrink-0">MY TEAM</span>` : ''}
                            <h4 class="text-xs font-bold text-gray-900 dark:text-white line-clamp-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 leading-snug">
                                ${hl.title}
                            </h4>
                        </div>
                        <div class="flex items-center justify-between text-[11px] text-gray-400 mt-1">
                            <span class="font-medium truncate">${hl.source || '공식 영상'}</span>
                            <span class="ml-1 text-[10px]">${hl.date}</span>
                        </div>
                    </div>
                </div>
            `).join("")}
        `;
    }

    // 1) 테이블 제목
    const tableTitle = document.getElementById("overseas-table-title");
    if (tableTitle) tableTitle.innerText = `🏆 ${league.name} 순위표`;

    // 2) 팀 순위 테이블
    const tbody = document.getElementById("overseas-table-body");
    if (tbody) {
        tbody.innerHTML = (league.teams || []).map(t => {
            const isUcl = t.rank <= 4;
            const isFavTeam = fav && isTeamMatch(t.team, fav);
            return `
            <tr class="hover:bg-blue-50/40 dark:hover:bg-darkbg-700/50 transition-colors ${isFavTeam ? 'bg-amber-50/30 dark:bg-amber-950/20 border-l-4 border-l-amber-500' : (isUcl ? 'border-l-4 border-l-blue-600' : '')}">
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-4 text-center font-bold">
                    <span class="w-5 h-5 sm:w-6 sm:h-6 rounded-full inline-flex items-center justify-center text-[11px] sm:text-xs ${isFavTeam ? 'bg-amber-400 text-amber-950 font-black' : (isUcl ? 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300 font-black' : 'text-gray-500 dark:text-gray-400')}">
                        ${t.rank}
                    </span>
                </td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-4 font-semibold text-gray-900 dark:text-white">
                    <div class="flex items-center space-x-2 sm:space-x-3">
                        ${t.emblem ? `<img src="${t.emblem}" alt="${t.team}" class="w-5 h-5 sm:w-7 sm:h-7 object-contain drop-shadow-sm" onerror="this.style.display='none'">` : ''}
                        <span class="font-bold ${isFavTeam ? 'text-amber-900 dark:text-amber-200' : ''}">${t.team}</span>
                        ${t.teamEng && t.teamEng !== t.team ? `<span class="hidden sm:inline text-xs text-gray-400 font-normal">(${t.teamEng})</span>` : ''}
                        <button type="button" onclick="toggleFavoriteTeam('overseas', '${t.team}', '${currentOverseasSub}')" title="선호 구단 등록/해제" 
                                class="fav-star-btn text-xs ${isFavTeam ? 'text-amber-500 font-black' : 'text-gray-300 hover:text-amber-400'}">
                            ★
                        </button>
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
                    <img src="${cat.first_player.headshot}" alt="${cat.first_player.name}" class="w-14 h-14 rounded-full object-cover border-2 border-indigo-400 bg-white shadow-sm" onerror="this.onerror=null; this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>👤</text></svg>'">
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
            const initialHubTeam = fav && league.teams.find(t => isTeamMatch(t.team, fav)) ? fav : league.teams[0].team;
            renderTeamHubDetails("overseas", initialHubTeam);
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

    const fav = getFavoriteTeam("mlb");

    // 0) 경기 결과 및 하이라이트 영상 렌더링
    renderMlbMatches();
    renderMlbHighlights();

    // 1) 30개 구단 전체 순위표
    const tbody = document.getElementById("mlb-overall-tbody");
    if (tbody) {
        tbody.innerHTML = (mlbData.all_teams || []).map((t, idx) => {
            const isFavTeam = fav && isTeamMatch(t.team, fav);
            return `
            <tr class="hover:bg-blue-50/40 dark:hover:bg-darkbg-700/50 transition-colors ${isFavTeam ? 'bg-amber-50/30 dark:bg-amber-950/20 border-l-4 border-l-amber-500' : (idx < 12 ? 'border-l-4 border-l-blue-500' : '')}">
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-4 text-center font-bold">
                    <span class="w-5 h-5 sm:w-6 sm:h-6 rounded-full inline-flex items-center justify-center text-[11px] sm:text-xs ${isFavTeam ? 'bg-amber-400 text-amber-950 font-black' : (idx < 12 ? 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300 font-bold' : 'text-gray-500')}">
                        ${t.overallRank || idx + 1}
                    </span>
                </td>
                <td class="py-2.5 px-2 sm:py-3.5 sm:px-4 font-semibold text-gray-900 dark:text-white">
                    <div class="flex items-center space-x-2 sm:space-x-3">
                        ${t.emblem ? `<img src="${t.emblem}" alt="${t.team}" class="w-5 h-5 sm:w-7 sm:h-7 object-contain" onerror="this.style.display='none'">` : ''}
                        <span class="font-bold ${isFavTeam ? 'text-amber-900 dark:text-amber-200' : ''}">${t.team}</span>
                        <span class="hidden sm:inline text-xs text-gray-400 font-normal">(${t.teamEng})</span>
                        <button type="button" onclick="toggleFavoriteTeam('mlb', '${t.team}')" title="선호 구단 등록/해제" 
                                class="fav-star-btn text-xs ${isFavTeam ? 'text-amber-500 font-black' : 'text-gray-300 hover:text-amber-400'}">
                            ★
                        </button>
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
            `;
        }).join("");
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
                            ${(d.teams || []).map(t => {
                                const isFavTeam = fav && isTeamMatch(t.team, fav);
                                return `
                                <tr class="hover:bg-gray-50 dark:hover:bg-darkbg-700/50 ${isFavTeam ? 'bg-amber-50/40 dark:bg-amber-950/20 font-bold' : ''}">
                                    <td class="p-2 text-center font-bold ${isFavTeam ? 'text-amber-600 dark:text-amber-400' : 'text-gray-500'}">${t.rank}</td>
                                    <td class="p-2 font-semibold flex items-center space-x-2">
                                        <img src="${t.emblem}" alt="${t.team}" class="w-5 h-5 object-contain" onerror="this.style.display='none'">
                                        <span class="${isFavTeam ? 'text-amber-900 dark:text-amber-200 font-black' : ''}">${t.team}</span>
                                        <button type="button" onclick="toggleFavoriteTeam('mlb', '${t.team}')" title="선호 구단 등록/해제" 
                                                class="fav-star-btn text-xs ${isFavTeam ? 'text-amber-500 font-black' : 'text-gray-300 hover:text-amber-400'} ml-0.5">
                                            ★
                                        </button>
                                    </td>
                                    <td class="p-2 text-center font-bold">${t.win}</td>
                                    <td class="p-2 text-center text-gray-500">${t.loss}</td>
                                    <td class="p-2 text-center font-bold text-blue-600 dark:text-blue-400">${t.rate}</td>
                                    <td class="p-2 text-center text-gray-500">${t.game_diff}</td>
                                </tr>
                                `;
                            }).join("")}
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
            const initialHubTeam = fav && mlbData.all_teams.find(t => isTeamMatch(t.team, fav)) ? fav : mlbData.all_teams[0].team;
            renderTeamHubDetails("mlb", initialHubTeam);
        }
    }
}

// 5-1. MLB 최근 경기 결과 렌더링 (마이팀 연동)
function renderMlbMatches() {
    const mlbData = window.INITIAL_DATA?.mlb;
    const grid = document.getElementById("mlb-matches-grid");
    if (!grid || !mlbData) return;

    const fav = getFavoriteTeam("mlb");
    let matches = [...(mlbData.recent_matches || [])];

    matches.forEach(m => {
        m.isFav = fav && (
            isTeamMatch(m.home_team, fav) ||
            isTeamMatch(m.away_team, fav) ||
            isTeamMatch(m.home_full, fav) ||
            isTeamMatch(m.away_full, fav)
        );
    });

    if (isMyTeamOnlyFilter && fav) {
        matches = matches.filter(m => m.isFav);
    } else {
        matches.sort((a, b) => (b.isFav ? 1 : 0) - (a.isFav ? 1 : 0));
    }

    matches = filterMatchesByStatus(matches);

    if (matches.length === 0) {
        grid.innerHTML = `
            <div class="col-span-full py-10 text-center bg-white dark:bg-darkbg-800 rounded-2xl border border-gray-200 dark:border-gray-800">
                <p class="text-xs sm:text-sm font-bold text-gray-500 dark:text-gray-400">
                    ${isMyTeamOnlyFilter ? `선호 구단 [${fav}]의 해당 조건 경기 일정이 없습니다.` : '해당 조건의 경기 일정이 없습니다.'}
                </p>
                ${(isMyTeamOnlyFilter || currentMatchFilter !== 'all') ? `<button type="button" onclick="setMatchFilter('all'); if (isMyTeamOnlyFilter) toggleMyTeamFilter();" class="mt-3 px-3 py-1.5 rounded-xl bg-blue-50 text-blue-600 dark:bg-blue-950 dark:text-blue-300 text-xs font-bold active:scale-95 transition-all">전체 경기 보기</button>` : ''}
            </div>
        `;
        return;
    }

    grid.innerHTML = matches.map(m => {
        const isLive = m.is_live || m.status === 'LIVE' || (typeof m.status === 'string' && m.status.includes('LIVE'));
        const isFinished = m.is_finished || m.status === '종료';
        const isUpcoming = m.is_upcoming || m.status === '예정';

        let statusBadgeHtml = '';
        if (isLive) {
            statusBadgeHtml = `
                <span class="px-2 py-0.5 rounded text-[10px] font-black bg-red-500 text-white flex items-center space-x-1 shadow-xs animate-pulse">
                    <span class="w-1.5 h-1.5 rounded-full bg-white animate-ping"></span>
                    <span>LIVE ${m.status_info || '진행중'}</span>
                </span>
            `;
        } else if (isFinished) {
            statusBadgeHtml = `
                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-300">
                    종료
                </span>
            `;
        } else {
            statusBadgeHtml = `
                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-700 dark:bg-blue-900/60 dark:text-blue-300">
                    ${m.status_info || '예정'}
                </span>
            `;
        }

        // 투수 정보 박스 (결정투수 / 라이브투수 / 선발예고)
        let pitcherInfoHtml = '';
        if (m.win_pitcher || m.lose_pitcher) {
            pitcherInfoHtml = `
                <div class="px-2.5 py-1.5 rounded-xl bg-gray-50 dark:bg-darkbg-900 border border-gray-100 dark:border-gray-800 text-[11px] mb-2 flex items-center justify-between truncate">
                    <div class="flex items-center space-x-2 truncate">
                        ${m.win_pitcher ? `<span class="text-blue-600 dark:text-blue-400 font-extrabold"><span class="px-1 py-0.2 rounded bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300 text-[9px] mr-1">승</span>${m.win_pitcher}</span>` : ''}
                        ${m.lose_pitcher ? `<span class="text-red-500 dark:text-red-400 font-bold"><span class="px-1 py-0.2 rounded bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300 text-[9px] mr-1">패</span>${m.lose_pitcher}</span>` : ''}
                        ${m.save_pitcher ? `<span class="text-emerald-600 dark:text-emerald-400 font-bold"><span class="px-1 py-0.2 rounded bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 text-[9px] mr-1">세</span>${m.save_pitcher}</span>` : ''}
                    </div>
                    <span class="text-[10px] text-gray-400 ml-1 flex-shrink-0">결정투수</span>
                </div>
            `;
        } else if (isLive && (m.current_pitcher || m.status_info)) {
            pitcherInfoHtml = `
                <div class="px-2.5 py-1.5 rounded-xl bg-red-50/60 dark:bg-red-950/30 border border-red-200/60 dark:border-red-800/40 text-[11px] mb-2 flex items-center justify-between truncate">
                    <span class="font-bold text-red-700 dark:text-red-300 truncate">
                        ${m.current_pitcher ? `<span class="px-1.5 py-0.2 rounded bg-red-500 text-white font-black text-[9px] mr-1">투수</span>${m.current_pitcher}` : '실시간 경기 진행 중'}
                    </span>
                    <span class="text-[10px] text-red-500 font-bold ml-1 flex-shrink-0">${m.status_info || 'LIVE'}</span>
                </div>
            `;
        } else if (isUpcoming && (m.home_starter || m.away_starter || m.starter_note)) {
            pitcherInfoHtml = `
                <div class="px-2.5 py-1.5 rounded-xl bg-blue-50/60 dark:bg-blue-950/30 border border-blue-200/60 dark:border-blue-800/40 text-[11px] mb-2 flex items-center justify-between truncate">
                    <span class="font-bold text-blue-700 dark:text-blue-300 truncate">
                        ${m.starter_note || `선발: ${m.away_starter || '미정'} vs ${m.home_starter || '미정'}`}
                    </span>
                    <span class="text-[10px] text-blue-500 font-bold ml-1 flex-shrink-0">선발예고</span>
                </div>
            `;
        } else if (m.pitcher_note) {
            pitcherInfoHtml = `
                <div class="px-2.5 py-1.5 rounded-xl bg-gray-50 dark:bg-darkbg-900 border border-gray-100 dark:border-gray-800 text-[11px] mb-2 flex items-center justify-between truncate">
                    <span class="font-medium text-gray-600 dark:text-gray-300 truncate">${m.pitcher_note}</span>
                    <span class="text-[10px] text-gray-400 ml-1 flex-shrink-0">경기정보</span>
                </div>
            `;
        }

        const awayScoreDisplay = isUpcoming ? '-' : (m.away_score !== null && m.away_score !== undefined ? m.away_score : '-');
        const homeScoreDisplay = isUpcoming ? '-' : (m.home_score !== null && m.home_score !== undefined ? m.home_score : '-');

        return `
        <div class="bg-white dark:bg-darkbg-800 rounded-2xl border ${isLive ? 'border-red-400 dark:border-red-500 ring-2 ring-red-400/30' : (m.isFav ? 'border-amber-400 dark:border-amber-500 ring-2 ring-amber-400/30 my-team-card' : 'border-gray-200 dark:border-gray-800')} p-3.5 sm:p-4 shadow-sm hover:shadow-md transition-all">
            <div class="flex items-center justify-between pb-2.5 border-b border-gray-100 dark:border-gray-700/60 text-xs">
                <div class="flex items-center space-x-1.5 text-gray-500 dark:text-gray-400 font-medium">
                    <i class="fa-regular fa-calendar text-[11px]"></i>
                    <span>${m.date}</span>
                    ${m.time ? `<span class="text-[10px] text-gray-400">(${m.time})</span>` : ''}
                </div>
                <div class="flex items-center space-x-1.5">
                    ${m.isFav ? `
                    <span class="px-1.5 py-0.2 rounded text-[10px] font-black bg-amber-400 text-amber-950 shadow-xs flex items-center space-x-1">
                        <i class="fa-solid fa-star text-[9px]"></i><span>MY TEAM</span>
                    </span>
                    ` : ''}
                    ${statusBadgeHtml}
                </div>
            </div>
            <div class="py-3 space-y-2">
                <!-- 원정팀 -->
                <div class="flex items-center justify-between ${m.away_win ? 'font-black text-gray-900 dark:text-white' : 'text-gray-500 dark:text-gray-400'}">
                    <div class="flex items-center space-x-2.5 truncate">
                        ${m.away_emblem ? `<img src="${m.away_emblem}" alt="${m.away_team}" class="w-6 h-6 object-contain" onerror="this.style.display='none'">` : ''}
                        <span class="text-xs sm:text-sm truncate font-semibold">${m.away_full || m.away_team}</span>
                        ${m.away_win ? `<span class="px-1.5 py-0.2 rounded text-[10px] font-bold bg-blue-100 text-blue-700 dark:bg-blue-900/60 dark:text-blue-300">승</span>` : ''}
                        <button type="button" onclick="toggleFavoriteTeam('mlb', '${m.away_team}')" title="선호 구단 등록/해제" 
                                class="fav-star-btn text-xs ${fav && isTeamMatch(m.away_team, fav) ? 'text-amber-500 font-black' : 'text-gray-300 hover:text-amber-400'} ml-0.5">
                            ★
                        </button>
                    </div>
                    <span class="text-base sm:text-lg ${m.away_win ? 'text-blue-600 dark:text-blue-400 font-black' : (isLive ? 'text-red-600 dark:text-red-400 font-black' : '')}">${awayScoreDisplay}</span>
                </div>
                <!-- 홈팀 -->
                <div class="flex items-center justify-between ${m.home_win ? 'font-black text-gray-900 dark:text-white' : 'text-gray-500 dark:text-gray-400'}">
                    <div class="flex items-center space-x-2.5 truncate">
                        ${m.home_emblem ? `<img src="${m.home_emblem}" alt="${m.home_team}" class="w-6 h-6 object-contain" onerror="this.style.display='none'">` : ''}
                        <span class="text-xs sm:text-sm truncate font-semibold">${m.home_full || m.home_team}</span>
                        ${m.home_win ? `<span class="px-1.5 py-0.2 rounded text-[10px] font-bold bg-blue-100 text-blue-700 dark:bg-blue-900/60 dark:text-blue-300">승</span>` : ''}
                        <button type="button" onclick="toggleFavoriteTeam('mlb', '${m.home_team}')" title="선호 구단 등록/해제" 
                                class="fav-star-btn text-xs ${fav && isTeamMatch(m.home_team, fav) ? 'text-amber-500 font-black' : 'text-gray-300 hover:text-amber-400'} ml-0.5">
                            ★
                        </button>
                    </div>
                    <span class="text-base sm:text-lg ${m.home_win ? 'text-blue-600 dark:text-blue-400 font-black' : (isLive ? 'text-red-600 dark:text-red-400 font-black' : '')}">${homeScoreDisplay}</span>
                </div>
            </div>
            ${pitcherInfoHtml}
            <div class="pt-2 border-t border-gray-100 dark:border-gray-700/60 flex items-center justify-between text-[11px]">
                <span class="text-gray-400 truncate">${m.venue || '경기장'}</span>
                <button type="button" onclick="focusMlbHighlight('${m.away_team}', '${m.home_team}')" 
                        class="px-2.5 py-1 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-600 dark:bg-blue-950/60 dark:hover:bg-blue-900/80 dark:text-blue-300 font-bold flex items-center space-x-1 active:scale-95 transition-all">
                    <i class="fa-solid fa-play text-[9px]"></i>
                    <span>하이라이트</span>
                </button>
            </div>
        </div>
        `;
    }).join("");
}

// 5-2. MLB 하이라이트 영상 목록 렌더링 (마이팀 연동)
function renderMlbHighlights() {
    const mlbData = window.INITIAL_DATA?.mlb;
    const hlList = document.getElementById("mlb-highlight-list");
    if (!hlList || !mlbData) return;

    const fav = getFavoriteTeam("mlb");
    let highlights = [...(mlbData.highlights || [])];

    highlights.forEach(h => {
        h.isFav = fav && (isTeamMatch(h.title, fav) || isTeamMatch(h.match, fav));
    });

    highlights.sort((a, b) => (b.isFav ? 1 : 0) - (a.isFav ? 1 : 0));

    // 선호 구단 영상이 1순위로 있으면 상단 플레이어에 해당 영상 기본 세팅
    // 선호 구단 영상이 1순위로 있으면 상단 플레이어 프리뷰에 해당 영상 세팅
    if (highlights.length > 0 && highlights[0].isFav) {
        const player = document.getElementById("mlb-video-player");
        const thumbEl = document.getElementById("mlb-facade-thumb");
        const titleEl = document.getElementById("mlb-current-video-title");
        const dateEl = document.getElementById("mlb-current-video-date");
        const tagEl = document.getElementById("mlb-current-video-tag");
        if (player && highlights[0].video_url) {
            player.dataset.src = highlights[0].video_url;
        }
        if (thumbEl && highlights[0].thumbnail) {
            thumbEl.src = highlights[0].thumbnail;
        }
        if (titleEl) titleEl.innerText = highlights[0].title;
        if (dateEl) dateEl.innerText = highlights[0].date;
        if (tagEl) tagEl.innerText = `★ ${fav} 공식 영상`;
    }

    hlList.innerHTML = `
        <span class="text-xs font-bold text-gray-400 block mb-1">
            ${fav ? `선호 구단 [${fav}] 영상 우선 배치됨 (클릭 시 바로 재생)` : '최신 하이라이트 영상 목록 (클릭 시 바로 재생)'}
        </span>
        ${highlights.map(hl => `
            <div onclick="playMlbVideo('${hl.video_url}', '${escapeHtml(hl.title)}', '${hl.date}')" 
                 class="mlb-hl-card cursor-pointer p-2 rounded-xl border ${hl.isFav ? 'border-amber-400 bg-amber-50/40 dark:bg-amber-950/40 shadow-xs' : 'border-gray-100 dark:border-gray-700/60 bg-white dark:bg-darkbg-800'} hover:bg-blue-50/50 dark:hover:bg-darkbg-700 transition-all flex items-center space-x-3 active:scale-98 group shadow-xs">
                <div class="relative w-28 h-16 sm:w-32 sm:h-18 rounded-lg overflow-hidden flex-shrink-0 bg-gray-200 dark:bg-gray-800">
                    <img src="${hl.thumbnail}" alt="${hl.title}" class="w-full h-full object-cover group-hover:scale-105 transition-transform" onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1508344928928-7165b67de128?w=640&auto=format&fit=crop&q=80'">
                    <div class="absolute inset-0 bg-black/30 flex items-center justify-center opacity-80 group-hover:opacity-100 transition-opacity">
                        <span class="w-7 h-7 rounded-full bg-red-600 text-white flex items-center justify-center shadow-md">
                            <i class="fa-solid fa-play text-[10px] ml-0.5"></i>
                        </span>
                    </div>
                </div>
                <div class="flex-grow min-w-0">
                    <div class="flex items-center space-x-1 mb-0.5">
                        ${hl.isFav ? `<span class="px-1.5 py-0.2 rounded text-[9px] font-black bg-amber-400 text-amber-950 flex-shrink-0">MY TEAM</span>` : ''}
                        <h4 class="text-xs font-bold text-gray-900 dark:text-white line-clamp-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 leading-snug">
                            ${hl.title}
                        </h4>
                    </div>
                    <div class="flex items-center justify-between text-[11px] text-gray-400 mt-1">
                        <span class="font-medium truncate">${hl.duration || '하이라이트'}</span>
                        <span class="ml-1 text-[10px]">${hl.date}</span>
                    </div>
                </div>
            </div>
        `).join("")}
    `;
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

// ========================================================
// 10. 공식 영상 플레이어 제어 및 경기 하이라이트 포커스
// ========================================================
function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// ========================================================
// 비디오 재생 및 스마트 지연 로딩 (Facade) 로직
// ========================================================

// 1-1) KBO 메인 비디오 재생 시작 (Facade 클릭 시)
function startKboMainVideo() {
    const frame = document.getElementById("kbo-video-frame");
    const facade = document.getElementById("kbo-video-facade");
    if (!frame) return;
    const url = frame.dataset.src || "https://www.youtube.com/embed/jNN3rRIK9LE";
    const autoplayUrl = url.includes("?") ? `${url}&autoplay=1` : `${url}?autoplay=1`;
    frame.src = autoplayUrl;
    frame.classList.remove("hidden");
    if (facade) facade.classList.add("hidden");
}

// 1-2) KBO 영상 선택 재생
function playKboVideo(embedUrl, title, date) {
    const frame = document.getElementById("kbo-video-frame");
    const facade = document.getElementById("kbo-video-facade");
    if (!frame || !embedUrl) return;

    frame.dataset.src = embedUrl;
    const autoplayUrl = embedUrl.includes("?") ? `${embedUrl}&autoplay=1` : `${embedUrl}?autoplay=1`;
    frame.src = autoplayUrl;
    frame.classList.remove("hidden");
    if (facade) facade.classList.add("hidden");

    const titleEl = document.getElementById("kbo-current-video-title");
    if (titleEl) titleEl.innerText = title || "KBO 공식 하이라이트";

    const dateEl = document.getElementById("kbo-current-video-date");
    if (dateEl) dateEl.innerText = date || "";

    showToast(`🎬 ${title} 재생 중`);
    frame.scrollIntoView({ behavior: "smooth", block: "center" });
}

// 2-1) K리그 메인 비디오 재생 시작 (Facade 클릭 시)
function startKleagueMainVideo() {
    const frame = document.getElementById("kleague-video-frame");
    const facade = document.getElementById("kleague-video-facade");
    if (!frame) return;
    const url = frame.dataset.src || "https://www.youtube.com/embed/QHq4QJ_R0E0";
    const autoplayUrl = url.includes("?") ? `${url}&autoplay=1` : `${url}?autoplay=1`;
    frame.src = autoplayUrl;
    frame.classList.remove("hidden");
    if (facade) facade.classList.add("hidden");
}

// 2-2) K리그 영상 선택 재생
function playKleagueVideo(embedUrl, title, date) {
    const frame = document.getElementById("kleague-video-frame");
    const facade = document.getElementById("kleague-video-facade");
    if (!frame || !embedUrl) return;

    frame.dataset.src = embedUrl;
    const autoplayUrl = embedUrl.includes("?") ? `${embedUrl}&autoplay=1` : `${embedUrl}?autoplay=1`;
    frame.src = autoplayUrl;
    frame.classList.remove("hidden");
    if (facade) facade.classList.add("hidden");

    const titleEl = document.getElementById("kleague-current-video-title");
    if (titleEl) titleEl.innerText = title || "K리그 공식 하이라이트";

    const dateEl = document.getElementById("kleague-current-video-date");
    if (dateEl) dateEl.innerText = date || "";

    showToast(`🎬 ${title} 재생 중`);
    frame.scrollIntoView({ behavior: "smooth", block: "center" });
}

// 3-1) 해외축구 메인 비디오 재생 시작 (Facade 클릭 시)
function startOverseasMainVideo() {
    const facade = document.getElementById("overseas-video-facade");
    const videoPlayer = document.getElementById("overseas-video-player");
    const videoFrame = document.getElementById("overseas-video-frame");
    if (facade) facade.classList.add("hidden");
    if (videoPlayer && videoPlayer.dataset.src) {
        videoPlayer.src = videoPlayer.dataset.src;
        videoPlayer.classList.remove("hidden");
        videoPlayer.play().catch(() => {});
    } else if (videoFrame && videoFrame.dataset.src) {
        const url = videoFrame.dataset.src;
        videoFrame.src = url.includes("?") ? `${url}&autoplay=1` : `${url}?autoplay=1`;
        videoFrame.classList.remove("hidden");
    }
}

// 3-2) 해외축구 기본 비디오 프리뷰 설정
function setOverseasDefaultVideo(hl) {
    if (!hl) return;
    const videoPlayer = document.getElementById("overseas-video-player");
    const videoFrame = document.getElementById("overseas-video-frame");
    const facadeThumb = document.getElementById("overseas-facade-thumb");
    const facade = document.getElementById("overseas-video-facade");
    if (!videoPlayer || !videoFrame) return;

    const titleEl = document.getElementById("overseas-current-video-title");
    if (titleEl) titleEl.innerText = hl.title || "해외축구 공식 하이라이트";

    const dateEl = document.getElementById("overseas-current-video-date");
    if (dateEl) dateEl.innerText = hl.date || "";

    const tagEl = document.getElementById("overseas-current-video-tag");
    if (tagEl) tagEl.innerText = hl.source || "공식 영상";

    if (facadeThumb && hl.thumbnail) {
        facadeThumb.src = hl.thumbnail;
    }
    if (facade) facade.classList.remove("hidden");

    if (hl.type === "mp4" && hl.video_url) {
        videoPlayer.dataset.src = hl.video_url;
        videoPlayer.src = "";
        videoPlayer.classList.add("hidden");
        videoFrame.classList.add("hidden");
        videoFrame.src = "";
    } else if (hl.embed_url) {
        videoFrame.dataset.src = hl.embed_url;
        videoFrame.src = "";
        videoFrame.classList.add("hidden");
        videoPlayer.classList.add("hidden");
        videoPlayer.src = "";
    }
}

// 3-3) 해외축구 영상 선택 재생
function playOverseasVideo(type, videoUrl, embedUrl, title, date) {
    const facade = document.getElementById("overseas-video-facade");
    const videoPlayer = document.getElementById("overseas-video-player");
    const videoFrame = document.getElementById("overseas-video-frame");
    if (!videoPlayer || !videoFrame) return;

    if (facade) facade.classList.add("hidden");

    const titleEl = document.getElementById("overseas-current-video-title");
    if (titleEl) titleEl.innerText = title || "해외축구 공식 하이라이트";

    const dateEl = document.getElementById("overseas-current-video-date");
    if (dateEl) dateEl.innerText = date || "";

    if (type === "mp4" && videoUrl) {
        videoPlayer.src = videoUrl;
        videoPlayer.classList.remove("hidden");
        videoFrame.classList.add("hidden");
        videoFrame.src = "";
        videoPlayer.play().catch(() => {});
        videoPlayer.scrollIntoView({ behavior: "smooth", block: "center" });
    } else if (embedUrl) {
        const autoplayUrl = embedUrl.includes("?") ? `${embedUrl}&autoplay=1` : `${embedUrl}?autoplay=1`;
        videoFrame.src = autoplayUrl;
        videoFrame.classList.remove("hidden");
        videoPlayer.classList.add("hidden");
        videoPlayer.src = "";
        videoFrame.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    showToast(`🎬 ${title} 재생 중`);
}

// 4-1) MLB 메인 비디오 재생 시작 (Facade 클릭 시)
function startMlbMainVideo() {
    const player = document.getElementById("mlb-video-player");
    const facade = document.getElementById("mlb-video-facade");
    if (!player) return;
    if (facade) facade.classList.add("hidden");
    const url = player.dataset.src;
    if (url) {
        player.src = url;
    }
    player.classList.remove("hidden");
    player.play().catch(() => {});
}

// 4-2) MLB 영상 선택 재생 (mp4 고화질 재생)
function playMlbVideo(videoUrl, title, date) {
    const player = document.getElementById("mlb-video-player");
    const facade = document.getElementById("mlb-video-facade");
    if (!player || !videoUrl) return;

    if (facade) facade.classList.add("hidden");
    player.src = videoUrl;
    player.classList.remove("hidden");
    player.play().catch(() => {});

    const titleEl = document.getElementById("mlb-current-video-title");
    if (titleEl) titleEl.innerText = title || "MLB Film Room 하이라이트";

    const dateEl = document.getElementById("mlb-current-video-date");
    if (dateEl) dateEl.innerText = date || "";

    showToast(`🎬 ${title} 재생 중`);
    player.scrollIntoView({ behavior: "smooth", block: "center" });
}

// 6) 경기 카드에서 하이라이트 포커스
function focusKboHighlight(t1, t2) {
    const kboData = window.INITIAL_DATA?.kbo;
    const highlights = kboData?.highlights || [];
    let match = highlights.find(h => (h.match && (h.match.includes(t1) || h.match.includes(t2))) || (h.title && (h.title.includes(t1) || h.title.includes(t2))));
    if (!match && highlights.length > 0) match = highlights[0];

    if (match) {
        playKboVideo(match.embed_url, match.title, match.date);
    } else {
        showToast("해당 경기의 영상이 준비 중입니다.");
    }
}

function focusKleagueHighlight(home, away) {
    const klData = window.INITIAL_DATA?.kleague;
    const subData = klData?.[currentKLeagueSub];
    const highlights = subData?.highlights || klData?.highlights || [];
    let match = highlights.find(h => (h.title && (isTeamMatch(h.title, home) || isTeamMatch(h.title, away))));
    if (!match && highlights.length > 0) match = highlights[0];

    if (match) {
        playKleagueVideo(match.embed_url, match.title, match.date);
    } else {
        showToast("해당 경기의 영상이 준비 중입니다.");
    }
}

function focusOverseasHighlight(home, away) {
    const socData = window.INITIAL_DATA?.overseas;
    const league = socData?.leagues ? socData.leagues[currentOverseasSub] : null;
    const highlights = league?.highlights || [];
    let match = highlights.find(h => (h.match && (h.match.includes(home) || h.match.includes(away))) || (h.title && (h.title.includes(home) || h.title.includes(away))));
    if (!match && highlights.length > 0) match = highlights[0];

    if (match) {
        playOverseasVideo(match.type, match.video_url, match.embed_url, match.title, match.date);
    } else {
        showToast("해당 경기의 영상이 준비 중입니다.");
    }
}

function focusMlbHighlight(t1, t2) {
    const mlbData = window.INITIAL_DATA?.mlb;
    const highlights = mlbData?.highlights || [];
    let match = highlights.find(h => (h.match && (h.match.includes(t1) || h.match.includes(t2))) || (h.title && (h.title.includes(t1) || h.title.includes(t2))));
    if (!match && highlights.length > 0) match = highlights[0];

    if (match) {
        playMlbVideo(match.video_url, match.title, match.date);
    } else {
        showToast("해당 경기의 영상이 준비 중입니다.");
    }
}
