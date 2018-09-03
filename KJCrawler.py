import requests
from bs4 import BeautifulSoup

req = requests.get("https://www.jobaba.net/fntn/dtl.do?seq=5153")
allHtml = req.content

html = BeautifulSoup(allHtml, "html.parser")

p = html.find("p", {"class":"alam-area"})
div = html.find("div", {"class":"data-sec01"})

subject = p.text
content = div.text

print("제목1 : " + subject)
print("내용 : " + content)
