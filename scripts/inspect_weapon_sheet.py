import gspread
import os

from config import SHEET_URL, CREDS_PATH

def inspect_weapon_sheet():
    creds_path = CREDS_PATH
    sheet_url = SHEET_URL
    
    gc = gspread.service_account(filename=creds_path)
    doc = gc.open_by_url(sheet_url)
    
    try:
        worksheet = doc.worksheet("Weapon")
        headers = worksheet.row_values(1)
        print(f"Headers in 'Weapon' sheet: {headers}")
        
        # Also check first data row to see values
        first_row = worksheet.row_values(2)
        print(f"First data row: {first_row}")
    except Exception as e:
        print(f"Error accessing 'Weapon' sheet: {e}")

if __name__ == "__main__":
    inspect_weapon_sheet()
