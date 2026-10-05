# 🎨 [공통 기획] Apex 시그니처 다크 테마 디자인 시스템 (Design System)

> **문서 ID**: `PLAN-000`  
> **상태**: `Approved / Standard`  
> **적용 범위**: 전 화면(GNB, 무기/레전드 도감, 맵, 계산기, 티어표) 공통 UI 컴포넌트

---

## 1. 🎯 디자인 컨셉 및 방향성
- **컨셉**: Apex Legends 인게임 HUD(Head-Up Display)의 미래지향적 SF 분위기 계승.
- **핵심 원칙**:
  1. **정보 가독성 최우선 (Data-First)**: 복잡한 수치와 텍스트가 어두운 배경에서도 즉시 식별될 수 있도록 높은 대비(High Contrast) 유지.
  2. **SF 테크니컬 감성**: 직각 모서리 대신 **사선 모서리 컷팅(Chamfered Edges)**과 얇은 테크니컬 그리드 라인 활용.
  3. **인게임 아이덴티티**: 공식 Apex Red, 실드 블루, 에너지 오렌지 색상을 포인트 액센트로 적용.

---

## 2. 🎨 컬러 시스템 (Color Tokens)

### 1) 배경 & 서피스 (Background & Surfaces)
| 토큰명 | Hex 코드 | 용도 |
| :--- | :--- | :--- |
| `--bg-main` | `#121316` | 전체 웹페이지 최하단 기본 배경색 (Deep Charcoal) |
| `--bg-surface` | `#1A1C20` | 카드, 패널, 모달창 기본 바탕색 (Elevated Slate) |
| `--bg-surface-hover` | `#24272D` | 카드 호버(Hover) 시 살짝 밝아지는 서피스 색 |
| `--border-panel` | `#2F343B` | 패널 및 카드 테두리 라인 |

### 2) 액센트 컬러 (Brand & Role Accents)
| 토큰명 | Hex 코드 | 용도 |
| :--- | :--- | :--- |
| `--accent-red` | `#DA292A` | Apex 시그니처 레드 (메인 버튼, 선택된 탭, 에러, 헤드샷 데미지) |
| `--accent-orange` | `#FF5E1E` | 에너지 오렌지 (하이라이트, 이벤트 배지, 경고) |
| `--accent-blue` | `#00E5FF` | 실드 사이언 블루 (실드 수치, 정보 뱃지, 링크) |
| `--accent-green` | `#22C55E` | 성공, 안전, 원탄창 킬 가능 뱃지 |

### 3) 텍스트 컬러 (Typography)
| 토큰명 | Hex 코드 | 용도 |
| :--- | :--- | :--- |
| `--text-primary` | `#F3F4F6` | 헤드라인, 주요 수치값 (순백색에 가까운 밝은 회색) |
| `--text-secondary`| `#9CA3AF` | 설명 문구, 비활성 라벨, 부가 정보 |
| `--text-muted` | `#6B7280` | 단위 표기(초, 발, RPM), 푸터 텍스트 |

---

## 3. 🧩 공통 UI 컴포넌트 가이드

### 1) 사선 모서리 카드 (Chamfered Card)
- 일반적인 둥근 모서리(`border-radius`) 대신, 카드의 우측 상단과 좌측 하단에 사선 컷팅 효과 적용:
  ```css
  clip-path: polygon(0 0, calc(100% - 12px) 0, 100% 12px, 100% 100%, 12px 100%, 0 calc(100% - 12px));
  ```

### 2) 인게임 뱃지 태그 (Badge Tags)
- 탄약 종류, 총기 클래스, 레전드 역할군을 나타내는 소형 뱃지:
  - 폰트: Bold 대문자 11px
  - 패딩: `2px 8px`
  - 배경: 각 탄약/역할군 고유 색상의 투명도 15% + 테두리 1px

### 3) 공통 헤더 GNB (Global Navigation Bar)
- 좌측: `APEX INFO` 로고 + 버전 배지 (`v0.1.0`)
- 중앙: 메뉴 탭 `[ 홈 ]` `[ 무기 도감 ]` `[ 레전드 ]` `[ 맵 ]` `[ 계산기 ]` `[ 티어표 ]`
- 우측: 외부 위키 링크 및 GitHub 아이콘
