import requests
from bs4 import BeautifulSoup

def inspect_first_row():
    url = "https://apexlegends.wiki.gg/wiki/Weapon"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    tables = soup.find_all('table', class_='wikitable')
    table = tables[1]
    rows = table.find_all('tr')
    
    # Print headers to see structure
    for i, row in enumerate(rows[:3]):
        cells = row.find_all(['th', 'td'])
        print(f"Row {i}: {[c.text.strip() for c in cells]}")
        
    # Print first data row cells
    for row in rows:
        if not row.find('th'):
            cells = row.find_all('td')
            print(f"First data row: {[c.text.strip() for c in cells]}")
            break

if __name__ == "__main__":
    inspect_first_row()
