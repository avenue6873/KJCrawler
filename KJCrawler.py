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
          "LIST_SUBJECT_XPATH, " \
          "DETAIL_SUBJECT_XPATH, " \
          "CONTENT_XPATH, " \
          "REGIST_DE_XPATH, " \
          "SUBJECT_KEYWORD, " \
          "LIST_CNT_XPATH," \
          "IF(LAST_COLCT_DE = '', '00000000', LAST_COLCT_DE) AS LAST_COLCT_DE," \
          "CREAT_PNTTM " \
      "FROM kjcrawler_web_trget " \
      "ORDER BY COLCT_TRGET_ID"

# CURSOR에 쿼리 적재
curs.execute("set names utf8")
curs.execute(sql)

# 쿼리 결과 DATA FETCH
return_query = curs.fetchall()

# 반복문으로 row별로 출력
for row in return_query:
    # 결과 값을 해당 변수에 저장 (조회결과변수)
    v_colct_trget_id = row['COLCT_TRGET_ID'] # 수집대상ID
    v_colct_instt_nm = row['COLCT_INSTT_NM'] # 수집기관명
    v_colct_bbs_nm = row['COLCT_BBS_NM'] # 수집게시판명
    v_colct_bbs_adres = row['COLCT_BBS_ADRES'] # 수집게시판주소
    v_list_subject_xpath = row['LIST_SUBJECT_XPATH'] # 목록제목XPATH
    v_detail_subject_xpath = row['DETAIL_SUBJECT_XPATH'] # 상세제목XPATH
    v_content_xpath = row['CONTENT_XPATH'] # 내용XPATH
    v_regist_de_xpath = row['REGIST_DE_XPATH'] # 등록일자XPATH
    v_list_cnt_xpath = row['LIST_CNT_XPATH']  # 게시물갯수XPATH
    v_subject_keyword = row['SUBJECT_KEYWORD'] # 제목키워드
    v_last_colct_de = row['LAST_COLCT_DE'] # 최종등록일자
    v_creat_pnttm = row['CREAT_PNTTM'] # 등록일자

    # 데이터 처리용 변수
    v_list_cnt = ''
    v_prefix_subject = '' # 제목 접두사
    v_suffix_subject = '' # 제목 접미사
    v_keyword_index = '' # 키워드 인덱스
    v_slash_index = '' # 제목 접미사 / 인덱스
    v_trans_subject_xpath = '' # 변환 제목XPATH

    # 크롤링 데이터 변수
    v_bbs_link_url = ''  # 게시물 링크 URL
    v_reg_de = '' # 등록일자
    v_subject = '' # 제목
    v_content = '' # 내용


    # 수집대상 게시판 목록 url 대입하여 driver 오픈
    driver.get(v_colct_bbs_adres)

    # chromedriver 2초 대기
    driver.implicitly_wait(2)

    # 게시물 갯수 조회
    v_list_cnt = len(driver.find_elements_by_xpath(v_list_cnt_xpath))

    # 목록제목 XPATH의 반복지점의 인덱스를 키워드로 추출
    v_keyword_index = v_list_subject_xpath.find(v_subject_keyword)

    # 목록제목 XPATH의 prefix를 추출
    v_prefix_subject = v_list_subject_xpath[:v_keyword_index]

    # 제목 접미사의 / 인덱스 추출
    v_slash_index = v_list_subject_xpath[v_keyword_index:].find('/')

    # 목록제목 XPATH의 suffix 추출 (키워드 인덱스와 접미사의 / 인덱스를 추출하여 더한 값으로 suffix 분리
    v_suffix_subject = v_list_subject_xpath[v_keyword_index + v_slash_index:]

    # 대상 게시판의 최근게시물 조회
    sql = '''SELECT COLCT_DATA_SUBJECT, COLCT_DATA_REGIST_DE  ''' \
            '''FROM KJCRAWLER_WEB_DATA ''' \
            '''WHERE COLCT_TRGET_ID = %s ''' \
            '''ORDER BY CREAT_PNTTM DESC'''

    # CURSOR에 쿼리 적재
    curs.execute("set names utf8")
    curs.execute(sql, (v_colct_trget_id))

    # 최근 게시물 1개만 가져옴
    result = curs.fetchone()

    # 게시물 목록 수 만큼 반복문 실행
    for cnt in range(1, v_list_cnt+1):
        # 수집대상 게시판 목록 url 대입하여 driver 오픈
        driver.get(v_colct_bbs_adres)

        # chromedriver 2초 대기
        driver.implicitly_wait(2)

        # 등록일자 추출
        v_reg_de = driver.find_element_by_xpath(v_regist_de_xpath.replace("tr[1]", v_subject_keyword + '[' + str(cnt) + ']')).text.replace('-', '').replace('/', '').replace('.', '')

        # 제목 XPATH 동적 변환
        v_trans_subject_xpath = v_prefix_subject + v_subject_keyword + '[' + str(cnt) + ']' + v_suffix_subject

        # 상세페이지 이동
        driver.find_element_by_xpath(v_trans_subject_xpath).click()

        # 현재 게시물의 주소를 변수에 담음
        v_bbs_link_url = driver.current_url

        # 제목 추출
        v_subject = driver.find_element_by_xpath(v_detail_subject_xpath)

        # 최근게시물 조회 결과가 없을 경우 반복문 진행
        if (result == None):
            # 내용 추출
            v_content = driver.find_element_by_xpath(v_content_xpath)
            print(v_reg_de)
            # 수집데이터 테이블에 데이터 INSERT
            curs.execute('INSERT INTO kjcrawler_web_data (COLCT_TRGET_ID, COLCT_DATA_SUBJECT, COLCT_DATA_CONTENT, '
                         'COLCT_LINK_ADRES, COLCT_DATA_REGIST_DE, CREAT_PNTTM) VALUES (%s, %s, %s, %s, %s, now())',
                         (v_colct_trget_id,
                          v_subject,
                          v_content,
                          v_bbs_link_url,
                          v_reg_de))

            #대상정보 테이블에 최종수집일자 업데이트
            curs.execute('UPDATE kjcrawler_web_trget SET LAST_COLCT_DE = %s WHERE COLCT_TRGET_ID = %s', (v_today, v_colct_trget_id))
        else:
            if(result['COLCT_DATA_SUBJECT'] != c_subject):
                # 내용 추출
                v_content = driver.find_element_by_xpath(v_content_xpath)

                # 수집데이터 테이블에 데이터 INSERT
                curs.execute('INSERT INTO kjcrawler_web_data (COLCT_TRGET_ID, COLCT_DATA_SUBJECT, COLCT_DATA_CONTENT, '
                             'COLCT_LINK_ADRES, COLCT_DATA_REGIST_DE, CREAT_PNTTM) VALUES (%s, %s, %s, %s, %s, now())',
                             (v_colct_trget_id,
                              v_subject,
                              v_content,
                              v_bbs_link_url,
                              v_reg_de))

                # 대상정보 테이블에 최종수집일자 업데이트
                curs.execute('UPDATE kjcrawler_web_trget SET LAST_COLCT_DE = %s WHERE COLCT_TRGET_ID = %s', (v_today, v_colct_trget_id))
            else:
                break

        conn.commit()

driver.quit()
