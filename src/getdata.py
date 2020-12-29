import requests
from bs4 import BeautifulSoup
import re
import pandas


def getData(type, data_list):
    list = []
    for i in data_list:
        urlName = "https://fushinsha-joho.co.jp/serif.cgi?ym=" + i
        url = requests.get(urlName)
        print(i + 'のデータを取得中…')
        if type == "joukyou":
            soup = BeautifulSoup(url.content, "html.parser")
            a = soup.find_all(style="font-size: 14px; line-height: 18px;")
            for i in a:
                text = i.string
                list.append(text)
        elif type == 'iti':
            soup = BeautifulSoup(url.content, "html.parser")
            a = soup.find_all(style="margin-top: 6px; font-size: 12px; line-height: 14px;")
            for i in a:
                text = i.string.replace('\t', '').replace('\n', '').replace('*', '')
                text = text.split(' ')[0]
                list.append(text)
        elif type == 'serihu':
            soup = BeautifulSoup(url.content, "html.parser")
            a = soup.find_all("a", class_="headline")
            for i in a:
                text = i.div.string.replace('\t', '')
                text = re.findall("(?<=\「).+?(?=\」)", text)
                for x in text:
                    list.append(x)
    return list


if __name__ == "__main__":
    print(getData('iti', pandas.date_range(start="2018-01", end="2021-01", freq="M").to_series().dt.strftime("%Y%m")))
