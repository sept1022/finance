from code_table import *

from bs4 import BeautifulSoup
import pandas as pd
import requests
import re
import progressbar

class CollectFinancialStatement:
    SUMMARY_URL_TEMPLATE = "https://companyinfo.stock.naver.com/v1/company/c1010001.aspx?cmp_cd={}"
    FINANCIAL_STATEMENT_URL_TEMPLATE = url = 'https://companyinfo.stock.naver.com/v1/company/ajax/cF1001.aspx?cmp_cd={}&fin_typ=4&freq_typ=Y&encparam={}&id={}'
    HEADERS = {"Referer": "HACK"}

    def __init__(self, code_table, output_directory, log_path):
        self.pat_enc = re.compile("encparam: '(.*)'", re.IGNORECASE)
        self.pat_id = re.compile("id: '([a-zA-Z0-9]*)' ?", re.IGNORECASE)
        self.code_table = code_table
        self.output_directory = output_directory
        self.logger = open(log_path + '/finance_statement_error.log', 'w')

    def get_financial_stetement(self, name):
        try:
            code = self.code_table.get_code(name)
            summary_url = CollectFinancialStatement.SUMMARY_URL_TEMPLATE.format(code)
            html = requests.get(summary_url).text
            encparam = self.pat_enc.search(html).group(1)
            encid = self.pat_id.search(html).group(1)

            url = CollectFinancialStatement.FINANCIAL_STATEMENT_URL_TEMPLATE.format(code, encparam, encid)
            html = requests.get(url, headers=CollectFinancialStatement.HEADERS).text

            # HTML 파싱
            soup = BeautifulSoup(html, "html5lib")
            result = soup.select("table > thead > tr:nth-of-type(2) > th")

            # DataFrame 변환
            df = pd.read_html(html)[1]
            df.columns = ["구분"] + [x.text.split()[0] for x in result]
            df = df.set_index('구분')
            df = df.applymap("{:.2f}".format)

            df.to_csv('{}/{}_{}.csv'.format(self.output_directory, name, code))
        except Exception as e:
            self.logger.write('[{}:{}] - {}\n'.format(name, code, e))


if __name__ == '__main__':
    code_table = CodeTable('../../data/data.csv')
    financial_statement = CollectFinancialStatement(code_table, '../../data/financial_statement/raw', '../../log')

    names = code_table.get_names()

    for page in progressbar.progressbar(range(1, len(names))):
        financial_statement.get_financial_stetement(names[page])
