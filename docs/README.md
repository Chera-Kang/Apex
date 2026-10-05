# 📚 Apex Legends Platform - 문서 체계 (Documentation Hub)

프로덕트의 **'기획(Planning) ➔ 개발(Dev) ➔ 검증(QA)'** 라이프사이클을 효율적으로 관리하기 위한 문서 디렉토리입니다.

```
docs/
├── planning/       # [기획] PRD, 공통 디자인 시스템, 4대 핵심 기능 명세서 (Living Document)
├── dev/            # [개발] 아키텍처 설계, 기술 스택 결정, 데이터 파이프라인 명세
└── qa/             # [검증] 테스트 전략(Test Strategy), 품질 체크리스트, 배포 승인 기준(DoD)
```

---

## 📂 폴더별 역할 및 문서 목록

### 1. `planning/` (기획 및 기능 명세서)
모든 기능 명세서는 **기획(UI Flow) ➔ 개발(Data Schema) ➔ 검증(DoD)** 3단계 표준 섹션을 갖춘 단일 문서(Living Document)로 관리됩니다.

- [PRD.md](file:///c:/Dev/Apex/docs/planning/PRD.md): **[제품 나침반]** 제품 비전 및 `v1.0 (MVP 4대 기능)` ➔ `v1.x (확장)` ➔ `v2.0 (대규모 도약)` 버전 로드맵
- [00_design_system.md](file:///c:/Dev/Apex/docs/planning/00_design_system.md): 공통 Apex 다크 테마 디자인 토큰, 타이포그래피, HUD 사선 모서리
- [00_home_page.md](file:///c:/Dev/Apex/docs/planning/00_home_page.md): 메인 로비 커맨드 센터 대시보드 및 GNB 네비게이션
- [01_weapons.md](file:///c:/Dev/Apex/docs/planning/01_weapons.md): **[기능 1]** 총기 정보 명세서 (31종 기본 스펙, 필터링, 교차검증)
- [02_apex_info.md](file:///c:/Dev/Apex/docs/planning/02_apex_info.md): **[기능 2]** Apex Info 명세서 (공지사항, 패치노트, 실시간 맵 로테이션)
- [03_legends.md](file:///c:/Dev/Apex/docs/planning/03_legends.md): **[기능 3]** 레전드 정보 명세서 (28종 프로필, 스토리, 스킬 수치, 시즌 20 퍽)
- [04_tierlist.md](file:///c:/Dev/Apex/docs/planning/04_tierlist.md): **[기능 4]** 티어리스트 명세서 (시즌 메타 무기/레전드 티어 시각화)

---

### 2. `dev/` (개발 참고 & 아키텍처)
- [architecture_overview.md](file:///c:/Dev/Apex/docs/dev/architecture_overview.md): 시스템 아키텍처, SPA 해시 라우터, 위키 크롤러 및 구글 시트 파이프라인

---

### 3. `qa/` (품질 검증 & 테스트 리포트)
- [test_strategy_weapons.md](file:///c:/Dev/Apex/docs/qa/test_strategy_weapons.md): 무기 데이터 3단계 수학적 교차검증 전략 및 품질 기준
