import os
import sys
from pathlib import Path
import pandas as pd
import gspread

# 프로젝트 루트 및 scripts 경로 설정
CURRENT_DIR = Path(__file__).resolve().parent
BASE_DIR = CURRENT_DIR.parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from config import DATA_DIR, SHEET_URL, CREDS_PATH

def upload_weapons_to_sheets():
    # 1. Load the refined CSV data from data directory
    csv_path = DATA_DIR / 'weapons_data_refined.csv'
    if not csv_path.exists():
        print(f"Error: {csv_path} not found. Run apex_crawler.py first.")
        return

    try:
        df = pd.read_csv(csv_path)
        df = df.fillna('-')
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # 2. Connect to Google Sheets
    if not os.path.exists(CREDS_PATH):
        print(f"Error: {CREDS_PATH} not found. Check your config/.env settings.")
        return
    
    try:
        print("Connecting to Google Sheets...")
        gc = gspread.service_account(filename=CREDS_PATH)
        doc = gc.open_by_url(SHEET_URL)
        
        # Select or create the 'Weapon' worksheet
        try:
            worksheet = doc.worksheet("Weapon")
        except Exception:
            print("Worksheet 'Weapon' not found. Creating it...")
            worksheet = doc.add_worksheet(title="Weapon", rows="100", cols="25")

        # 3. Prepare data for upload
        # Headers matching the refined weapon data schema
        headers = [
            'name', 'name_kor', 'type', 'ammo', 
            'mag_0', 'mag_1', 'mag_2', 'mag_3', 
            'dmg', 'dmg_head', 'dmg_body', 'dmg_leg', 
            'RPM', 'DPS', 'Reload_time', 'Reload_time(Tactical)',
            'Projectile_Speed'
        ]
        
        # Filter dataframe for available headers
        available_headers = [h for h in headers if h in df.columns]
        if not available_headers:
            available_headers = list(df.columns)
            
        df_final = df[available_headers]
        values = [available_headers] + df_final.values.tolist()

        # 4. Update the sheet
        print(f"Updating 'Weapon' sheet with {len(df_final)} weapons...")
        worksheet.clear()
        worksheet.update(values=values, range_name='A1')
        
        # Basic Formatting
        col_letter = chr(64 + len(available_headers))
        worksheet.format(f'A1:{col_letter}1', {
            "backgroundColor": {"red": 0.1, "green": 0.1, "blue": 0.1},
            "horizontalAlignment": "CENTER",
            "textFormat": {"foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}, "bold": True}
        })
        
        # Freeze the first row
        worksheet.freeze(rows=1)
        
        print(f"Successfully updated 'Weapon' sheet in: {doc.title}")
        
    except Exception as e:
        import traceback
        print(f"An error occurred:\n{traceback.format_exc()}")

if __name__ == "__main__":
    upload_weapons_to_sheets()
