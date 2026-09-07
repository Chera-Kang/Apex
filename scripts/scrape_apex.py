import requests
from bs4 import BeautifulSoup
import json
import csv

def scrape_apex_weapons():
    url = "https://apexlegends.wiki.gg/wiki/Weapon"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    tables = soup.find_all('table', class_='wikitable')
    table = tables[1]
    rows = table.find_all('tr')
    
    # Extract headers with colspans
    header_info = []
    for row in rows:
        if row.find('th'):
            ths = row.find_all('th')
            header_info.append([(th.text.strip(), int(th.get('colspan', 1))) for th in ths])
        else:
            break
            
    # Flatten headers to get a list of column names
    # This is tricky because of multiple header rows.
    # We'll just hardcode the mapping based on our inspection.
    
    data = []
    weapon_rows = rows[len(header_info):]
    
    for i, row in enumerate(weapon_rows):
        cols = row.find_all('td')
        if not cols: continue
        
        try:
            name = cols[0].text.strip()
            w_type = cols[1].text.strip()
            # ... process with checks ...
            if len(cols) < 20:
                # Handle shorter rows (e.g. Care Package weapons or simplified rows)
                data.append({
                    "name": name,
                    "type": w_type,
                    "info": "Incomplete data in table"
                })
                continue

            ammo = cols[2].text.strip()
            modes = cols[3].text.strip()
            
            dmg_body = cols[4].text.strip()
            dmg_head = cols[5].text.strip()
            dmg_leg = cols[6].text.strip()
            
            rpm = cols[10].text.strip()
            dps = cols[11].text.strip()
            
            mag_base = cols[12].text.strip()
            mag_l3 = cols[15].text.strip()
            
            rel_tac_base = cols[16].text.strip()
            rel_tac_l3 = cols[19].text.strip()
            
            rel_full_base = cols[20].text.strip()
            rel_full_l3 = cols[23].text.strip()
            
            proj_speed = cols[24].text.strip() if len(cols) > 24 else "N/A"
            
            data.append({
                "name": name,
                "type": w_type,
                "ammo": ammo,
                "modes": modes,
                "damage_body": dmg_body,
                "damage_head": dmg_head,
                "damage_leg": dmg_leg,
                "rpm": rpm,
                "dps": dps,
                "mag_base": mag_base,
                "mag_l3": mag_l3,
                "reload_tac_base": rel_tac_base,
                "reload_tac_l3": rel_tac_l3,
                "reload_full_base": rel_full_base,
                "reload_full_l3": rel_full_l3,
                "projectile_speed": proj_speed
            })
        except Exception as e:
            print(f"Skipping row {i} ({cols[0].text.strip() if cols else 'unknown'}): {e}")
            continue
        
    return data

def save_data(data):
    with open('weapons_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    if data:
        # Get all unique keys from all dictionaries
        all_keys = set()
        for d in data:
            all_keys.update(d.keys())
        all_keys = sorted(list(all_keys))
        
        with open('weapons_data.csv', 'w', newline='', encoding='utf-8-sig') as f:
            dict_writer = csv.DictWriter(f, fieldnames=all_keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)

if __name__ == "__main__":
    data = scrape_apex_weapons()
    if data:
        save_data(data)
        print(f"Scraped {len(data)} weapons.")
