from code_table import *
import requests
import pandas as pd
from bs4 import BeautifulSoup
import progressbar


class CollectStockPrice:
    PAGE_URL_TEMPLATE = 'http://finance.naver.com/item/sise_day.nhn?code={}'
    def __init__(self, code_table, output_directory, log_path):
        self.code_table = code_table
        self.output_directory = output_directory
        self.logger = open(log_path + '/stock_price.log', 'w')

    def get_url_and_max_page(self, name):
        code = self.code_table.get_code(name)
        url = CollectStockPrice.PAGE_URL_TEMPLATE.format(code)
        #print("요청 URL = {}".format(url))

        r = requests.get(url)
        source = BeautifulSoup(r.content, 'html.parser')
        max_page = source.find_all('table', align='center')
        max_page = max_page[0].find_all('td', class_='pgRR')
        max_page = max_page[0].a.get('href')

        return code, url, int(max_page[max_page.rfind('page=') + 5:])

    def get_stock_price(self, name):
        df = pd.DataFrame()
        code, url, max_page = self.get_url_and_max_page(name)

        for page in range(1, max_page + 1):
            pg_url = '{url}&page={page}'.format(url=url, page=page)
            df = df.append(pd.read_html(pg_url, header=0)[0], ignore_index=True)

        df.to_csv('{output_directory}/{name}_{code}.csv'.format(output_directory=self.output_directory, name=name, code=code))


if __name__ == '__main__':
    code_table = CodeTable('../../data/data.csv')
    collect_stock_price = CollectStockPrice(code_table, '../../data/stock_price/raw' ,'../../log')

    names = code_table.get_names()
    for page in progressbar.progressbar(range(1, len(names))):
        collect_stock_price.get_stock_price(names[page])

