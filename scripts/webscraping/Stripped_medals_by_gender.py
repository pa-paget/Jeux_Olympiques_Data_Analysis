import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import StringIO

url = 'https://en.wikipedia.org/wiki/List_of_stripped_Olympic_medals'
headers = {'User-Agent': 'Mozilla/5.0'}

try:
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # tableau par genre
    target_table = None
    for table in soup.find_all('table', {'class': 'wikitable'}):
        if "Gender" in table.get_text():
            target_table = table
            break

    if target_table:
        headers_html = target_table.find_all('th')
        for th in headers_html:
            img = th.find('img')
            if img:
                alt = img.get('alt', '')
                if "1" in alt: th.string = "Gold"
                elif "2" in alt: th.string = "Silver"
                elif "3" in alt: th.string = "Bronze"

        df_gender = pd.read_html(StringIO(str(target_table)), header=1)[0]

        df_gender.columns = [str(c).strip() for c in df_gender.columns]

        # Exportation vers CSV
        output_file = '../../data/data_raw/Olympic_Stripped_Medals_Gender.csv'
        df_gender.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"Fichier '{output_file}' généré ")
        print(df_gender.head())
    else:
        print("Tableau 'Gender' non trouvé.")

except Exception as e:
    print(f"Erreur : {e}")