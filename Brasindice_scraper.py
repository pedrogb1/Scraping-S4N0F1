import requests
import json
from constants import URLS
from bs4 import BeautifulSoup
import concurrent.futures
import pandas as pd

def main():


    urls = [URLS.BRASINDICE.format(i) for i in range(0, 1000, 50)] # Gera os links
    
    with open('header.json', 'r') as f:
        headers = json.load(f)

    data = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        # Acessa todos os links paralelamente
        pages = list(executor.map(lambda url: make_request(url, headers), urls)) 
        # Extrai as informações das páginas paralelamente
        executor.map(lambda page: data.extend(extract_content_from_html(page)), pages)
    
   

    df = pd.DataFrame(
        {
            'Nome': data
        }
    )

    df['Principio Ativo'] = df['Nome'].str.extract('(([A-Z][\s]?[+-.]?[\s]?)+)')[0]
    df['Nome'] = df['Nome'].str.replace('(([A-Z][\s]?[+-.]?[\s]?)+)', '', regex=True)

    df.to_csv('data_med_brasindice.csv', index=False)


def make_request(url, headers):
    page = requests.get(url=url, headers=headers)
    return page


def extract_content_from_html(page):
    soup = BeautifulSoup(page.text, features="lxml")
    result = soup.find_all("a", {"class": "listViewTdLinkS1"})

    return [result[i].text for i in range(len(result)) if i%3==0]
    
main()