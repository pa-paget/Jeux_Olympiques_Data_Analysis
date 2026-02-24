import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
from io import StringIO

url = 'https://en.wikipedia.org/wiki/List_of_stripped_Olympic_medals'
headers = {'User-Agent': 'Mozilla/5.0'}

def clean_text(text):
    if isinstance(text, str):
        text = re.sub(r'\[.*?\]', '', text)
        return text.strip()
    return text

try:
    print("Accès à la page...")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    for td in soup.find_all('td'):
        classes = td.get('class', [])
        if not td.get_text(strip=True):
            if 'gold' in classes: td.string = "Gold"
            elif 'silver' in classes: td.string = "Silver"
            elif 'bronze' in classes: td.string = "Bronze"

    all_tables = pd.read_html(StringIO(str(soup)), attrs={'class': 'wikitable'})
    data_outputs = {}

    df_main = all_tables[0]
    
    if isinstance(df_main.columns, pd.MultiIndex):
        df_main.columns = [col[-1] for col in df_main.columns.values]
    
    new_names = ['Olympics', 'Athlete', 'Country', 'Medal', 'Event', 'Ref']
    current_cols = list(df_main.columns)
    for i in range(min(len(current_cols), len(new_names))):
        current_cols[i] = new_names[i]
    df_main.columns = current_cols
    
    data_outputs['Main_List'] = df_main.applymap(clean_text)


    for df in all_tables[1:]: 
        df_clean = df.applymap(clean_text)
        
        if isinstance(df_clean.columns, pd.MultiIndex):
            df_clean.columns = [col[-1] for col in df_clean.columns.values]
        
        cols_lower = [str(c).lower() for c in df_clean.columns]
        
        if 'country' in cols_lower:
            data_outputs['By_Country'] = df_clean
        elif 'sport' in cols_lower:
            data_outputs['By_Sport'] = df_clean
        elif 'gender' in cols_lower:
            data_outputs['By_Gender'] = df_clean

    output_filename = '../../data/data_raw/Olympic_Stripped_Medals_Country.xlsx'
    with pd.ExcelWriter(output_filename) as writer:
        for sheet_name, df in data_outputs.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"Onglet '{sheet_name}' ajouté.")

    print(f"\nSuccès ! Le fichier est prêt : {output_filename}")

except Exception as e:
    print(f"Une erreur est survenue : {e}")
