import requests
from bs4 import BeautifulSoup
import pandas as pd
import gspread
import os
import time

# --- Configuration & Mappings ---
from config import SHEET_URL, CREDS_PATH

NAME_KOR_MAP = {
    "HAVOC Rifle": "하복 소총", "VK-47 Flatline": "VK-47 플랫라인", "Hemlok Burst AR": "헴록 버스트 AR",
    "R-301 Carbine": "R-301 카빈", "Nemesis Burst AR": "네메시스 버스트 AR", "Alternator SMG": "얼터네이터 SMG",
    "Prowler Burst PDW": "프라울러 버스트 PDW", "R-99 SMG": "R-99 SMG", "Volt SMG": "볼트 SMG",
    "C.A.R. SMG": "C.A.R. SMG", "Devotion LMG": "디보션 LMG", "L-STAR EMG": "L-STAR EMG",
    "M600 Spitfire": "M600 스핏파이어", "Rampage LMG": "램페이지 LMG", "G7 Scout": "G7 스카우트",
    "Triple Take": "트리플 테이크", "30-30 Repeater": "30-30 리피터", "Bocek Compound Bow": "보섹 컴파운드 보우",
    "Charge Rifle": "차지 라이플", "Longbow DMR": "롱보우 DMR", "Kraber .50-Cal Sniper": "크레이버 .50구경 스나이퍼",
    "Sentinel": "센티넬", "EVA-8 Auto": "EVA-8 오토", "Mastiff Shotgun": "마스티프 샷건",
    "Mozambique Shotgun": "모잠비크 샷건", "Peacekeeper": "피스키퍼", "RE-45 Auto": "RE-45 오토",
    "P2020": "P2020", "Wingman": "윙맨", "Mozambique Shotgun Akimbo": "모잠비크 아킴보",
    "P2020 Akimbo": "P2020 아킴보", "RE-45 Auto Akimbo": "RE-45 아킴보"
}

def clean_val(val, is_numeric=False):
    """Clean data and return '-' if invalid/empty."""
    if val is None: return "-"
    s = str(val).strip()
    if not s or "Incomplete" in s or s.lower() == "n/a":
        return "-"
    if is_numeric:
        # Check if it looks like a number (at least has a digit)
        if not any(char.isdigit() for char in s):
            return "-"
    return s

def scrape_data():
    print("Scraping Apex Legends Wiki...")
    url = "https://apexlegends.wiki.gg/wiki/Weapon"
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        print(f"Failed to fetch wiki: {e}")
        return []

    tables = soup.find_all('table', class_='wikitable')
    if len(tables) < 2:
        print("Error: Weapons table not found.")
        return []

    table = tables[1]
    rows = table.find_all('tr')
    
    weapons_list = []
    for i, row in enumerate(rows):
        cols = row.find_all('td')
        # Skip header rows and rows that are too short
        if not cols or len(cols) < 15: continue
        
        name_en = cols[0].text.strip()
        if not name_en: continue

        # --- Data Extraction ---
        try:
            # Basic Info
            w_type = clean_val(cols[1].text)
            
            # Ammo (Extract text from alt or title of the image)
            ammo_cell = cols[2]
            ammo_img = ammo_cell.find('img')
            if ammo_img:
                ammo_text = ammo_img.get('alt', ammo_img.get('title', '')).replace('Ammo', '').strip()
            else:
                ammo_text = ammo_cell.text.strip()
            ammo_text = clean_val(ammo_text)

            # Damage & Stats
            dmg_body = clean_val(cols[4].text, True)
            dmg_head = clean_val(cols[5].text, True)
            dmg_leg = clean_val(cols[6].text, True)
            rpm = clean_val(cols[10].text, True)
            dps = clean_val(cols[11].text, True)

            # Magazines (Mag 4 removed as requested)
            mag_0 = clean_val(cols[12].text, True)
            mag_1 = clean_val(cols[13].text, True)
            mag_2 = clean_val(cols[14].text, True)
            mag_3 = clean_val(cols[15].text, True)

            # Reload Times
            # Col 16 is tactical, Col 20 is full
            reload_tac = clean_val(cols[16].text, True)
            reload_full = clean_val(cols[20].text, True)
            
            # Recommendation: Projectile Speed (Col 24)
            proj_speed = clean_val(cols[24].text, True) if len(cols) > 24 else "-"

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
                "Projectile_Speed": proj_speed # New recommended column
            })
        except Exception as e:
            print(f"Error parsing row for {name_en}: {e}")
            continue

    print(f"Successfully scraped {len(weapons_list)} weapons.")
    return weapons_list

def upload_to_google_sheets(data):
    if not data: return
    
    print("Connecting to Google Sheets...")
    try:
        gc = gspread.service_account(filename=CREDS_PATH)
        doc = gc.open_by_url(SHEET_URL)
        worksheet = doc.worksheet("Weapon")
        
        # Define Headers (mag_4 removed, added reload times and recommended columns)
        headers = [
            'name', 'name_kor', 'type', 'ammo', 
            'mag_0', 'mag_1', 'mag_2', 'mag_3', 
            'dmg', 'dmg_head', 'dmg_body', 'dmg_leg', 
            'RPM', 'DPS', 'Reload_time', 'Reload_time(Tactical)',
            'Projectile_Speed'
        ]
        
        # Convert data to rows
        rows = [headers]
        for item in data:
            row = [item.get(h, "-") for h in headers]
            rows.append(row)

        # Clear and Update
        print("Clearing and updating the sheet...")
        worksheet.clear()
        worksheet.update('A1', rows)
        
        # Formatting
        worksheet.format(f'A1:{chr(64+len(headers))}1', {
            "backgroundColor": {"red": 0.1, "green": 0.1, "blue": 0.1},
            "horizontalAlignment": "CENTER",
            "textFormat": {"foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}, "bold": True}
        })
        worksheet.freeze(rows=1)
        
        print(f"Update complete! Processed {len(data)} weapons.")
        
    except Exception as e:
        print(f"Failed to upload to Google Sheets: {e}")

if __name__ == "__main__":
    weapon_data = scrape_data()
    if weapon_data:
        upload_to_google_sheets(weapon_data)
