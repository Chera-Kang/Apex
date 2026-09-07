import requests
from bs4 import BeautifulSoup

def inspect_table_columns():
    url = "https://apexlegends.wiki.gg/wiki/Weapon"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    tables = soup.find_all('table', class_='wikitable')
    table = tables[1]
    rows = table.find_all('tr')
    
    # Let's find a row with full data, like HAVOC
    for row in rows:
        cols = row.find_all('td')
        if cols and 'HAVOC' in cols[0].text:
            print(f"Row for {cols[0].text.strip()}:")
            for i, col in enumerate(cols):
                print(f"Col {i}: {col.text.strip()}")
            break

if __name__ == "__main__":
    inspect_table_columns()
