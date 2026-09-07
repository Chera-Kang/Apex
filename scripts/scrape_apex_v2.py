import requests
from bs4 import BeautifulSoup
import json
import csv
import os

# Mapping English names to Korean names for Apex Legends weapons
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
    "Peacekeeper": "피스키퍼",
    "RE-45 Auto": "RE-45 오토",
    "P2020": "P2020",
    "Wingman": "윙맨",
    "Mozambique Shotgun Akimbo": "모잠비크 아킴보",
    "P2020 Akimbo": "P2020 아킴보",
    "RE-45 Auto Akimbo": "RE-45 아킴보"
}

def scrape_apex_weapons():
    url = "https://apexlegends.wiki.gg/wiki/Weapon"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    tables = soup.find_all('table', class_='wikitable')
    if len(tables) < 2:
        print("Error: Could not find the weapons table.")
        return []
        
    table = tables[1]
    rows = table.find_all('tr')
    
    data = []
    # Skip header rows (usually first 2-3 rows depending on the table structure)
    for i, row in enumerate(rows):
        cols = row.find_all('td')
        if not cols or len(cols) < 15: continue
        
        try:
            name_en = cols[0].text.strip()
            # Basic info
            w_type = cols[1].text.strip()
            
            # Ammo is often an image, we might need to get it from alt text or title
            ammo_img = cols[2].find('img')
            ammo = ammo_img['alt'] if ammo_img and 'alt' in ammo_img.attrs else ""
            if not ammo:
                ammo = cols[2].text.strip()

            # Damage
            dmg_body = cols[4].text.strip()
            dmg_head = cols[5].text.strip()
            dmg_leg = cols[6].text.strip()
            
            # RPM/DPS
            rpm = cols[10].text.strip()
            dps = cols[11].text.strip()
            
            # Magazines
            mag_0 = cols[12].text.strip()
            mag_1 = cols[13].text.strip()
            mag_2 = cols[14].text.strip()
            mag_3 = cols[15].text.strip()
            mag_4 = cols[16].text.strip() if len(cols) > 16 and i > 0 else "" # Check if L4 exists

            # Add to data
            data.append({
                "name": name_en,
                "name_kor": NAME_KOR_MAP.get(name_en, name_en),
                "type": w_type,
                "ammo": ammo,
                "mag_0": mag_0,
                "mag_1": mag_1,
                "mag_2": mag_2,
                "mag_3": mag_3,
                "mag_4": mag_4,
                "dmg": dmg_body, # Default dmg as body dmg
                "dmg_head": dmg_head,
                "dmg_body": dmg_body,
                "dmg_leg": dmg_leg,
                "RPM": rpm,
                "DPS": dps
            })
        except Exception as e:
            print(f"Skipping row {i}: {e}")
            continue
            
    return data

def save_data(data):
    if not data: return
    
    # Save to CSV
    keys = data[0].keys()
    with open('weapons_data_refined.csv', 'w', newline='', encoding='utf-8-sig') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    print(f"Saved {len(data)} weapons to weapons_data_refined.csv")

if __name__ == "__main__":
    weapons = scrape_apex_weapons()
    save_data(weapons)
