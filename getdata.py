import requests
from bs4 import BeautifulSoup
import re

urlName = "https://fushinsha-joho.co.jp/serif.cgi?ym=202012"
url = requests.get(urlName)
list = []
soup = BeautifulSoup(url.content, "html.parser")
a = soup.find_all("a", class_="headline") 
for i in a:
  text = i.div.string.replace('\t','')
  text = re.findall("(?<=\「).+?(?=\」)", text)
  for x in text:
    list.append(x)
  

print(list)