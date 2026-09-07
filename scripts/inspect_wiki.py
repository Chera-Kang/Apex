import requests
from bs4 import BeautifulSoup

url = "https://apexlegends.wiki.gg/wiki/Weapons"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)
print(f"Status Code: {response.status_code}")
print(f"HTML Preview: {response.text[:500]}")

soup = BeautifulSoup(response.text, 'html.parser')

# Look for all tables
tables = soup.find_all('table')

print(f"Found {len(tables)} tables.")

for i, table in enumerate(tables):
    print(f"\n--- Table {i} ---")
    headers = [th.text.strip() for th in table.find_all('th')]
    print(f"Headers: {headers[:10]}...") 
    
    rows = table.find_all('tr')
    for row in rows:
        tds = row.find_all('td')
        if tds:
            data = [td.text.strip() for td in tds]
            print(f"First data row: {data[:10]}...")
            break

