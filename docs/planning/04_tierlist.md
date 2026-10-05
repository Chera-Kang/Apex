# 🏆 [기능 4] 티어리스트 명세서 (Tier List Specification)

> **문서 ID**: `SPEC-004`  
> **상태**: `v1.0 개발 예정 (In-Progress) / v1.4 대기 (Backlog)`  
> **단일 문서 원칙(Living Document)**: 시즌 메타 기반 무기/레전드 티어표 시각화 및 향후 유저 커스텀 티어 메이커 기능의 기획, 데이터 구조, 검증 기준을 단일 파일로 관리합니다.

---

## 📌 기능 버전 및 진행 현황 (Version Tracker)

| 버전 | 구분 | 목표 | 상태 | 주요 반영 사항 |
| :---: | :---: | :--- | :---: | :--- |
| **v1.0** | MVP | 시즌 메타 무기/레전드 티어표 시각화 | ⏳ 진행 중 (In-Progress) | S, A, B, C, D 티어별 무기/레전드 카드 렌더링 및 메타 선정 이유 요약 |
| **v1.4** | 확장 | 유저 커스텀 드래그 & 드롭 티어 메이커 | ⏳ 예정 (Backlog) | 드래그 & 드롭으로 나만의 티어표 편집 및 고화질 PNG 이미지 저장 기능 |

---

## 1. 📋 기획 (Planning : Why & UI Flow)

### 1) 왜 필요한가? (User Value)
- 플레이어들이 가장 관심 있어 하고 토론하기 좋아하는 콘텐츠는 **"지금 시즌엔 어떤 총과 레전드가 1티어(S티어)인가?"**입니다.
- 시즌 및 스플릿 패치에 따라 실시간으로 변하는 무기와 레전드의 티어(S~D)를 시각적인 인게임 감성 카드로 명쾌하게 보여줍니다.

### 2) 화면 구성 및 인터랙션 흐름 (UI Flow)
1. **GNB 진입**: 상단 `[ 티어표 ]` 탭 클릭 또는 URL `#tierlist` 직접 접근.
2. **카테고리 전환**:
   - `[ 무기 티어표 ]` / `[ 레전드 티어표 ]` 탭 제공.
3. **티어 행(Tier Rows) 레이아웃**:
   - **S TIER (Apex Red / Gold)**: 현 메타 압도적 1티어 (예: 하복, R-99 보급, 레이스, 패스파인더)
   - **A TIER (Energy Orange)**: 준수한 성능의 주력 선택지 (예: 플랫라인, 볼트, 방갈로르)
   - **B TIER (Shield Blue)**: 상황에 따라 유효한 표준 선택지
   - **C TIER (Slate)**: 특정 조건에서만 쓰이는 비주류
   - **D TIER (Muted)**: 상향이 필요한 하위권
4. **티어별 한 줄 코멘트**: 각 무기/레전드 카드 호버 시 "현재 왜 이 티어인가?" 핵심 이유 툴팁 제공.

---

## 2. ⚙️ 개발 (Dev : Data & Implementation)

### 1) 데이터 저장 구조 ([data/tierlist_data.json](file:///c:/Dev/Apex/data/tierlist_data.json))
```json
{
  "season": "Season 24",
  "weapons_tier": {
    "S": ["HAVOC Rifle", "R-99 SMG", "Kraber .50-Cal Sniper"],
    "A": ["VK-47 Flatline", "Volt SMG", "Hemlok Burst AR", "Peacekeeper"],
    "B": ["R-301 Carbine", "Alternator SMG", "G7 Scout", "EVA-8 Auto"],
    "C": ["P2020", "RE-45 Auto", "Longbow DMR"],
    "D": ["Charge Rifle"]
  },
  "tier_comments": {
    "HAVOC Rifle": "터보차저 장착 시 압도적인 근/중거리 DPS 자랑",
    "R-99 SMG": "케어 패키지 보급 무기로 승격되며 파괴적인 성능 복구"
  }
}
```

### 2) 프론트엔드 연동
- [data/weapons_data.json](file:///c:/Dev/Apex/data/weapons_data.json)과 매핑하여 해당 무기의 탄약 뱃지, 한글명, 데미지 스펙을 티어 카드에 자동으로 바인딩.

---

## 3. ✅ 검증 및 완료 기준 (Verification & DoD)

### v1.0 완료 기준 (MVP 목표)
- [ ] 무기 및 레전드 티어표가 S~D 등급별로 시각적으로 구분되어 깔끔하게 렌더링될 것.
- [ ] 카테고리 탭(`무기` ↔ `레전드`) 전환이 부드럽게 동작할 것.
- [ ] 모바일/웹 반응형 화면에서 티어 행 내부 카드들이 줄바꿈되며 깨지지 않을 것.

### v1.4 확장 완료 기준 (차기 백로그)
- [ ] 드래그 & 드롭 인터랙션을 지원하여 유저가 직접 아이콘을 끌어다 티어표를 재배치할 수 있을 것.
- [ ] [PNG 저장] 버튼 클릭 시 워터마크가 포함된 완성된 티어표 이미지가 다운로드될 것.
