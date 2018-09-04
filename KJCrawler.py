import requests
from bs4 import BeautifulSoup

rootAdres = "https://www.bucheon.go.kr/site/program/board/basicboard/"
req = requests.get("https://www.bucheon.go.kr/site/program/board/basicboard/list?boardtypeid=26736&menuid=148004001001")
allHtml = req.content

html = BeautifulSoup(allHtml, 'html.parser')

sj_list = html.select('tbody > tr > .td-lf > a')

for row in sj_list:
    # 링크변환
    transLink = rootAdres + row.get('href').replace("./", "")

    conReq = requests.get(transLink)

    conHtml = conReq.content

    contentHtml = BeautifulSoup(conHtml, 'html.parser')

    content = contentHtml.select_one(".board-cons").text

    print("[제목] : " + row.text.strip() + "\n[링크] : " + row.get('href').strip()+"\n[변환링크] : " + transLink + "\n[내용] : " + content + "\n\n")

