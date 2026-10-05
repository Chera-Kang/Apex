import requests
from bs4 import BeautifulSoup
import gspread
import os
import sys
import json
import csv
import re
from pathlib import Path

# Windows 콘솔 한글 깨짐 방지
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 프로젝트 루트 및 scripts 경로 설정
CURRENT_DIR = Path(__file__).resolve().parent
BASE_DIR = CURRENT_DIR.parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

# --- Configuration & Mappings ---
from config import DATA_DIR, SHEET_URL, CREDS_PATH

NAME_KOR_MAP = {
    "HAVOC Rifle": "하복 소총",
    "VK-47 Flatline": "VK-47 플랫라인",
    "Hemlok Burst AR": "헴록 버스트 AR",
    "R-301 Carbine": "R-301 카빈",
    "Nemesis Burst AR": "네메시스 버스트 AR",
    "Alternator SMG": "얼터네이터 SMG",
    "Prowler Burst PDW": "프라울러 버스트 PDW",
    "R-99 SMG": "R-99 SMG",
    "Volt SMG": "볼트 SMG",
    "C.A.R. SMG": "C.A.R. SMG",
    "Devotion LMG": "디보션 LMG",
    "L-STAR EMG": "L-STAR EMG",
    "M600 Spitfire": "M600 스핏파이어",
    "Rampage LMG": "램페이지 LMG",
    "G7 Scout": "G7 스카우트",
    "Triple Take": "트리플 테이크",
    "30-30 Repeater": "30-30 리피터",
    "Bocek Compound Bow": "보섹 컴파운드 보우",
    "Charge Rifle": "차지 라이플",
    "Longbow DMR": "롱보우 DMR",
    "Kraber .50-Cal Sniper": "크레이버 .50구경 스나이퍼",
    "Sentinel": "센티넬",
    "EVA-8 Auto": "EVA-8 오토",
    "Mastiff Shotgun": "마스티프 샷건",
    "Mozambique Shotgun": "모잠비크 샷건",
    "Mozambique Shotgun Akimbo": "모잠비크 아킴보",
    "Peacekeeper": "피스키퍼",
    "RE-45 Auto": "RE-45 오토",
    "RE-45 Auto Akimbo": "RE-45 아킴보",
    "P2020": "P2020",
    "P2020 Akimbo": "P2020 아킴보",
    "Wingman": "윙맨"
}

VALID_WEAPON_TYPES = {"AR", "LMG", "Marksman", "Pistol", "Shotgun", "SMG", "Sniper"}

def clean_num(val):
    """숫자 문자열을 정수/실수로 변환하거나 '-' 반환 (노트 기호 [1] 및 min/max 텍스트 제거)"""
    if val is None:
        return "-"
    s = str(val).strip()
    if not s or s.lower() == "n/a" or "incomplete" in s.lower() or s == "":
        return "-"
    s = re.sub(r"\[\d+\]", "", s).strip()
    m = re.search(r"(\d+(?:\.\d+)?)", s)
    if m:
        n = m.group(1)
        return int(n) if n.isdigit() else float(n)
    return "-"

def clean_ammo(ammo_cell):
    """탄약 이미지의 alt/title에서 탄약명 추출 및 SVG 확장자 제거"""
    img = ammo_cell.find("img")
    if img:
        raw = img.get("alt", img.get("title", ""))
    else:
        raw = ammo_cell.text.strip()
    raw = raw.replace(".svg", "").replace("Ammo", "").replace("Rounds", "").strip()
    return raw if raw else "-"

def scrape_data():
    """Apex Legends wiki.gg에서 무기 제원 데이터를 안전하게 크롤링"""
    print("Scraping Apex Legends Wiki (wiki.gg)...")
    url = "https://apexlegends.wiki.gg/wiki/Weapon"
    try:
        # Cloudflare / User-Agent 블록 방지를 위해 cURL 표준 User-Agent 명시
        response = requests.get(url, headers={"User-Agent": "curl/8.4.0"}, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
    except Exception as e:
        print(f"Failed to fetch wiki: {e}")
        return []

    tables = soup.find_all("table", class_="wikitable")
    if len(tables) < 2:
        print("Error: Weapons table not found on page.")
        return []

    # Table 1이 'General Stats' 테이블
    table = tables[1]
    rows = table.find_all("tr")

    weapons_list = []
    seen_names = set()

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 15:
            continue

        name_en = cols[0].text.strip()
        w_type = cols[1].text.strip()

        # 무기 종류(Type)가 유효하고 헤더나 노이즈 행이 아닌 경우만 파싱
        if w_type not in VALID_WEAPON_TYPES:
            continue

        # 중복 무기(예: Bocek 산탄 캡 모드 행) 방지
        if name_en in seen_names:
            continue
        seen_names.add(name_en)

        try:
            ammo_text = clean_ammo(cols[2])

            # 전 무기 공통 통계 (열 위치 고정)
            # Col 4: 몸통 데미지(Body)
            # Col 5: 헤드샷 기본 데미지(Head Lv.0)
            # Col 9: 다리 데미지(Legs)
            # Col 10: RPM (연사력)
            # Col 11: DPS (초당 피해량)
            dmg_body = clean_num(cols[4].text)
            dmg_head = clean_num(cols[5].text)
            dmg_leg = clean_num(cols[9].text)
            rpm = clean_num(cols[10].text)
            dps = clean_num(cols[11].text)

            # 열 개수에 따른 탄창 및 재장전 시간 동적 매핑
            cols_len = len(cols)
            mag_0, mag_1, mag_2, mag_3 = "-", "-", "-", "-"
            reload_tac, reload_full, proj_speed = "-", "-", "-"

            if cols_len == 25:  # 일반 드롭 풀 스펙 무기 (AR, SMG, LMG 등)
                mag_0 = clean_num(cols[12].text)
                mag_1 = clean_num(cols[13].text)
                mag_2 = clean_num(cols[14].text)
                mag_3 = clean_num(cols[15].text)
                reload_tac = clean_num(cols[16].text)
                reload_full = clean_num(cols[20].text)
                proj_speed = clean_num(cols[24].text)
            elif cols_len == 16:  # 보급 무기 (R-99, Devotion, Kraber) 또는 윙맨/모잠비크
                mag_0 = clean_num(cols[12].text)
                reload_tac = clean_num(cols[13].text)
                reload_full = clean_num(cols[14].text)
                proj_speed = clean_num(cols[15].text)
            elif cols_len == 19:  # 권총류 (RE-45, P2020, P2020 아킴보)
                mag_0 = clean_num(cols[12].text)
                mag_1 = clean_num(cols[13].text)
                mag_2 = clean_num(cols[14].text)
                mag_3 = clean_num(cols[15].text)
                reload_tac = clean_num(cols[16].text)
                reload_full = clean_num(cols[17].text)
                proj_speed = clean_num(cols[18].text)
            elif cols_len == 22:  # 샷건류 탄창 고정 (EVA-8, Peacekeeper)
                mag_0 = clean_num(cols[12].text)
                reload_tac = clean_num(cols[13].text)
                reload_full = clean_num(cols[17].text)
                proj_speed = clean_num(cols[21].text)
            elif cols_len == 18:  # 30-30 리피터 (단발 개별 장전)
                mag_0 = clean_num(cols[12].text)
                mag_1 = clean_num(cols[13].text)
                mag_2 = clean_num(cols[14].text)
                mag_3 = clean_num(cols[15].text)
                proj_speed = clean_num(cols[17].text)
            elif cols_len == 15:  # 마스티프, 보섹 활
                mag_0 = clean_num(cols[12].text)
                proj_speed = clean_num(cols[14].text)

            weapons_list.append({
                "name": name_en,
                "name_kor": NAME_KOR_MAP.get(name_en, name_en),
                "type": w_type,
                "ammo": ammo_text,
                "mag_0": mag_0,
                "mag_1": mag_1,
                "mag_2": mag_2,
                "mag_3": mag_3,
                "dmg": dmg_body,
                "dmg_head": dmg_head,
                "dmg_body": dmg_body,
                "dmg_leg": dmg_leg,
                "RPM": rpm,
                "DPS": dps,
                "Reload_time": reload_full,
                "Reload_time(Tactical)": reload_tac,
                "Projectile_Speed": proj_speed
            })
        except Exception as e:
            print(f"Error parsing row for {name_en}: {e}")
            continue

    print(f"Successfully scraped {len(weapons_list)} weapons from wiki.")
    return weapons_list

def upload_to_google_sheets(data):
    """구글 시트 'Weapon' 탭에 깨끗한 최신 제원 데이터 동기화"""
    if not data:
        return False
    
    print("Connecting to Google Sheets...")
    try:
        gc = gspread.service_account(filename=CREDS_PATH)
        doc = gc.open_by_url(SHEET_URL)
        worksheet = doc.worksheet("Weapon")
        
        headers = [
            'name', 'name_kor', 'type', 'ammo', 
            'mag_0', 'mag_1', 'mag_2', 'mag_3', 
            'dmg', 'dmg_head', 'dmg_body', 'dmg_leg', 
            'RPM', 'DPS', 'Reload_time', 'Reload_time(Tactical)',
            'Projectile_Speed'
        ]
        
        rows = [headers]
        for item in data:
            row = [item.get(h, "-") for h in headers]
            rows.append(row)

        print(f"Updating Google Sheet with {len(data)} weapons...")
        worksheet.clear()
        worksheet.update(values=rows, range_name='A1')
        
        # 가독성을 위한 헤더 서식 지정 (다크 헤더 + 볼드 텍스트)
        col_end_letter = chr(64 + len(headers))
        worksheet.format(f'A1:{col_end_letter}1', {
            "backgroundColor": {"red": 0.12, "green": 0.13, "blue": 0.15},
            "horizontalAlignment": "CENTER",
            "textFormat": {"foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}, "bold": True}
        })
        worksheet.freeze(rows=1)
        
        print(f"Google Sheets update complete! ({len(data)} weapons)")
        return True
    except Exception as e:
        print(f"Failed to upload to Google Sheets: {e}")
        return False

def save_local_data(data):
    """로컬 CSV 및 JSON 파일 동기화 저장 (UTF-8)"""
    if not data:
        return
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save CSV
    csv_path = DATA_DIR / "weapons_data_refined.csv"
    headers = list(data[0].keys())
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)
    print(f"Saved {len(data)} weapons to {csv_path}")

    # Save JSON
    json_path = DATA_DIR / "weapons_data.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(data)} weapons to {json_path}")

if __name__ == "__main__":
    weapon_data = scrape_data()
    if weapon_data:
        save_local_data(weapon_data)
        upload_to_google_sheets(weapon_data)
