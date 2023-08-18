from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager

from copy import deepcopy
import re
from time import sleep
import pandas as pd
# import requests

url_anvisa = 'https://consultas.anvisa.gov.br/#'
url_db = f'{url_anvisa}/bulario/q/'
lista_df = []

def start_driver(url):
    # Config Driver
    # option = webdriver.ChromeOptions()
    # For headless mode, the 2 lines below are required
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--incognito')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-dev-sh-usage')
    # options.add_argument('start-maximized')

    # Path to chromedriver 
    driver = webdriver.Chrome(service=Service(r'D:\pedro\Desktop\Challenge2023_SANOFI\chromedriver.exe'), options=options)


    driver.get(url)
    sleep(3)
    return driver




def main():
    driver = start_driver(url_db)
    driver
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    names_compounds = soup.select("a.ng-binding")
    codes_compounds = [str((drug.get('href').split('/')[-2])) for drug in names_compounds[2:-1]]
    names_compounds = [drug.text for drug in names_compounds[2:-1]]
    # [print(drug) for drug in names_compounds]
    # [print(code) for code in codes_compounds]

    name_code = list(zip(names_compounds,codes_compounds))
    # print(name_code)
    
    for i in range(0,len(name_code)):
        code = name_code[i][1]
        url_med = f'{url_anvisa}/medicamentos/{code}/'
        driver.get(url_med)
        sleep(2.5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        sub_names_compounds = soup.select("td.col-xs-4.ng-binding")
        # print(sub_names_compounds)
        
        # Filtering with regex
        # sub_names_compounds = [str(re.sub(r'\s*ATIVA\s*|\xa0\n\s*|CANCELADA OU CADUCA\s*', '', drug.text)).strip() for drug in sub_names_compounds]
        sub_names_compounds = [str(re.sub(r'\s*\xa0\n\s*|\s*\n\s*', '', drug.text)).strip() for drug in sub_names_compounds]
        sub_names_compounds = [drug.replace('ATIVA', ' --STATUS=ATIVA').replace('CANCELADA OU CADUCA', ' --STATUS=CANCELADA OU CADUCA') for drug in sub_names_compounds]
        # print(sub_names_compounds)

        # print(name_code[i][0])
        # [print('->', drug) for drug in sub_names_compounds]
        
        # princ_ativo = deepcopy(name_code[i][0])
        for drug in sub_names_compounds:
            lista_df.append({
                "Principio Ativo":[name_code[i][0]],
                "Nome": drug.replace(' --STATUS=ATIVA', '').replace('--STATUS=CANCELADA OU CADUCA', ''),
                "Status": (drug.split(' ').pop()).replace('--STATUS=', '')
            })
        # [print(item) for item in lista_df]
        lista_csv = [pd.DataFrame(d) for d in lista_df]
        lista_csv = pd.concat(lista_csv)
        print(lista_csv)
        lista_csv.to_csv('data_med.csv', index=False)
main()