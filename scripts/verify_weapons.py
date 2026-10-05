"""
Apex Legends 무기 데이터 교차 검증 및 실시간 패치 감지기 (Cross-Validation & Patch Tracker)
=============================================================================
1. Live Wiki vs DB(구글 시트 / 로컬 JSON) 필드별 정밀 비교
2. 수식 물리 불변성 검증 (DPS ≈ 데미지 * RPM / 60, 헤드샷 >= 몸통 >= 다리)
3. 밸런스 패치 및 보급 로테이션 변경점 자동 감지
4. 승인 시 원클릭 DB & 로컬 데이터 동기화
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Windows 콘솔 한글 깨짐 방지
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
BASE_DIR = CURRENT_DIR.parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from config import DATA_DIR, SHEET_URL, CREDS_PATH
from apex_crawler import scrape_data, upload_to_google_sheets, save_local_data

def load_local_json() -> Dict[str, Dict[str, Any]]:
    """로컬 data/weapons_data.json 로드"""
    json_path = DATA_DIR / "weapons_data.json"
    if not json_path.exists():
        return {}
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            items = json.load(f)
            return {item["name"]: item for item in items if "name" in item}
    except Exception as e:
        print(f"[경고] 로컬 JSON 로드 실패: {e}")
        return {}

def load_google_sheet_weapons() -> Dict[str, Dict[str, Any]]:
    """구글 시트 'Weapon' 탭 로드"""
    try:
        import gspread
        gc = gspread.service_account(filename=CREDS_PATH)
        doc = gc.open_by_url(SHEET_URL)
        ws = doc.worksheet("Weapon")
        records = ws.get_all_records()
        return {r["name"]: r for r in records if "name" in r and r["name"]}
    except Exception as e:
        print(f"[경고] 구글 시트 연결 실패: {e}")
        return {}

def verify_math_invariants(weapons: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """물리 및 수식 불변성 검증 (오타 및 비정상 수치 필터링)"""
    math_issues = []
    for w in weapons:
        name = w.get("name", "Unknown")
        body = w.get("dmg_body")
        head = w.get("dmg_head")
        leg = w.get("dmg_leg")
        rpm = w.get("RPM")
        dps = w.get("DPS")

        # 1. 헤드샷 >= 몸통 >= 다리 데미지 검증
        if isinstance(head, (int, float)) and isinstance(body, (int, float)):
            if head < body:
                math_issues.append({
                    "weapon": name,
                    "type": "DAMAGE_HIERARCHY",
                    "detail": f"헤드 데미지({head})가 몸통({body})보다 낮음"
                })
        if isinstance(body, (int, float)) and isinstance(leg, (int, float)):
            if leg > body:
                math_issues.append({
                    "weapon": name,
                    "type": "DAMAGE_HIERARCHY",
                    "detail": f"다리 데미지({leg})가 몸통({body})보다 높음 (이전 칼럼 밀림 버그 가능성)"
                })

        # 2. DPS 계산식 교차검증 (DPS ≈ body * RPM / 60)
        # 단, 차지 라이플이나 충전 무기류는 특수 충전 메커니즘이 있으므로 오차 10 이상만 플래그
        if isinstance(body, (int, float)) and isinstance(rpm, (int, float)) and isinstance(dps, (int, float)):
            calc_dps = round(body * rpm / 60, 1)
            diff = abs(calc_dps - dps)
            if diff > 5 and name not in ["Charge Rifle", "Sentinel", "30-30 Repeater", "Bocek Compound Bow", "Triple Take"]:
                math_issues.append({
                    "weapon": name,
                    "type": "DPS_MISMATCH",
                    "detail": f"표기 DPS({dps})와 계산 DPS({calc_dps}) 간 차이 발생 (차이: {diff:.1f})"
                })

    return math_issues

def compare_wiki_with_db(wiki_weapons: List[Dict[str, Any]], db_weapons: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Live Wiki 데이터와 현재 DB(구글 시트/로컬) 데이터를 1:1 대조하여 패치 내역 분석"""
    wiki_map = {w["name"]: w for w in wiki_weapons}
    
    diff_report = {
        "new_weapons": [],
        "missing_weapons": [],
        "balance_changes": [],
        "state_changes": []  # 일반 <-> 보급 전환 등
    }

    # 신규 무기 감지
    for name in wiki_map:
        if name not in db_weapons:
            diff_report["new_weapons"].append(name)

    # 누락/삭제 무기 감지
    for name in db_weapons:
        if name not in wiki_map:
            diff_report["missing_weapons"].append(name)

    # 기존 무기 제원 변경점 감지 (패치 감지)
    compare_fields = [
        "type", "ammo", "dmg_body", "dmg_head", "dmg_leg",
        "RPM", "DPS", "mag_0", "mag_1", "mag_2", "mag_3"
    ]

    for name, w_live in wiki_map.items():
        if name not in db_weapons:
            continue
        w_db = db_weapons[name]
        
        # 보급 <-> 일반 무기 탄약 변경 감지
        live_ammo = str(w_live.get("ammo", ""))
        db_ammo = str(w_db.get("ammo", ""))
        if ("Mythic" in live_ammo and "Mythic" not in db_ammo) or ("Mythic" not in live_ammo and "Mythic" in db_ammo):
            diff_report["state_changes"].append({
                "weapon": name,
                "change": f"보급 전환 감지: '{db_ammo}' -> '{live_ammo}'"
            })

        weapon_diffs = []
        for field in compare_fields:
            val_live = str(w_live.get(field, "-")).strip()
            val_db = str(w_db.get(field, "-")).strip()
            
            # .svg 확장자 또는 소수점/정수 포맷 차이 정규화
            val_db_clean = val_db.replace(".svg", "").replace("Ammo", "").replace("Rounds", "").strip()
            val_live_clean = val_live.replace(".svg", "").replace("Ammo", "").replace("Rounds", "").strip()

            if val_live_clean != val_db_clean:
                weapon_diffs.append({
                    "field": field,
                    "old_val": val_db,
                    "new_val": val_live
                })

        if weapon_diffs:
            diff_report["balance_changes"].append({
                "weapon": name,
                "diffs": weapon_diffs
            })

    return diff_report

def print_verification_report(wiki_weapons, db_source_name, diff_report, math_issues):
    """결과 리포트 출력"""
    print("\n" + "=" * 70)
    print(f" [APEX INFO] 데이터 교차검증 & 패치 감지 리포트")
    print(f" 비교 대상: Live wiki.gg ({len(wiki_weapons)}종) vs {db_source_name}")
    print("=" * 70)

    # 1. 수식 불변성 검증 결과
    print("\n[1] 수학적 정합성 검증 (Math & Physics Invariant Check):")
    if not math_issues:
        print("  -> OK: 모든 무기의 헤드샷/몸통/다리 비율 및 DPS 공식이 정상입니다.")
    else:
        print(f"  -> 주의: {len(math_issues)}건의 수식 불일치/특이사항 발견:")
        for issue in math_issues:
            print(f"     * [{issue['type']}] {issue['weapon']}: {issue['detail']}")

    # 2. 신규/누락 무기
    print("\n[2] 무기 라인업 변경 감지 (Weapon Lineup Changes):")
    if diff_report["new_weapons"]:
        print(f"  -> [신규 무기 추가]: {', '.join(diff_report['new_weapons'])}")
    if diff_report["missing_weapons"]:
        print(f"  -> [무기 삭제/미등재]: {', '.join(diff_report['missing_weapons'])}")
    if not diff_report["new_weapons"] and not diff_report["missing_weapons"]:
        print("  -> OK: 라인업에 변동이 없습니다.")

    # 3. 보급 로테이션 변경
    if diff_report["state_changes"]:
        print("\n[3] 케어 패키지(보급 무기) 로테이션 변경 감지:")
        for sc in diff_report["state_changes"]:
            print(f"  -> [ROTATION] {sc['weapon']}: {sc['change']}")

    # 4. 세부 수치 밸런스 패치
    print("\n[4] 밸런스 패치 및 제원 변동 상세 (Balance / Data Diffs):")
    if not diff_report["balance_changes"]:
        print("  -> 변동 사항 없음: DB와 최신 위키 데이터가 100% 일치합니다.")
    else:
        print(f"  -> 총 {len(diff_report['balance_changes'])}개 무기에서 수치 변동 감지:")
        for bc in diff_report["balance_changes"][:15]:  # 상위 15개 출력
            print(f"\n  * 무기: {bc['weapon']}")
            for d in bc["diffs"]:
                print(f"    - {d['field']:<12}: {d['old_val']}  -->  {d['new_val']}")
        if len(diff_report["balance_changes"]) > 15:
            print(f"\n  ... 외 {len(diff_report['balance_changes']) - 15}개 무기 변경")

    print("\n" + "=" * 70)

def main():
    parser = argparse.ArgumentParser(description="Apex Legends 무기 데이터 교차검증기")
    parser.add_argument("--sync", action="store_true", help="검증 완료 후 최신 데이터를 로컬 및 구글 시트에 자동 동기화")
    parser.add_argument("--source", choices=["sheet", "local"], default="sheet", help="대조할 DB 소스 선택 (기본: sheet)")
    args = parser.parse_args()

    # 1. Live Wiki 스크랩
    wiki_weapons = scrape_data()
    if not wiki_weapons:
        print("[오류] Wiki 데이터를 가져오지 못했습니다.")
        sys.exit(1)

    # 2. 수식 정합성 검증
    math_issues = verify_math_invariants(wiki_weapons)

    # 3. DB 소스 로드 (구글 시트 또는 로컬 JSON)
    if args.source == "sheet":
        db_weapons = load_google_sheet_weapons()
        source_name = f"Google Sheets 'Weapon' 탭 ({len(db_weapons)}종)"
        if not db_weapons:
            print("[알림] 구글 시트를 불러오지 못해 로컬 JSON으로 대체 대조합니다.")
            db_weapons = load_local_json()
            source_name = f"로컬 weapons_data.json ({len(db_weapons)}종)"
    else:
        db_weapons = load_local_json()
        source_name = f"로컬 weapons_data.json ({len(db_weapons)}종)"

    # 4. Diff 계산
    diff_report = compare_wiki_with_db(wiki_weapons, db_weapons)

    # 5. 리포트 출력
    print_verification_report(wiki_weapons, source_name, diff_report, math_issues)

    # 6. 동기화 옵션 처리
    if args.sync:
        print("\n[동기화 진행] 최신 검증 데이터를 구글 시트와 로컬 파일에 적용합니다...")
        save_local_data(wiki_weapons)
        upload_to_google_sheets(wiki_weapons)
        print("[완료] 모든 데이터가 최신 상태로 동기화되었습니다.")
    else:
        has_diffs = bool(diff_report["new_weapons"] or diff_report["balance_changes"] or diff_report["state_changes"])
        if has_diffs:
            print("\n[안내] 데이터 차이가 발견되었습니다. 최신 데이터로 동기화하려면 다음 명령어를 실행하세요:")
            print("  .venv\\Scripts\\python.exe scripts/verify_weapons.py --sync\n")

if __name__ == "__main__":
    main()
