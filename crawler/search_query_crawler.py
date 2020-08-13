# 같은 폴더 안에 chromedriver.exe 위치시키기

from selenium import webdriver
import time
import re
import sys
import pandas as pd
import re

# 저장할 파일명 지정
f = open("query_table.csv", "w", encoding='utf-8')

# columns = [code, query, company, company_code] 헤더 지정하기
f.write('code_PK' + ',' + 'query' + ',' + 'original_query' + ',' + 'company' + ',' + 'company_code' + '\n')

# temp list
temp = []

#  초기 수집된 product(code).csv 불러오기
product_df = pd.read_csv('product(code).csv', encoding='cp949')

# product column에서 하나씩 가져와서 for문 돌리기

for i in range(len(product_df['product'])):
    print(product_df['product'][i])

    driver = webdriver.Chrome()

    # 제품명 column에서 하나씩 차례로 가져와서 쿼리 던짐
    query = product_df['product'][i]
    url = 'https://www.coupang.com/np/search?q='
    driver.get(url + query)
    time.sleep(5)
    try:
        # 수정된 검색어 가져오기
        search_query = driver.find_element_by_css_selector('div.search-query-result > p > span > strong').text
        search_query = re.search(r"^['](\w|[ ])+", search_query).group()
        search_query = search_query[1:]
        print(search_query)
    except:
        search_query = product_df['product'][i]
        print(search_query)

    # 검색어가 없으면 리스트에 저장
    if search_query not in temp:
        temp.append(search_query)

        # code_PK는 company_code+index(i)
        code_PK = product_df['companycode'][i] + str(i + 1)
        f.write(code_PK + ',' + search_query + ',' + product_df['product'][i] + ',' + product_df['company'][i] + ',' + product_df['companycode'][i] + '\n')
        print(code_PK + ',' + search_query + ',' + product_df['product'][i] + ',' + product_df['company'][i] + ',' + product_df['companycode'][i])

    driver.close()