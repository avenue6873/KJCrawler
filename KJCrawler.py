# -*- coding: utf-8 -*-
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import pymysql
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException

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
          "REGIST_DE_KEYWORD, " \
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
    v_regist_de_keyword = row['REGIST_DE_KEYWORD'] # 등록일자키워드
    v_last_colct_de = row['LAST_COLCT_DE'] # 최종등록일자
    v_creat_pnttm = row['CREAT_PNTTM'] # 등록일자

    # 프로그램 내부 사용 변수
    p_subject_keyword_loc = v_list_subject_xpath.find(v_subject_keyword) # 목록 키워드 위치
    p_prefix_subject = v_list_subject_xpath[:p_subject_keyword_loc] # 목록 제목 접두사
    p_suffix_subject = v_list_subject_xpath[p_subject_keyword_loc:][v_list_subject_xpath[p_subject_keyword_loc:].find('/'):] #목록 제목 접미사
    p_subject_start_no = v_list_subject_xpath[p_subject_keyword_loc:][v_list_subject_xpath[p_subject_keyword_loc:].find('[')+1:v_list_subject_xpath[p_subject_keyword_loc:].find(']')] # 반복 시작 번호
    p_loop_subject = '' # 반복 제목 XPATH 생성 변수
    
    p_regist_loc = v_regist_de_xpath.find(v_regist_de_keyword) # 등록일자 키워드 위치
    p_prefix_regist_de = v_regist_de_xpath[:p_regist_loc] # 목록 등록일자 접두사
    p_suffix_regist_de = v_regist_de_xpath[p_regist_loc:][v_regist_de_xpath[p_regist_loc:].find('/'):] # 목록 등록일자 접미사
    p_loop_regist_de = '' # 반복 등록일자 XPATH 생성 변수

    # 수집데이터 변수
    c_regist_de = '' # 등록일자
    c_subject = '' # 상세 제목
    c_content = '' # 상세 내용

    # 수집대상 게시판 목록 url 대입하여 driver 오픈
    driver.get(v_colct_bbs_adres)

    # chromedriver 2초 대기
    driver.implicitly_wait(2)

    # 게시물 갯수 조회
    v_list_cnt = len(driver.find_elements_by_xpath(v_list_cnt_xpath))

    # 대상 게시판의 최근게시물 조회
    sql = '''SELECT COLCT_DATA_SUBJECT ''' \
            '''FROM KJCRAWLER_WEB_DATA ''' \
            '''WHERE COLCT_TRGET_ID = %s ''' \
            '''ORDER BY CREAT_PNTTM DESC ''' \
            '''LIMIT %s'''

    # CURSOR에 쿼리 적재
    curs.execute(sql, (v_colct_trget_id, v_list_cnt))

    # 최신 등록된 데이터를 게시물 개수만큼 가져옴
    result = curs.fetchall()

    # 게시물 목록 수 만큼 반복문 실행
    for cnt in range(int(p_subject_start_no), v_list_cnt+1):
        # 수집대상 게시판 목록 url 대입하여 driver 오픈
        driver.get(v_colct_bbs_adres)

        # chromedriver 1초 대기
        driver.implicitly_wait(1)

        # 등록일자 동적 XPATH 생성
        p_loop_regist_de = p_prefix_regist_de + v_regist_de_keyword + '[' + str(cnt) + ']' + p_suffix_regist_de

        # 제목 동적XPATH 생성
        p_loop_subject = p_prefix_subject + v_subject_keyword + '[' + str(cnt) + ']' + p_suffix_subject

        # 등록일자 추출 (element exception 오류 발생 대비)
        try:
            c_regist_de = driver.find_element_by_xpath(p_loop_regist_de).text.replace('-', '').replace('/','').replace('.','')

        except NoSuchElementException:
            c_regist_de = 'PASS'

        # 제목 클릭하여 상세페이지 이동
        driver.find_element_by_xpath(p_loop_subject).click()

        # 상세화면 제목 추출
        c_subject = driver.find_element_by_xpath(v_detail_subject_xpath).text

        # 상세화면 내용 추출
        c_content = driver.find_element_by_xpath(v_content_xpath).text

        # 현재 게시물의 주소를 변수에 담음
        c_bbs_link_url = driver.current_url

        # 목록에서 등록일자 추출 실패 시 상세에서 등록일자 가져옴
        if (c_regist_de == 'PASS'):
            c_regist_de = driver.find_element_by_xpath(v_regist_de_xpath).text

        # 기존 등록된 데이터 존재 유무에 따라 분기처리
        if(result is None):
            print('와우')
        else:
            # 조회된 데이터가 있을 경우 배열에 담음
            for sjcnt in result:
                print(result[sjcnt])

        # 등록일자 길이에 따라 날짜 형태가 다르므로 분기하여 처리
        if (len(c_regist_de) > 8):
            c_regist_de = c_regist_de[0:9]
        elif (len(c_regist_de) < 8 or c_regist_de is None):
            c_regist_de = v_today



        conn.commit()

driver.quit()
