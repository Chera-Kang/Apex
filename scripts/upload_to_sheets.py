import pandas as pd
import gspread
import os

def upload_weapons_to_sheets():
    # 1. Load the CSV data
    csv_path = 'weapons_data.csv'
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # 2. Clean the data
    df_clean = df[df['info'] != 'Incomplete data in table'].copy()
    df_clean = df_clean.dropna(subset=['name'])
    df_clean = df_clean.fillna('')

    cols_order = [
        'name', 'type', 'ammo', 'modes', 
        'damage_body', 'damage_head', 'damage_leg', 
        'dps', 'rpm', 
        'mag_base', 'mag_l3', 
        'reload_tac_base', 'reload_tac_l3', 
        'reload_full_base', 'reload_full_l3', 
        'projectile_speed'
    ]
    available_cols = [c for c in cols_order if c in df_clean.columns]
    df_final = df_clean[available_cols]

    # 3. Connect to Google Sheets
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
        
        # Select the first worksheet
        worksheet = doc.get_worksheet(0)
        if not worksheet:
            worksheet = doc.add_worksheet(title="Weapon Data", rows="100", cols="20")

        # 4. Prepare data for upload
        header = [col.replace('_', ' ').title() for col in df_final.columns]
        values = [header] + df_final.values.tolist()

        # 5. Update the sheet
        print(f"Uploading {len(df_final)} rows...")
        worksheet.clear()
        worksheet.update('A1', values)
        
        # Basic Formatting (Column width and Header style)
        worksheet.format('A1:P1', {
            "backgroundColor": {"red": 0.15, "green": 0.15, "blue": 0.15},
            "horizontalAlignment": "CENTER",
            "textFormat": {"foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}, "bold": True}
        })
        
        print(f"Successfully uploaded to: {doc.title}")
        
    except Exception as e:
        import traceback
        print(f"An error occurred:\n{traceback.format_exc()}")

if __name__ == "__main__":
    upload_weapons_to_sheets()
