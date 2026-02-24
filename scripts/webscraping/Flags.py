import requests
from bs4 import BeautifulSoup
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

url = "https://fr.wikipedia.org/wiki/Liste_des_codes_pays_du_CIO"
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# On cherche TOUS les tableaux de classe wikitable
tables = soup.find_all('table', {'class': 'wikitable'})

liste_pays = []

for table in tables:
    # On parcourt chaque ligne de chaque tableau
    for row in table.find_all('tr')[1:]:
        cols = row.find_all(['td', 'th'])
        if len(cols) >= 2:
            code = cols[0].get_text(strip=True)
            # Nettoyage du nom (certains ont des années comme "Grèce (1896-)")
            nom_pays = cols[1].get_text(strip=True)
            
            # Extraction du drapeau
            img_tag = cols[1].find('img')
            url_drapeau = ""
            if img_tag and img_tag.get('src'):
                # On récupère une image un peu plus grande (100px au lieu de 20px)
                url_drapeau = "https:" + img_tag['src'].replace('20px', '100px')

            liste_pays.append({
                "code_cio": code,
                "nom_pays": nom_pays,
                "url_drapeau": url_drapeau
            })

# Sauvegarde
with open('../../data/data_raw/codes_cio_new_test.json', 'w', encoding='utf-8') as f:
    json.dump(liste_pays, f, ensure_ascii=False, indent=4)

print(f"Succès ! {len(liste_pays)} pays extraits dans 'codes_cio.json'.")