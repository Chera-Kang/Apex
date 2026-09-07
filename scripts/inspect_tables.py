import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_weapons():
    url = "https://apexlegends.wiki.gg/wiki/Weapon"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all tables with class 'wikitable'
    tables = soup.find_all('table', class_='wikitable')
    
    for i, table in enumerate(tables):
        headers = [th.text.strip() for th in table.find_all('th')]
        print(f"Table {i} headers: {headers[:10]}")
        
if __name__ == "__main__":
    scrape_weapons()
