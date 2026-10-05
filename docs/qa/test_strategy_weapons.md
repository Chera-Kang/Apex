# 🛡️ 무기 도감 및 TTK 계산기 테스트 전략 (QA Test Strategy)

> **대상 모듈**: `Weapons & TTK Calculator`  
> **기준 기획서**: [docs/planning/01_weapon_calculator.md](file:///c:/Dev/Apex/docs/planning/01_weapon_calculator.md)  
> **작성자**: QA Engineer

---

## 1. 🎯 테스트 목표
1. 위키/시트 크롤링 데이터의 무결성(결측치, 음수, 이상치)을 100% 자동 검출.
2. 방어구/헬멧 상태별 TTK 및 필요 탄환 수 계산 알고리즘의 정밀 수학 일치성 보증 (오차 ±0.01초 이내).
3. 반응형 웹 환경(모바일 375px ~ 데스크톱 1440px) 및 인터랙션 반응 속도(100ms) 품질 확보.

---

## 2. 🧪 4단계 검증 체계 (Verification Gates)

```
[Gate 1: Data QA] ──► [Gate 2: Logic QA] ──► [Gate 3: E2E QA] ──► [Gate 4: Sign-off]
 크롤링 데이터 정합성   TTK 수학 오차 단정    반응형/크로스 브라우징   배포 승인 리포트
 (pytest)              (TC 자동 설계 연계)   (Playwright/Manual)    (GO / NO-GO)
```

### Gate 1: Data Quality Gate (데이터 무결성 검증)
- [ ] 전체 무기 개수: 29개 무기 전수 로드 확인
- [ ] 데미지 관계식: `dmg_head >= dmg_body >= dmg_leg` 단정
- [ ] 양수 검증: `RPM > 0`, `DPS > 0` 검증
- [ ] 필수값 누락 검증: `name`, `type`, `ammo`, `dmg_body` 필드에 null/빈값 차단

### Gate 2: Logic Accuracy QA (TTK 정밀 수학 검증)
- **오라클(Test Oracle) 대조 테스트 케이스**:
  | 총기명 | RPM | 데미지 | 적 체력(Armor) | 필요 탄환 | 기대 TTK | 허용 오차 |
  | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
  | **R-99** | 1080 | 14 | 200 (퍼플) | 15발 | **0.78초** | ±0.01초 |
  | **Volt SMG** | 720 | 15 | 200 (퍼플) | 14발 | **1.08초** | ±0.01초 |
  | **VK-47 Flatline** | 600 | 18 | 225 (레드) | 13발 | **1.20초** | ±0.01초 |
  | **Kraber** | 26 | 140 | 100 (노실드) | 1발 | **0.00초** | 0.00초 (단발 킬) |
- **TC 자동 설계 도구 연계 영역**:
  - 무기 29종 × 방어구 5종 × 헬멧 4종 조합에 대한 **페어와이즈(Pairwise) 테스트 매트릭스** 자동 생성 및 대량 회귀 검증(Regression).

### Gate 3: UI & E2E 인터랙션 QA
- [ ] 필터링 반응 시간: 탭 클릭 후 그리드 재정렬까지 100ms 이내
- [ ] 모바일(375px iPhone SE), 태블릿(768px iPad), PC(1440px) 뷰포트 레이아웃
- [ ] 0 데미지 및 특수 무기(보섹 활, 차지 라이플) 예외 조작 시 프론트 크래시 방어

### Gate 4: QA Sign-Off (최종 배포 승인)
- 4단계 게이트 통과 후 `docs/qa/qa_signoff_v0.1.0.md` 배포 승인 문서 발행 (최종 판정: `GO`)
