import pandas as pd
import gspread
import os

def upload_weapons_to_sheets():
    # 1. Load the refined CSV data
    csv_path = 'weapons_data_refined.csv'
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found. Run scrape_apex_v2.py first.")
        return

    try:
        df = pd.read_csv(csv_path)
        df = df.fillna('')
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # 2. Connect to Google Sheets
    from config import SHEET_URL, CREDS_PATH
    creds_path = CREDS_PATH
    if not os.path.exists(creds_path):
        print(f"Error: {creds_path} not found.")
        return
    
    try:
        print("Connecting to Google Sheets...")
        gc = gspread.service_account(filename=creds_path)
        sheet_url = SHEET_URL
        doc = gc.open_by_url(sheet_url)
        
        # Select the 'Weapon' worksheet
        try:
            worksheet = doc.worksheet("Weapon")
        except Exception:
            print("Worksheet 'Weapon' not found. Creating it...")
            worksheet = doc.add_worksheet(title="Weapon", rows="100", cols="20")

        # 3. Prepare data for upload
        # Headers should match the Weapon sheet exactly
        headers = ['name', 'name_kor', 'type', 'ammo', 'mag_0', 'mag_1', 'mag_2', 'mag_3', 'mag_4', 'dmg', 'dmg_head', 'dmg_body', 'dmg_leg', 'RPM', 'DPS']
        
        # Reorder/filter dataframe to match headers
        # Use only headers that exist in both
        available_headers = [h for h in headers if h in df.columns]
        df_final = df[available_headers]
        
        values = [available_headers] + df_final.values.tolist()

        # 4. Update the sheet
        print(f"Updating 'Weapon' sheet with {len(df_final)} weapons...")
        worksheet.clear()
        worksheet.update('A1', values)
        
        # Basic Formatting
        worksheet.format('A1:O1', {
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
