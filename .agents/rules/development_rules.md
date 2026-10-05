# 개발 및 품질 관리 표준 규칙 (Development & Quality Standards)

## 1. 📂 경로 참조 원칙 (Path Safety)
- **작업 디렉토리(CWD) 상대경로 의존 금지**:
  - `open('data.csv')` 또는 `os.getcwd()`에 의존하는 코드를 작성하지 않는다.
  - 항상 `scripts/config.py`에 정의된 `BASE_DIR`, `CONFIG_DIR`, `DATA_DIR` 또는 `pathlib.Path(__file__).resolve()`를 기준으로 한 절대 경로를 사용한다.

---

## 2. 🧩 순수 로직과 프레젠테이션의 분리 (Separation of Concerns)
- **비즈니스 계산 로직(TTK, DPS, 유효 사거리 감쇄 등)**은 UI 컴포넌트나 크롤러 안에 결합하지 않고, 순수 함수(Pure Function)로 독립 모듈(`src/utils/calculator.ts` 또는 `scripts/core/`)에 분리한다.
- 순수 함수 구조를 유지하여 단위 테스트(Unit Test) 및 TC 자동 설계 모듈이 100% 독립 검증할 수 있도록 설계한다.

---

## 3. 📋 데이터 계약(Data Contract) 준수
- 크롤러나 백엔드가 생성하는 데이터 필드명 및 타입은 사전에 정의된 `Data Contract`를 준수해야 한다.
- 필드명 변경, 삭제 등 하위 호환성을 깨뜨리는 스키마 수정은 기획 문서(PRD) 검토 없이 임의로 진행하지 않는다.

---

## 4. 🔍 검증 우선주의 (Verification First)
- 코드 수정 후에는 반드시 관련된 테스트 코드나 스크립트(예: 데이터 로더, 린트, 빌드)를 직접 실행하여 동작을 검증한 뒤 완료를 보고한다.
- 추측에 기반한 완료 보고는 지양하며, 실행 결과 로그(Exit Code, Output)를 근거로 제시한다.

---

## 5. 🖥️ 화면 개발 및 뷰포트 기준 (Desktop-First with Responsive Foundation)
- **데스크톱 웹 우선 (Desktop-First)**:
  - 초기 화면 개발 및 기능/데이터 검증은 **PC 모니터(1440px / 1920px 데스크톱 뷰)**를 기준으로 우선 완성한다.
- **반응형 확장 대비 (Responsive-Ready Foundation)**:
  - 추후 모바일/태블릿 반응형 뷰를 일괄 추가할 때 전체 구조를 전면 재작성하지 않도록, 경직된 고정 픽셀(`width: 1200px` 하드코딩 등) 사용을 지양한다.
  - `flex`, `grid`, `max-width`, `%` 등 유연한 CSS 레이아웃을 기본으로 사용하여, 향후 미디어 쿼리(`@media`) 추가만으로 모바일/태블릿에 자연스럽게 대응될 수 있도록 기초 구조를 설계한다.

---

## 6. 🔄 데이터 및 에셋 캐시 버스팅 원칙 (Cache Busting)
- 브라우저 및 CDN 캐시로 인해 게임 밸런스 패치나 최신 데이터가 누락되는 것을 원천 방지한다.
- 데이터 JSON 및 핵심 정적 에셋 호출 시 `?v=${Date.now()}` 타임스탬프 또는 명시적 릴리즈 버전(`?v=1.0.0`) 파라미터를 필수로 부여한다.

---

## 7. 🔗 URL Hash 기반 딥링크 및 브라우저 히스토리 (History-Aware Routing)
- SPA 내 모든 주요 탭 및 뷰 전환은 URL Hash(`#home`, `#weapons`, `#legends` 등)와 1:1 동기화되어야 한다.
- 특정 뷰의 URL을 복사해 공유할 수 있는 딥링크를 보장하고, 브라우저 뒤로 가기/앞으로 가기(`hashchange`) 시 페이지 새로고침이나 이탈 없이 이전 화면이 자연스럽게 복원되도록 설계한다.

---

## 8. 🛡️ 데이터-UI 매핑의 견고성 및 안전 폴백 (Robust Mapping & Safe Fallback)
- 탄약, 총기군, 레전드 클래스 등 상태/카테고리 뱃지를 UI에 바인딩할 때 하드코딩된 if-else를 지양하고 설정 딕셔너리(`CONFIG`) 구조를 사용한다.
- 대소문자 무시 및 공백 정규화(trim)를 적용하며, 신규 탄약이나 예외 데이터가 유입되더라도 UI가 깨지지 않는 기본 폴백(Default Badge)을 의무적으로 구현한다.

---

## 9. 📜 외부 지적재산권(IP) 및 라이선스 준수 (Legal & Policy Compliance)
- 게임 데이터, 이미지, 폰트 활용 시 Electronic Arts의 공식 팬 콘텐츠 정책(Fan Content Policy) 및 오픈폰트 라이선스(OFL)를 철저히 준수한다.
- 비상업적 팬 메이드 프로젝트 명시 및 원저작권자 권리 표기가 담긴 [CREDITS.md](file:///c:/Dev/Apex/CREDITS.md) 문서를 항상 유지한다.


