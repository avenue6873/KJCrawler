# -*- coding: utf-8 -*-
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import pymysql
from datetime import datetime

# 현재날짜구해서 변수에 대입 YYYYmmdd 형태의 시간 출력
v_today = datetime.today().strftime("%Y%m%d")

# ChromeDriver Headless 모드 설정
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('1920x1080')
options.add_argument("--disable-gpu")

# 윈도우용 ChromeDriver Load
driver = webdriver.Chrome('C:\chromedriver\chromedriver.exe', chrome_options=options)

# 유동적인 변수는 postfix v_로 구분

# MySQL Connection 연결
conn = pymysql.connect(host='kungjjak.cafe24.com', user='kungjjak', password='tkfkdgo0812^^', db='kjcrawler', charset='utf8')

# MySQL Connection 후 Cursor 생성
curs = conn.cursor(pymysql.cursors.DictCursor)

# 쿼리 변수 대입
sql = "SELECT " \
          "COLCT_TRGET_ID, " \
          "COLCT_INSTT_NM, " \
          "COLCT_BBS_NM, " \
          "COLCT_BBS_ADRES, " \
          "SUBJECT_XPATH, " \
          "CONTENT_XPATH, " \
          "REGIST_DE_XPATH, " \
          "SUBJECT_TR_LOC, " \
          "SUBJECT_TD_LOC," \
          "CONTENT_TR_LOC," \
          "CONTENT_TD_LOC," \
          "LIST_CNT," \
          "IF(LAST_COLCT_DE = '', '00000000', LAST_COLCT_DE) AS LAST_COLCT_DE," \
          "CREAT_PNTTM " \
      "FROM kjcrawler_web_trget"

# CURSOR에 쿼리 적재
curs.execute("set names utf8")
curs.execute(sql)

# 쿼리 결과 DATA FETCH
return_query = curs.fetchall()

# 반복문으로 row별로 출력
for row in return_query:
    # 결과 값을 해당 변수에 저장
    v_colct_trget_id = row['COLCT_TRGET_ID'] # 수집대상ID
    v_colct_instt_nm = row['COLCT_INSTT_NM'] # 수집기관명
    v_colct_bbs_nm = row['COLCT_BBS_NM'] # 수집게시판명
    v_colct_bbs_adres = row['COLCT_BBS_ADRES'] # 수집게시판주소
    v_subject_xpath = row['SUBJECT_XPATH'] # 제목XPATH
    v_content_xpath = row['CONTENT_XPATH'] # 내용XPATH
    v_regist_de_xpath = row['REGIST_DE_XPATH'] # 등록일자XPATH
    v_subject_tr_loc = row['SUBJECT_TR_LOC'] # 제목행위치
    v_subject_td_loc = row['SUBJECT_TD_LOC'] # 제목열위치
    v_content_tr_loc = row['CONTENT_TR_LOC'] # 내용행위치
    v_content_td_loc = row['CONTENT_TD_LOC'] # 내용열위치
    v_list_cnt = row['LIST_CNT']  # 게시물갯수
    v_last_colct_de = row['LAST_COLCT_DE'] # 최종등록일자
    v_creat_pnttm = row['CREAT_PNTTM'] # 등록일자
    v_bbs_link_url = '' # 게시물 링크 URL

    for list_cnt in range(int(v_subject_tr_loc), int(v_list_cnt)+1, 1):
        # DB에서 가져온 XPATH 값을 게시물 수 만큼 동적 변경
        v_trans_subject_xpath = v_subject_xpath.replace("trn", str(list_cnt)).replace("tdn", v_subject_td_loc)

        # chromedriver 2초 대기
        driver.implicitly_wait(1)

        # 수집대상 게시판 목록 url 대입하여 driver 오픈
        driver.get(v_colct_bbs_adres)

        # 제목 추출하여 변수에 담음
        v_crawling_subject = driver.find_element_by_xpath(v_trans_subject_xpath).text

        # 상세페이지 이동
        driver.find_element_by_xpath(v_trans_subject_xpath).click()

        # 등록일자 추출하여 변수에 담음
        v_crawling_regist_de = driver.find_element_by_xpath(v_regist_de_xpath).text.replace("-", "").replace("/", "")

        # 수집하려는 데이터의 등록일자가 최종수집일자와 같거나 더 클 경우에만 수집하기 위함.
        if v_crawling_regist_de >= v_last_colct_de:

            # 현재 게시물의 주소를 변수에 담음
            v_colct_link_adres = driver.current_url

            # 내용xpath 변수 및 내용 변수 선언
            v_crawling_content = ""
            v_trans_content_xpath = ""

            # 내용 추출하여 변수에 담음 (td 값 존재에 따라 xpath가 달라지므로 if문 사용)
            if v_content_td_loc == 'X':
                v_trans_content_xpath = v_content_xpath.replace("trn", v_content_tr_loc)
                v_crawling_content = driver.find_element_by_xpath(v_trans_content_xpath).text
            else:
                v_trans_content_xpath = v_content_xpath.replace("trn", v_content_tr_loc).replace("tdn", v_content_td_loc)
                v_crawling_content = driver.find_element_by_xpath(v_trans_content_xpath).text

            # 수집데이터 테이블에 데이터 INSERT
            curs.execute('INSERT INTO kjcrawler_web_data (COLCT_TRGET_ID, COLCT_DATA_SUBJECT, COLCT_DATA_CONTENT, '
                         'COLCT_LINK_ADRES, COLCT_DATA_REGIST_DE, CREAT_PNTTM) VALUES (%s, %s, %s, %s, %s, now())', (v_colct_trget_id,
                                                                                               v_crawling_subject,
                                                                                               v_crawling_content,
                                                                                               v_colct_link_adres,
                                                                                               v_crawling_regist_de))

            # 대상정보 테이블에 최종수집일자 업데이트
            curs.execute('UPDATE kjcrawler_web_trget SET LAST_COLCT_DE = %s WHERE COLCT_TRGET_ID = %s', (v_today, v_colct_trget_id))

            conn.commit()

            print("제목 : " + v_crawling_subject + ", 등록일자 : " + v_crawling_regist_de + ", 내용 : " + v_crawling_content + ", 링크주소 : " + v_colct_link_adres)

driver.quit()
