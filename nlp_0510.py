pip install beautifulsoup4
import os, re, csv
import requests
import urllib.request as ur
from bs4 import BeautifulSoup as bs
url = 'https://www.yna.co.kr/news?site=navi_latest_depth01'
html = ur.urlopen(url)
soup = bs(html.read(), 'html.parser')
soup

headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebkit /537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36"}
r = requests.get("https://www.yna.co.kr/news?site=navi_latest_depth01/", headers=headers)

url = 'https://www.yna.co.kr/news?site=navi_latest_depth01'

html = ur.urlopen(url)

soup = bs(html.read(), 'html.parser')

import os, re

item = soup.find_all("div", class_="item-box01")

arr_title = []
arr_time = []
arr_href = []

for i in item:
	title = str(i.find_all("strong", class_="tit-news"))
	fit_title = re.sub('<.+?>', '', title, 0).strip()
	fit_title = re.sub('<.+?>', '', title, 0).strip()
	arr_title.append(fit_title)

	time = str(i.find_all("span", class_="txt-time"))
	fit_time = re.sub('<.+?>', '', time, 0).strip()
	arr_time.append(fit_time)

	href = str(i.find_all("a")[0].get("href"))
	fit_href = re.sub('<.+?>', '', href, 0).strip()
	arr_href.append(href)

	news_con = i.find_all("div", class_="news-con")
	  for k in news_con:	
    soup3 = bs(ur.urlopen('https:' + k.find_all("a")[0].get("href")).read(), 'html.parser')

  for j in soup3.find_all('p'):
    print(j.text)

  if(i == 3) :
    break;

print(list(zip(arr_title, arr_time, arr_href)))