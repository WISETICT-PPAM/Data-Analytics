import pymysql
from selenium import webdriver
import time
import re
import sys
import pandas as pd
import urllib.request
# from .review_crawler import review_crawler


# db connection
conn = pymysql.connect(host="ppam.ceubmhz1zgkv.ap-northeast-1.rds.amazonaws.com",user = "admin",password ="ppam1234", db="ppam_test",charset="utf8")
curs = conn.cursor(pymysql.cursors.DictCursor)


sql ='''
        CREATE TABLE review_table(
        review_code VARCHAR(15) NOT NULL,
        review_date VARCHAR(8) NOT NULL,
        review_raw VARCHAR(2000) NOT NULL,
        review_cleaned VARCHAR(2000),
        PRIMARY KEY(review_code))CHARSET = utf8;
    '''    
curs.execute(sql)
conn.commit()


# 검색어 테이블에서 post_code, post_url 불러오기
post_table = pd.read_sql("select * from post_table", conn)
post_table.info()

#%%
# 리뷰 크롤러 함수 정의
def review_crawling(post_url, post_code):
    # 상세페이지 접속
    driver = webdriver.Chrome(r"C:\Users\이다혜\Desktop\crawling_DB\chromedriver.exe")
    driver.get(post_url)
    time.sleep(5)

    # 상품평 버튼 보이게 스크롤바 내리기
    for i in range(200, 2000, 200):
        driver.execute_script('window.scrollTo(0,i)')
        try:
            # 상품평 버튼 클릭
            review_button = driver.find_element_by_css_selector('div#btfTab ul.tab-titles > li:nth-of-type(2)')
            review_button.click()
            time.sleep(10)

            # 최신순 보기 버튼 눌러지는지 확인
            new_review_button = driver.find_element_by_css_selector(
                'button.sdp-review__article__order__sort__newest-btn.js_reviewArticleNewListBtn.js_reviewArticleSortBtn')
            new_review_button.click()
            time.sleep(10)
            break
        except:
            pass

    # 베스트 리뷰 버튼 누르기
    best_review_button = driver.find_element_by_css_selector(
        'button.sdp-review__article__order__sort__best-btn.js_reviewArticleHelpfulListBtn.js_reviewArticleSortBtn')
    best_review_button.click()
    time.sleep(5)

    # 베스트 리뷰 50개 크롤링
    review_code_list = []
    review_date_list = []
    review_list = []
    cnt = 1
    for i in range(1, 11):
        container = driver.find_elements_by_css_selector("section.js_reviewArticleListContainer article")
        for con in container:
            # 작성 날짜
            date = con.find_element_by_css_selector(
                'div.sdp-review__article__list__info__product-info__reg-date').text.replace('.', '')
            # 리뷰 내용
            try:
                review = con.find_element_by_css_selector(
                    'div.sdp-review__article__list__review.js_reviewArticleContentContainer').text.replace('\n', ' ')
                review = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', '', review)
                
                print(date + ',' + review + ',' + str(cnt))
                review_code = post_code + '-' + str(cnt)
                review_code_list.append(review_code)
                review_date_list.append(date)
                review_list.append(review)
                
                cnt += 1
            except:
                pass
        try:
            page_button = driver.find_element_by_css_selector(
                'div.sdp-review__article__page.js_reviewArticlePagingContainer > button:nth-child(' + str(i + 2) + ')')
            page_button.click()
            time.sleep(3)
        except:
            break

    
    # 최신순 보기 버튼 누르기
    new_review_button = driver.find_element_by_css_selector(
        'button.sdp-review__article__order__sort__newest-btn.js_reviewArticleNewListBtn.js_reviewArticleSortBtn')
    new_review_button.click()
    time.sleep(5)
    
    cnt_new = 1
    for i in range(1, 100):
        # 리뷰 컨테이너 선택
        container = driver.find_elements_by_css_selector("section.js_reviewArticleListContainer article")
        for con in container:
            try:
                if cnt_new == 101:
                    print('100개 수집 완료')
                    break
                # 작성 날짜
                date = con.find_element_by_css_selector(
                    'div.sdp-review__article__list__info__product-info__reg-date').text.replace('.', '')
                # 리뷰 내용
                review = con.find_element_by_css_selector(
                    'div.sdp-review__article__list__review.js_reviewArticleContentContainer').text.replace('\n', ' ')
                review = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', '', review)
                print(date + ',' + review + ',' + str(cnt_new))
                
                
                review_code = post_code + '-' + str(cnt)
                review_code_list.append(review_code)
                review_date_list.append(date)
                review_list.append(review)
                cnt_new += 1
                cnt += 1
                
            except:
                pass
            
        if cnt_new == 101:
            print('100개 수집 완료, 종료')
            break
        
        # 다음 페이지 버튼 있는지 확인
        try:
            page_button = driver.find_element_by_css_selector(
                'div.sdp-review__article__page.js_reviewArticlePagingContainer > button:nth-child(' + str(i % 11 + 2) + ')')
            page_button.click()
            time.sleep(3)
        # 없어서 에러 나면 최신순 리뷰 수집 종료
        except:
            print('100개 미만 수집완료')
            break
    
    driver.close()
    return review_code_list, review_date_list, review_list  # 전체 리스트를 리턴

#%%

# for문 돌면서 해당 url에 접속해서 리뷰 가져오기
review_codes = []
review_dates = []
reviews = []

# 전체 게시글 개수 : 468개 -> 100개씩 끊어서 돌리기 
len(post_table)

for i in range(100):
    review_code_list, review_date_list, review_list = review_crawling(post_table['post_url'][i], post_table['post_code'][i])
    review_codes += review_code_list
    review_dates += review_date_list
    reviews += review_list
    
    
#%% 수집 완료되면 DB에 넣기
for i in range(len(reviews)):
    sql ='''INSERT INTO ppam_test.review_table (review_code, review_date, review_raw) 
            VALUES(%s,%s,%s);'''
    val = (review_codes[i], review_dates[i], reviews[i]) 
    curs.execute(sql,val)

conn.commit()
