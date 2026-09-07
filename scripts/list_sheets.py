import gspread
import os

from config import SHEET_URL, CREDS_PATH

def list_worksheets():
    creds_path = CREDS_PATH
    sheet_url = SHEET_URL
    
    gc = gspread.service_account(filename=creds_path)
    doc = gc.open_by_url(sheet_url)
    
    sheets = doc.worksheets()
    print(f"Worksheets: {[s.title for s in sheets]}")

if __name__ == "__main__":
    list_worksheets()
