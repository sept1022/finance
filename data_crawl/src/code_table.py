#-*- coding: utf-8 -*-

import pandas as pd

class CodeTable:
    def __init__(self, path):
        #1. http://marketdata.krx.co.kr/contents/MKD/04/0406/04060100/MKD04060100.jsp에서 excel download -> csv 변환
        self.code_df = pd.read_csv(path)

        # code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0]
        #  종목코드가 6자리이기 때문에 6자리를 맞춰주기 위해 설정해줌

        self.code_df.종목코드 = self.code_df.종목코드.map('{:06d}'.format)
        # 우리가 필요한 것은 회사명과 종목코드이기 때문에 필요없는 column들은 제외해준다.
        self.code_df = self.code_df[['기업명', '종목코드']]
        # 한글로된 컬럼명을 영어로 바꿔준다.
        self.code_df = self.code_df.rename(columns={'기업명': 'name', '종목코드': 'code'})

    def get_code(self, name):
        code = self.code_df.query("name=='{}'".format(name))['code'].to_string(index=False)
        return code

    def get_name(self, code):
        name = self.code_df.query("code=='{}'".format(code))['name'].to_string(index=False)
        return name

    def get_names(self):
        return self.code_df.name.tolist()


if __name__ == "__main__":
    code_table = CodeTable('../../data/data.csv')

    print(code_table.code_df.head())
    print(code_table.get_code('삼성전자'))
    print(code_table.get_name(code_table.get_code('삼성전자')))

    print(code_table.get_names())

