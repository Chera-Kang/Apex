# 🔫 [기능 1] 총기 정보 명세서 (Weapons Specification)

> **문서 ID**: `SPEC-001`  
> **상태**: `v1.0 완료 (Done) / v1.1 대기 (Backlog)`  
> **단일 문서 원칙(Living Document)**: 총기 도감 기능의 기획, 개발 데이터 구조, 검증 기준(DoD) 및 버전별 확장 내역을 단일 파일로 관리합니다.

---

## 📌 기능 버전 및 진행 현황 (Version Tracker)

| 버전 | 구분 | 목표 | 상태 | 주요 반영 사항 |
| :---: | :---: | :--- | :---: | :--- |
| **v1.0** | MVP | 총기 기본 제원 & 필터링 도감 | **✅ 완료 (Done)** | 31종 총기 수집, 3단계 교차검증 파이프라인, 탄약 6종 뱃지, 실시간 검색 |
| **v1.1** | 확장 | 총기 실전 심화 팁 & 가이드 | ⏳ 예정 (Backlog) | 총기별 반동 패턴 팁, 추천 홉업/부착물 조합, 거리별 데미지 감쇄 안내 |

---

## 1. 📋 기획 (Planning : Why & UI Flow)

### 1) 왜 필요한가? (User Value)
- 에이펙스 레전드에는 31종의 총기가 존재하며, 패치마다 데미지와 탄창 용량이 바뀝니다.
- 유저는 교전 전 "내 총의 기본 데미지가 몇인지, 탄창 용량과 연사력(RPM)이 어떻게 되는지"를 한곳에서 빠르게 필터링하여 확인하길 원합니다.

### 2) 화면 구성 및 인터랙션 흐름 (UI Flow)
1. **GNB 진입**: 사용자가 상단 `[ 무기 도감 ]` 탭을 클릭하거나 URL `#weapons`로 직접 접근합니다.
2. **필터 툴바**:
   - **총기군 필터**: `[전체]` `[AR]` `[SMG]` `[LMG]` `[Marksman]` `[Sniper]` `[Shotgun]` `[Pistol]` 버튼으로 즉시 카드 필터링
   - **탄약 필터**: `[전체]` `[경량]` `[중량]` `[에너지]` `[스나이퍼]` `[샷건]` 선택 지원
   - **실시간 검색**: 한글(예: `플랫라인`, `카빈`) 또는 영문(예: `R-99`, `volt`) 입력 시 즉각 반응
3. **무기 카드 그리드**:
   - 총기 한/영 명칭, 분류 뱃지, 고유 탄약 뱃지(경량 오렌지, 중량 블루, 에너지 그린, 보급 마젠타 등)
   - 3분할 데미지 박스: **HEAD / BODY / LEG**
   - 하단 정보 바: **RPM, DPS, 기본~확장 탄창 용량**

---

## 2. ⚙️ 개발 (Dev : Data & Implementation)

### 1) 데이터 수집 및 교차검증 체계 (Pipeline)
- **출처**: [Apex Legends Wiki - Weapons](https://apexlegends.wiki.gg/wiki/Weapon)
- **수집 스크립트**: [scripts/apex_crawler.py](file:///c:/Dev/Apex/scripts/apex_crawler.py) (가변 15~25열 동적 파싱)
- **3단계 교차검증기**: [scripts/verify_weapons.py](file:///c:/Dev/Apex/scripts/verify_weapons.py)
  - `헤드샷(Lv.0) >= 몸통 >= 다리` 데미지 물리 계층 검증
  - `DPS ≈ 데미지 × RPM ÷ 60` 공식 검증으로 오타 필터링
  - Live Wiki vs DB 1:1 대조로 패치 변경점 감지 및 `--sync` 원클릭 갱신

### 2) 데이터 저장 구조
- **구글 스프레드시트 (`Weapon` 탭)**: 운영 및 관리용 17개 핵심 제원 표
- **로컬 JSON ([data/weapons_data.json](file:///c:/Dev/Apex/data/weapons_data.json))**:
  ```json
  {
    "name": "VK-47 Flatline",
    "name_kor": "VK-47 플랫라인",
    "type": "AR",
    "ammo": "Heavy",
    "mag_0": 19, "mag_1": 23, "mag_2": 27, "mag_3": 29,
    "dmg_head": 32, "dmg_body": 18, "dmg_leg": 15,
    "RPM": 600, "DPS": 180,
    "Reload_time": 3.1, "Reload_time(Tactical)": 2.4,
    "Projectile_Speed": 24000
  }
  ```

### 3) 프론트엔드 연동
- [src/app.js](file:///c:/Dev/Apex/src/app.js): `loadWeaponsData()`에서 `?v=${Date.now()}` 캐시 버스팅 적용 호출
- [src/styles/main.css](file:///c:/Dev/Apex/src/styles/main.css): `AMMO_BADGE_CONFIG`와 1:1 매핑되는 탄약 색상 뱃지

---

## 3. ✅ 검증 및 완료 기준 (Verification & DoD)

### v1.0 완료 기준 (현재 검증 완료)
- [x] 31종 전 무기 데이터가 `weapons_data.json` 및 구글 시트에 누락/열 밀림 없이 적재될 것.
- [x] `verify_weapons.py` 실행 시 수식 정합성 에러가 0건일 것.
- [x] `#weapons` 해시 라우팅 및 브라우저 뒤로 가기가 정상 동작할 것.
- [x] 보급(R-99, 크레이버 등) 및 일반 탄약 뱃지 색상이 정상 점등될 것.
- [x] 총기군/탄약 필터 및 한/영 검색이 지연 없이 필터링될 것.

### v1.1 확장 완료 기준 (차기 백로그)
- [ ] 카드 클릭 시 '세부 정보 모달'이 열리고 추천 부착물(총열, 개머리판 등)이 표시될 것.
- [ ] 총기별 1~2줄의 핵심 실전 운용 팁 텍스트가 노출될 것.
