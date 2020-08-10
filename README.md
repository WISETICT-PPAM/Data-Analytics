# 데이터 분석 팀 진행 방향
---
## Requirements
- selenium
- PyKoSpacing
  - https://github.com/haven-jeon/PyKoSpacing
- konlpy
- krwordrank
  - https://github.com/lovit/kr-wordrank
  
## Step1. 생리대 제품 리뷰 크롤링
- 오픈마켓(쿠팡) 웹사이트에서 생리대 제품의 리뷰를 크롤링하여 수집하고 DB에 저장
- 제품별로 최신순 리뷰 100개, 베스트순 리뷰 50개 총 150개 리뷰를 수집
'''python
review_cralwer.py
'''
## Step2. 텍스트 마이닝을 위한 리뷰 전처리
- 수집된 리뷰 데이터에서 특수문자, 숫자, 영문자, 한글 자음 및 모음만 있는 경우를 제거
- PyKoSpacing 라이브러리를 이용하여 맞춤법과 띄어쓰기 교정

## Step3. 리뷰 텍스트의 형태소 분석
- konlpy 라이브러리의 kkma(꼬꼬마 형태소 분석기)를 이용하여 리뷰 형태소 분석

## Step4. 제품 키워드 풀(pool) 구축
- Referenced Code
  - https://github.com/lovit/kr-wordrank
- krwordrank 라이브러리를 이용하여 15개 제품의 제품별 리뷰에서 키워드를 추출
- 추출된 키워드를 검사하여 불용어(ex. 생리대, 사용, 구매, 배송 등) 및 동의어 등을 제거하고 약 50개의 키워드를 포함한 키워드 풀(pool) 구축

## Step5. 제품별 특성 키워드 선정



## Step6. 해당 키워드를 포함하는 리뷰 선별 
