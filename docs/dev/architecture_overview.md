# 🛠️ 개발 아키텍처 및 구현 가이드 (Architecture Overview)

## 1. 🏗️ 기술 스택 및 구조 (Tech Stack)
- **프론트엔드**: Vite + Vanilla JS (또는 React) + Vanilla CSS (Apex 다크 테마 토큰 기반)
- **데이터 소스**: [data/weapons_data.json](file:///c:/Dev/Apex/data/weapons_data.json) (정적 로드 또는 추후 로컬 API 서빙)
- **파이프라인**: Python 3.12 (`scripts/apex_crawler.py`, `scripts/upload_to_sheets.py`)

---

## 2. 🗂️ 프론트엔드 권장 디렉토리 구조
```text
frontend/ (또는 web/)
├── index.html
├── src/
│   ├── components/      # UI 컴포넌트 (WeaponCard, FilterBar, TtkSimulator)
│   ├── utils/           # 💡 순수 비즈니스 로직 (UI와 완전 격리)
│   │   ├── calculator.js    # TTK, DPS, One-mag kill 공식
│   │   └── formatters.js    # 숫자, 초 단위 포맷터
│   ├── styles/          # 디자인 시스템 및 테마 토큰
│   │   ├── variables.css    # Apex 다크 테마 색상, 폰트 변수
│   │   └── main.css
│   └── main.js          # 엔트리포인트 및 상태 바인딩
```

---

## 3. 📐 핵심 계산 공식 (Pure Logic Specification)

### 1) Shots to Kill (처치 필요 탄환 수)
```javascript
// Target_HP: 방어구 티어에 따른 총 체력 (예: 퍼플 = 100 기본 HP + 100 실드 = 200)
// damage: 1발당 데미지 (기본 dmg_body)
const shotsToKill = Math.ceil(targetHp / damage);
```

### 2) Time to Kill (TTK, 초 단위)
첫 발은 조작 즉시 발사(0초)되므로, 발사 간격은 `(필요 탄환 수 - 1)` 번 발생합니다:
```javascript
// RPM: 분당 발사 속도
// 발사 간 딜레이(초) = 60 / RPM
if (shotsToKill <= 1) {
  return 0.0; // 단발 킬 (예: 크레이버 헤드샷)
}
const timeBetweenShots = 60.0 / rpm;
const ttk = (shotsToKill - 1) * timeBetweenShots;
```

### 3) One-Mag Kill 가능 여부
```javascript
const isOneMagKill = magazineCapacity >= shotsToKill;
```
*(위 함수들은 `src/utils/calculator.js`에 독립 순수 함수로 작성되어, 단위 테스트 및 TC 자동 설계 도구에서 직접 import하여 100% 자동 검증할 수 있도록 유지합니다.)*
