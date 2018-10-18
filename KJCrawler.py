# -*- coding: utf-8 -*-
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import pymysql
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException
from multiprocessing import Pool # 멀티프로세싱
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

p_start_time = time.time() # 시작시간 저장

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
    v_list_cnt = '' # 목록갯수

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

    p_subject_arr = [] # 최신등록된 게시물 조회 배열
    p_dupl_flag = 'N' # 데이터 중복 플래그

    # 수집데이터 변수
    c_regist_de = '' # 등록일자
    c_subject = '' # 상세 제목
    c_content = '' # 상세 내용

    # 수집대상 게시판 목록 url 대입하여 driver 오픈
    driver.get(v_colct_bbs_adres)

    # 크롬드라이버 2초대기
    driver.implicitly_wait(1)

    # 게시물 갯수 조회 
    v_list_cnt = len(driver.find_elements_by_xpath(v_list_cnt_xpath))

    # 게시물 갯수가 0일 경우 기본 10으로 세팅
    if(v_list_cnt == 0):
        v_list_cnt = 10
    
    print('수집기관명 : ' + v_colct_instt_nm + ', 게시물 갯수 : ' + str(v_list_cnt))
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

    # 조회된 데이터가 있을 경우 배열에 담음
    if(len(result) > 0):
        for sjdict in range(0, v_list_cnt):
            p_subject_arr.insert(sjdict, result[sjdict]['COLCT_DATA_SUBJECT'])
    
    # 게시물 목록 수 만큼 반복문 실행
    for cnt in range(int(p_subject_start_no), v_list_cnt+1):
        # 수집대상 게시판 목록 url 대입하여 driver 오픈
        driver.get(v_colct_bbs_adres)

        # 크롬드라이버 2초대기
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
        #if(v_colct_trget_id != 4):
        driver.find_element_by_xpath(p_loop_subject).click()
        #else:
        #    element = driver.find_element_by_xpath(p_loop_subject)
        #    element.submit()

        # 상세화면 제목 추출
        c_subject = driver.find_element_by_xpath(v_detail_subject_xpath).text
        print(c_subject)
        # 게시판 형식 중 첨부파일이 있을 경우 상세 내용보다 위에 위치할 경우 class 값으로 가져옴
        if(v_colct_trget_id == 1): # 부천시청(1)일 경우
            c_content = driver.find_element_by_class_name(v_content_xpath).text
        else:
            # 상세화면 내용 추출
            c_content = driver.find_element_by_xpath(v_content_xpath).text

        # 현재 게시물의 주소를 변수에 담음
        c_bbs_link_url = driver.current_url

        # 목록에서 등록일자 추출 실패 시 상세에서 등록일자 가져옴
        if (c_regist_de == 'PASS'):
            c_regist_de = driver.find_element_by_xpath(v_regist_de_xpath).text

        # 등록일자 길이에 따라 날짜 형태가 다르므로 분기하여 처리
        if (len(c_regist_de) > 8):
            c_regist_de = c_regist_de[0:9]
        elif (len(c_regist_de) < 8 or c_regist_de is None):
            c_regist_de = v_today

        # 기존 등록된 데이터 존재 유무에 따라 분기처리
        if(len(result) == 0):
            p_dupl_flag = 'N'
        else:
            # 조회된 데이터가 있을 경우 배열값과 추출한 제목 비교
            for sjlist in range(0, v_list_cnt):
                if(p_subject_arr[sjlist] == c_subject):
                    p_dupl_flag = 'Y'

        # 중복값이 존재하지 않을 경우 데이터 처리
        if(p_dupl_flag == 'N'):
            # 데이터 테이블 INSERT
            curs.execute('INSERT INTO kjcrawler_web_data (COLCT_TRGET_ID, COLCT_DATA_SUBJECT, COLCT_DATA_CONTENT, '
                         'COLCT_LINK_ADRES, COLCT_DATA_REGIST_DE, CREAT_PNTTM) VALUES (%s, %s, %s, %s, %s, now())',
                         (v_colct_trget_id,
                          c_subject,
                          c_content,
                          c_bbs_link_url,
                          c_regist_de))

            # 대상 테이블 UPDATE
            curs.execute('UPDATE kjcrawler_web_trget SET LAST_COLCT_DE = %s WHERE COLCT_TRGET_ID = %s',
                         (v_today, v_colct_trget_id))

        conn.commit()

driver.quit()
