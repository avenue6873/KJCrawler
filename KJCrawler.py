# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import pymysql

# 유동적인 변수는 postfix v_로 구분

# MySQL Connection 연결
conn = pymysql.connect(host='kungjjak.cafe24.com', user='kungjjak', password='tkfkdgo0812^^', db='kungjjak', charset='utf8')

# MySQL Connection 후 Cursor 생성
curs = conn.cursor(pymysql.cursors.DictCursor)

# 쿼리 변수 대입
sql = "SELECT " \
          "COLCT_TRGET_ID, " \
          "INSTT_NM, " \
          "BBS_NM, " \
          "BASS_ADRES, " \
          "BBS_LIST_ADRES, " \
          "LIST_SELECTOR, " \
          "CONTENT_SELECTOR, " \
          "NOTICE_AT, " \
          "SUBJECT_LOC, " \
          "REGIST_DE_LOC, " \
          "CREAT_PNTTM, " \
          "UPDT_PNTTM " \
      "FROM TB_CRAWLER_TRGET"

# CURSOR에 쿼리 적재
curs.execute("set names utf8")
curs.execute(sql)

# 쿼리 결과 DATA FETCH
return_query = curs.fetchall()

# 반복문으로 row별로 출력
for row in return_query:
    # 결과 값을 해당 변수에 저장
    v_colct_trget_id = row['COLCT_TRGET_ID'] # 수집대상ID
    v_instt_nm = row['INSTT_NM'] # 기관명
    v_bbs_nm = row['BBS_NM'] # 게시판명
    v_bass_adres = row['BASS_ADRES'] # 기본주소
    v_bbs_list_adres = row['BBS_LIST_ADRES'] # 게시판목록주소
    v_list_selector = row['LIST_SELECTOR'] # 목록셀렉터
    v_content_selector = row['CONTENT_SELECTOR'] # 내용셀렉터
    v_notice_at = row['NOTICE_AT'] # 공지사항여부
    v_subject_loc = row['SUBJECT_LOC'] # 제목위치
    v_regist_de_loc = row['REGIST_DE_LOC'] # 등록일자위치
    v_creat_pnttm = row['CREAT_PNTTM'] # 등록일자
    v_updt_pnttm = row['UPDT_PNTTM'] # 수정일자

    # requests 객체에 url 세팅
    v_request = requests.get(v_bbs_list_adres)

    # 해당 url의 html을 가져옴
    v_bbs_list_html = v_request.content

    # 가져온 html 파싱
    v_parse_html = BeautifulSoup(v_bbs_list_html, 'html.parser')

    # 파싱한 html에서 셀렉터를 이용하여 게시물 목록만 리스트로 추출
    v_get_list = v_parse_html.select(v_list_selector)

    # 게시물 목록을 반복문을 통해 순차적으로 추출
    for row_data in v_get_list:
        # 공지사항여부가 N일 경우 그대로 목록 추출
        if v_notice_at == 'N' :
            # 게시물의 제목, 상세링크주소, 등록일자를 가져옴(이때 제목위치, 등록일자위치는 int형으로 형변환)
            v_subject = row_data.select('td')[int(v_subject_loc)].text
            v_detail_adres = row_data.find('a').get('href').replace('./', '')
            v_regist_de = row_data.select('td')[int(v_regist_de_loc)].text.replace('-','')

            # 상세화면 주소 조합
            v_trans_detail_adres = v_bass_adres + v_detail_adres

            # 상세내용 requests 객체 url 세팅
            v_detail_request = requests.get(v_trans_detail_adres)

            # 상세내용 url의 html을 가져옴
            v_detail_content = v_detail_request.content

            # 가져온 상세내용 html 파싱
            v_detail_parse_html = BeautifulSoup(v_detail_content, 'html.parser')

            # 파싱한 상세내용 html에서 셀렉터를 이용하여 상세내용의 텍스트만 추출
            v_get_content = v_detail_parse_html.select_one(v_content_selector).text

            print(v_colct_trget_id, v_subject, v_get_content, v_regist_de)

            # 가져온 데이터 MySQL DB에 저장
            curs.execute('INSERT INTO TB_CRAWLER_INFO (COLCT_TRGET_ID, SUBJECT, CONTENT, BBS_REGIST_DE, UPDT_PNTTM) VALUES (%s, %s, %s, %s, now())', (v_colct_trget_id, v_subject, v_get_content, v_regist_de))

            conn.commit()

# Connection 종료
conn.close()