/**
 * Apex Info - Frontend Application Logic (app.js)
 * SPA Navigation, Real-time Weapons Dex Data Loading, Filtering & Live Timer
 */

// State
let allWeapons = [];
let currentClassFilter = 'ALL';
let currentAmmoFilter = 'ALL';
let currentSearchQuery = '';

// Route Definitions (URL Hash <-> Section ID Mapping)
const ROUTE_MAP = {
  'home': 'view-home',
  'weapons': 'view-weapons',
  'legends': 'view-legends',
  'maps': 'view-maps',
  'calculator': 'view-calculator',
  'tierlist': 'view-tierlist'
};

const TARGET_TO_ROUTE = {
  'view-home': 'home',
  'view-weapons': 'weapons',
  'view-legends': 'legends',
  'view-maps': 'maps',
  'view-calculator': 'calculator',
  'view-tierlist': 'tierlist'
};

// Ammo Badge Configuration (variables.css 1:1 Mapping & Fallback)
const AMMO_BADGE_CONFIG = [
  { key: 'mythic', className: 'badge-ammo-mythic' },
  { key: 'light', className: 'badge-ammo-light' },
  { key: 'heavy', className: 'badge-ammo-heavy' },
  { key: 'energy', className: 'badge-ammo-energy' },
  { key: 'sniper', className: 'badge-ammo-sniper' },
  { key: 'shotgun', className: 'badge-ammo-shotgun' }
];

document.addEventListener('DOMContentLoaded', () => {
  initRouter();
  initNavigation();
  initPortalLinks();
  initLiveTimer();
  loadWeaponsData();
  initFilterControls();
});

/* =============================================================================
   1. URL Hash Router & History Management
   ============================================================================= */
function initRouter() {
  window.addEventListener('hashchange', handleHashChange);
  handleHashChange();
}

function handleHashChange() {
  const hash = window.location.hash.replace(/^#/, '').toLowerCase().trim();
  const targetId = ROUTE_MAP[hash] || 'view-home';
  switchTab(targetId, false);
}

function navigateTo(route) {
  const cleanRoute = (route || 'home').toLowerCase().trim();
  if (window.location.hash !== `#${cleanRoute}`) {
    window.location.hash = cleanRoute;
  } else {
    handleHashChange();
  }
}

/* =============================================================================
   2. GNB Navigation & Tab Switching
   ============================================================================= */
function initNavigation() {
  const tabs = document.querySelectorAll('.nav-tab');

  tabs.forEach(tab => {
    tab.addEventListener('click', (e) => {
      e.preventDefault();
      const route = tab.getAttribute('data-route') || TARGET_TO_ROUTE[tab.getAttribute('data-target')] || 'home';
      navigateTo(route);
    });
  });

  // Brand Logo Click -> Navigate to #home
  const brandLogo = document.getElementById('brand-logo');
  if (brandLogo) {
    brandLogo.addEventListener('click', (e) => {
      e.preventDefault();
      navigateTo('home');
    });
  }
}

function switchTab(targetId, updateHash = false) {
  const tabs = document.querySelectorAll('.nav-tab');
  const sections = document.querySelectorAll('.view-section');

  // Update tabs active state
  tabs.forEach(t => {
    if (t.getAttribute('data-target') === targetId) {
      t.classList.add('active');
    } else {
      t.classList.remove('active');
    }
  });

  // Update sections visibility
  sections.forEach(sec => {
    if (sec.id === targetId) {
      sec.classList.remove('hidden');
    } else {
      sec.classList.add('hidden');
    }
  });

  if (updateHash) {
    const route = TARGET_TO_ROUTE[targetId] || 'home';
    if (window.location.hash !== `#${route}`) {
      window.location.hash = route;
    }
  }

  // Scroll to top smoothly
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

/* =============================================================================
   3. Home Portal Links
   ============================================================================= */
function initPortalLinks() {
  const portalWeapons = document.getElementById('portal-weapons');
  const portalLegends = document.getElementById('portal-legends');
  const portalCalc = document.getElementById('portal-calculator');
  const btnQuickMap = document.getElementById('btn-quick-map');

  if (portalWeapons) portalWeapons.addEventListener('click', () => navigateTo('weapons'));
  if (portalLegends) portalLegends.addEventListener('click', () => navigateTo('legends'));
  if (portalCalc) portalCalc.addEventListener('click', () => navigateTo('calculator'));
  if (btnQuickMap) btnQuickMap.addEventListener('click', () => navigateTo('maps'));
}

/* =============================================================================
   4. Live Map Rotation Timer Simulation
   ============================================================================= */
function initLiveTimer() {
  let secondsRemaining = 24 * 60 + 15; // 24m 15s initial
  const tickerEl = document.getElementById('home-ticker-map');

  if (!tickerEl) return;

  setInterval(() => {
    if (secondsRemaining > 0) {
      secondsRemaining--;
      const m = Math.floor(secondsRemaining / 60).toString().padStart(2, '0');
      const s = (secondsRemaining % 60).toString().padStart(2, '0');
      tickerEl.textContent = `올림푸스 (배틀로얄) · 남은 시간 00:${m}:${s}`;
    } else {
      secondsRemaining = 90 * 60; // reset to 1h 30m for next map
      tickerEl.textContent = `세상의 끝 (배틀로얄) · 방금 시작됨`;
    }
  }, 1000);
}

/* =============================================================================
   5. Weapons Data Loading & Rendering (with Cache Busting ?v=)
   ============================================================================= */
async function loadWeaponsData() {
  const gridContainer = document.getElementById('weapons-grid-container');
  if (!gridContainer) return;

  gridContainer.innerHTML = `
    <div style="grid-column: 1 / -1; padding: 3rem; text-align: center; color: var(--text-secondary);">
      <div class="pulse-dot" style="margin: 0 auto 1rem; width: 16px; height: 16px;"></div>
      <p style="font-family: var(--font-display); font-size: 1.25rem;">무기 데이터베이스 로드 중...</p>
    </div>
  `;

  try {
    const cacheBuster = `v=${Date.now()}`;
    const response = await fetch(`./data/weapons_data.json?${cacheBuster}`);
    if (!response.ok) {
      throw new Error(`HTTP Error: ${response.status}`);
    }
    allWeapons = await response.json();
    renderWeaponsList();
  } catch (error) {
    console.error('Failed to load weapons_data.json:', error);
    gridContainer.innerHTML = `
      <div style="grid-column: 1 / -1; padding: 3rem; text-align: center; color: var(--accent-red);">
        <p style="font-family: var(--font-display); font-size: 1.25rem;">데이터 로드 실패: ${error.message}</p>
        <p style="font-size: 0.9rem; color: var(--text-muted); margin-top: 0.5rem;">data/weapons_data.json 파일을 확인하세요.</p>
      </div>
    `;
  }
}

function renderWeaponsList() {
  const gridContainer = document.getElementById('weapons-grid-container');
  const countEl = document.getElementById('weapon-count');
  if (!gridContainer) return;

  // Filter
  const filtered = allWeapons.filter(w => {
    // Class filter
    if (currentClassFilter !== 'ALL') {
      if ((w.type || '').toUpperCase() !== currentClassFilter.toUpperCase()) {
        return false;
      }
    }
    // Ammo filter
    if (currentAmmoFilter !== 'ALL') {
      const ammoStr = (w.ammo || '').toLowerCase();
      if (!ammoStr.includes(currentAmmoFilter.toLowerCase())) {
        return false;
      }
    }
    // Search query
    if (currentSearchQuery) {
      const q = currentSearchQuery.toLowerCase();
      const nameEn = (w.name || '').toLowerCase();
      const nameKo = (w.name_kor || '').toLowerCase();
      if (!nameEn.includes(q) && !nameKo.includes(q)) {
        return false;
      }
    }
    return true;
  });

  if (countEl) {
    countEl.textContent = `${filtered.length}개 총기 표시 중 (전체 ${allWeapons.length}개)`;
  }

  if (filtered.length === 0) {
    gridContainer.innerHTML = `
      <div style="grid-column: 1 / -1; padding: 4rem; text-align: center; color: var(--text-muted);">
        <p style="font-family: var(--font-display); font-size: 1.5rem;">조건에 맞는 총기가 없습니다.</p>
        <p style="font-size: 0.95rem; margin-top: 0.5rem;">필터 조건을 변경하거나 검색어를 지워보세요.</p>
      </div>
    `;
    return;
  }

  gridContainer.innerHTML = filtered.map(w => createWeaponCardHTML(w)).join('');
}

function createWeaponCardHTML(w) {
  // Format ammo badge color
  const ammoClass = getAmmoClass(w.ammo);
  const ammoName = cleanAmmoName(w.ammo);

  // Mags info
  const mag0 = w.mag_0 && w.mag_0 !== '-' ? w.mag_0 : '-';
  const mag3 = w.mag_3 && w.mag_3 !== '-' ? w.mag_3 : (w.mag_1 || mag0);
  const magDisplay = (mag0 === mag3 || mag3 === '-') ? `${mag0}발` : `${mag0} ~ ${mag3}발`;

  return `
    <article class="weapon-card" data-name="${escapeHtml(w.name)}">
      <div>
        <div class="weapon-header">
          <div class="weapon-name-wrap">
            <span class="weapon-name-ko">${escapeHtml(w.name_kor || w.name)}</span>
            <span class="weapon-name-en">${escapeHtml(w.name)}</span>
          </div>
          <div class="weapon-badges">
            <span class="badge badge-class">${escapeHtml(w.type || 'ETC')}</span>
            <span class="badge ${ammoClass}">${escapeHtml(ammoName)}</span>
          </div>
        </div>

        <div class="weapon-stats-grid">
          <div class="stat-box">
            <span class="stat-label">HEAD</span>
            <span class="stat-val dmg-head">${w.dmg_head || '-'}</span>
          </div>
          <div class="stat-box">
            <span class="stat-label">BODY</span>
            <span class="stat-val dmg-body">${w.dmg_body || w.dmg || '-'}</span>
          </div>
          <div class="stat-box">
            <span class="stat-label">LEG</span>
            <span class="stat-val dmg-leg">${w.dmg_leg || '-'}</span>
          </div>
        </div>
      </div>

      <div class="weapon-footer">
        <div>
          <span>RPM: <strong>${w.RPM || '-'}</strong></span>
          <span style="margin: 0 0.5rem; opacity: 0.3;">|</span>
          <span>DPS: <strong>${w.DPS || '-'}</strong></span>
        </div>
        <div class="mag-info">
          탄창: <strong>${magDisplay}</strong>
        </div>
      </div>
    </article>
  `;
}

function getAmmoClass(ammo) {
  if (!ammo || typeof ammo !== 'string') return 'badge-ammo-default';
  const normalized = ammo.toLowerCase().trim();
  const matched = AMMO_BADGE_CONFIG.find(item => normalized.includes(item.key));
  return matched ? matched.className : 'badge-ammo-default';
}

function cleanAmmoName(ammo) {
  if (!ammo) return '탄약';
  return ammo
    .replace('.svg', '')
    .replace(' Rounds', '')
    .replace(' Ammo', '')
    .replace('Shells', '')
    .trim();
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/* =============================================================================
   5. Filter & Search Controls
   ============================================================================= */
function initFilterControls() {
  const filterBtns = document.querySelectorAll('.filter-btn');
  const searchInput = document.getElementById('weapon-search');

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const type = btn.getAttribute('data-filter-type');
      const val = btn.getAttribute('data-value');

      // Update active state in group
      const siblingBtns = btn.parentElement.querySelectorAll('.filter-btn');
      siblingBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      if (type === 'class') {
        currentClassFilter = val;
      } else if (type === 'ammo') {
        currentAmmoFilter = val;
      }

      renderWeaponsList();
    });
  });

  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      currentSearchQuery = e.target.value.trim();
      renderWeaponsList();
    });
  }
}
