from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
from time import sleep
import pandas as pd
import re

url_anvisa = 'https://consultas.anvisa.gov.br/#'
url_db = f'{url_anvisa}/bulario/q/'
lista_df = []

def start_driver(url):
    # Config Driver
    options = webdriver.FirefoxOptions()
    # For headless mode, the 2 lines below are required
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--incognito')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-dev-sh-usage')
    # options.add_argument('start-maximized')

    # Path to chromedriver 
    driver = webdriver.Firefox(options=options)

    driver.get(url)
    sleep(10)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    #find button 50
    element = driver.find_element(By.XPATH, '//*[@id="containerTable"]/div/div/div/div/button[3]')
    element.click()
    sleep(10)
    return driver

def nextPage(driver):
    driver
    element = driver.find_element(By.XPATH, '//*[@id="containerTable"]/div/div/div/ul/li[11]/a')
    element.click()
    sleep(10)
    
def recallPage(driver, page):
    driver
    driver.get(url_db)
    sleep(10)
    #find button 50
    element = driver.find_element(By.XPATH, '//*[@id="containerTable"]/div/div/div/div/button[3]')
    element.click()
    sleep(10)
    for temp_page in range(0, page):
        element = driver.find_element(By.XPATH, '//*[@id="containerTable"]/div/div/div/ul/li[11]/a')
        element.click()
        sleep(10)



def getPage(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    names_compounds = soup.select("a.ng-binding")
    codes_compounds = [str((drug.get('href').split('/')[-2])) for drug in names_compounds[2:-1]]
    names_compounds = [drug.text for drug in names_compounds[2:-1]]
    name_code = list(zip(names_compounds,codes_compounds))

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

def main():
    driver = start_driver(url_db)
    sleep(10)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    names_compounds = soup.select("a.ng-binding")
    codes_compounds = [str((drug.get('href').split('/')[-2])) for drug in names_compounds[2:-1]]
    names_compounds = [drug.text for drug in names_compounds[2:-1]]
    # [print(drug) for drug in names_compounds]
    # [print(code) for code in codes_compounds]

    name_code = list(zip(names_compounds,codes_compounds))
    # print(name_code)
    last_page = int(driver.find_element(By.XPATH, "/html/body/div[3]/div[1]/form/div/div[2]/div/div/div/ul/li[10]/a/span").text)

    
    for page in range(0,last_page - 1):
        print("Page", page + 1, sep=" ")
        getPage(driver)
        print("Page", page + 1, "END", sep=" ")
        print("-_"*100)
        recallPage(driver, page)
        nextPage(driver)
    

main()
