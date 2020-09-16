import pymysql
from selenium import webdriver
import time
import re
import sys
import pandas as pd
import urllib.request

# db connection
conn = pymysql.connect(host="ppam.ceubmhz1zgkv.ap-northeast-1.rds.amazonaws.com",user = "admin",password ="ppam1234", db="ppam_test",charset="utf8")
curs = conn.cursor(pymysql.cursors.DictCursor)

curs.execute("DROP TABLE post_table")

sql ='''
        CREATE TABLE post_table(
        post_code VARCHAR(10) NOT NULL,
        post_name VARCHAR(100) NOT NULL,
        post_url VARCHAR(500) NOT NULL,
        product_name VARCHAR(50),
        size VARCHAR(20),
        image_name VARCHAR(20)
        )CHARSET = utf8;
    '''    
curs.execute(sql)
conn.commit()

# 검색어 테이블 불러오기
search_table = pd.read_sql("select * from search_table", conn)
search_table.info()


#%%

# 크롤링 데이터 저장하는 리스트
post_code_list = []
post_name_list = []
post_url_list = []
image_name_list = []


for i in range(len(search_table)):
    driver = webdriver.Chrome(r"C:\Users\이다혜\Desktop\crawling_DB\chromedriver.exe")
    # 수정된 검색어 가져와서 검색
    search = search_table['search'][i]
    url = 'https://www.coupang.com/np/search?q='
    driver.get(url + search)
    time.sleep(5)
    # 판매량순으로 3개까지 수집
    # 판매량순 버튼 클릭
    try:
        best_sales_btn = driver.find_element_by_css_selector('ul.sorting-order-options li:nth-of-type(4)')
        best_sales_btn.click()
    except:
        continue
    time.sleep(5)
    # 판매량 순으로 게시글 3개까지 클릭 - 게시글 없는 경우는 패스
    try:
        con = driver.find_elements_by_css_selector('#productList li')
    except:
        continue

    for j in range(1,4):
        try:
            con[j].click()
        except:
            continue
        time.sleep(5)
        # 창 바꿔줘야 선택자 찾을 수 있다
        try:
            window_after = driver.window_handles[1]
            driver.switch_to.window(window_after)
        except:
            continue
        # 게시글 이름 수집 - 상세페이지가 제대로 불러와지지 않을 경우 에러 처리
        try:
            post_name = driver.find_element_by_css_selector('div.prod-buy-header > h2').text
        except:
            continue
        
        #post_code = query_code + 게시글 번호(1~3)
        post_code = search_table['search_code'][i] + '-' + str(j)
        
        # 게시글 URL 수집
        post_url = driver.current_url
        
        # 게시글 이미지 수집
        # imgsrc = driver.find_element_by_css_selector('#repImageContainer > img')
        # imgsrc = imgsrc.get_attribute('src')
        # urllib.request.urlretrieve(imgsrc, 'imgs/' + post_code + '.jpg')
        image_name = post_code +'.jpg'
        
        # print(post_code + ',' + post + ',' + url + ',' + 'product' + ',' + 'size' + ',' + 'image' + ',' + search_code + '\n')
        # f.write(post_code+ ',' + post + ',' + url + ',' + 'product' + ',' + 'size' + ',' + 'image' + ',' + search_code + '\n')
        
        # print(post_code, post_name, post_url, image_name)
        post_code_list.append(post_code)
        post_name_list.append(post_name)
        post_url_list.append(post_url)
        image_name_list.append(image_name)
        
        driver.close()
        window_before = driver.window_handles[0]
        driver.switch_to.window(window_before)
    driver.close()
    
    

#%%
# 수집 끝나면 DB에 넣기
for i in range(len(post_name_list)):
    sql ='''INSERT INTO ppam_test.post_table (post_code, post_name, post_url, image_name) 
            VALUES(%s,%s,%s,%s);'''
    val = (post_code_list[i], post_name_list[i], post_url_list[i], image_name_list[i]) 
    curs.execute(sql,val)

conn.commit()


