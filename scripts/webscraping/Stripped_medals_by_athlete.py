import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import csv
import os # J'importe os pour manipuler les chemins de fichiers

# Je définis l'URL et les headers pour simuler un navigateur
url = 'https://en.wikipedia.org/wiki/List_of_stripped_Olympic_medals'
headers = {'User-Agent': 'Mozilla/5.0'}

try:
    # Je récupère le contenu HTML de la page
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Je cible le tableau de données principal
    table = soup.find('table', {'class': 'wikitable'})

    data = []
    # Ma mémoire pour gérer les cellules fusionnées (rowspan)
    memory = {'olympics': ['', 0], 'athlete': ['', 0], 'country': ['', 0]}

    # Je parcours chaque ligne du tableau
    for row in table.find_all('tr')[1:]:
        cells = row.find_all(['td', 'th'])
        if not cells: continue
        
        row_values = {}
        cell_ptr = 0 
        
        # --- ÉTAPE 1 : GESTION DES FUSIONS (Olympics, Athlete, Country) ---
        for col in ['olympics', 'athlete', 'country']:
            if memory[col][1] > 0:
                row_values[col] = memory[col][0]
                memory[col][1] -= 1
            else:
                cell = cells[cell_ptr]
                # Je nettoie les balises de saut de ligne pour éviter les décalages
                for br in cell.find_all(["br", "p", "li"]): br.replace_with(" ")
                val = " ".join(cell.get_text(" ", strip=True).split())
                row_values[col] = val
                rowspan = int(cell.get('rowspan', 1))
                if rowspan > 1:
                    memory[col] = [val, rowspan - 1]
                cell_ptr += 1 

        # --- ÉTAPE 2 : EXTRACTION DE LA MÉDAILLE (Image alt) ---
        medal_cell = cells[cell_ptr]
        img = medal_cell.find('img')
        medal = img.get('alt') if img else medal_cell.get_text(strip=True)
        cell_ptr += 1

        # --- ÉTAPE 3 : EXTRACTION DE L'ÉPREUVE (Event) ---
        event = " ".join(cells[cell_ptr].get_text(" ", strip=True).split())

        # --- ÉTAPE 4 : NETTOYAGE DU POINT-VIRGULE (Fix Excel) ---
        def clean(text):
            text = re.sub(r'\[.*?\]', '', text)
            # Je remplace le point-virgule par une virgule pour protéger mon CSV
            return text.replace(';', ',').strip()

        data.append([
            clean(row_values['olympics']), clean(row_values['athlete']), 
            clean(row_values['country']), clean(medal), clean(event)
        ])

    # --- ÉTAPE 5 : PRÉPARATION DU DATAFRAME ---
    df = pd.DataFrame(data, columns=['Olympics', 'Athlete', 'Country', 'Medal', 'Event'])
    df['Medal'] = df['Medal'].replace({"1": "Gold", "2": "Silver", "3": "Bronze"})

    # --- ÉTAPE 6 : CALCUL DU CHEMIN ABSOLU ---
    # Je récupère le dossier où se trouve ce script précisément
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    
    # Je construis le chemin vers le dossier data_raw à partir de ce script
    # Cela remonte bien de deux niveaux (../../) par rapport au script
    output_dir = os.path.join(script_dir, '..', '..', 'data', 'data_raw')
    output_file = os.path.join(output_dir, 'Olympic_Stripped_Athlete.csv')

    # Par sécurité, si le chemin calculé n'existe pas, je le crée
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # J'exporte avec guillemets pour protéger la structure
    df.to_csv(output_file, index=False, encoding='utf-8-sig', quoting=csv.QUOTE_NONNUMERIC)
    
    print(f"Réussite totale ! Le fichier est ici : {output_file}")

except Exception as e:
    print(f"Oups, une erreur est survenue : {e}")