# -*- coding: utf-8 -*-
"""Untitled9.ipynb의 사본

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/13IeT87X2LpNtoPZAeFfOe3ry0NQmCwl9
"""

import pprint
import os, re, csv
import requests
import urllib.request as ur
from bs4 import BeautifulSoup as bs

url = 'https://www.yna.co.kr/news?site=navi_latest_depth01'

html = ur.urlopen(url)
# soup = bs(html.read(), 'html.parser')
soup = bs(html, "lxml")

soup

headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36"}
r = requests.get("https://www.yna.co.kr/news?site=navi_latest_depth01/", headers=headers)

item = soup.find_all("div", class_="item-box01")

arr_title = []
arr_time = []
arr_href = []
arr_text = []

count = 0
limit_num = 2 # 최신기사 limit_num개 단위만 사용(limit_num개 이상 넘어가면 속보 의미 없음)
for i in item:  
  count += 1  
  if(count == limit_num):  
    break
  title = str(i.find_all("strong", class_="tit-news"))
  fit_title = re.sub('<.+?>', '', title, 0).strip()
  fit_title = re.sub('<.+?>', '', title, 0).strip()
  arr_title.append(fit_title)
  # print(fit_title)

  time = str(i.find_all("span", class_="txt-time"))
  fit_time = re.sub('<.+?>', '', time, 0).strip()
  arr_time.append(fit_time)
  # print(fit_time)

  href = str(i.find_all("a")[0].get("href"))
  fit_href = re.sub('<.+?>', '', href, 0).strip()
  arr_href.append(href)

  news_con = i.find_all("div", class_="news-con")
  
  for k in news_con:
    k_url = 'https:' + k.find_all("a")[0].get("href")
    k_html = ur.urlopen(k_url)
    soup3 = bs(k_html.read(), 'html.parser')

  count_j = 0
  # print(len(soup3.find_all('p')))
  sum_text = ''
  arr_sum_text = []
  for j in soup3.find_all('p'):
    count_j += 1
    if(count_j >= 1 and count_j <= 6):
      continue
    if(count_j >= len(soup3.find_all('p'))-1):
      continue
    # print(count_j)
    # print(j.text)
    sum_text += j.text 
    arr_sum_text.append(str(j.text))

  arr_text.append(sum_text)

  if(i == 3) :
    break;
  
# print(arr_title)
arr_zip = zip(arr_title, arr_time, arr_href, arr_text)
# print(len(list(arr_zip)))
# print(list(arr_zip))
# print(arr_text)
# print(sum_text)
pprint.pprint(arr_text)

# https://lovit.github.io/nlp/2019/04/30/textrank/ 참고하기

pip install konlpy

import nltk
nltk.download('punkt')

from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords


# 문장 토큰화
for i in arr_text:
  sentences = sent_tokenize(i)
  pprint.pprint(sentences)

from konlpy.tag import Okt  

okt = Okt()  
tokens = okt.morphs(sum_text)  
print(tokens)

from collections import Counter

def scan_vocabulary(sents, tokenize, min_count=2):
    counter = Counter(w for sent in sents for w in tokenize(sent))
    counter = {w:c for w,c in counter.items() if c >= min_count}
    idx_to_vocab = [w for w, _ in sorted(counter.items(), key=lambda x:-x[1])]
    vocab_to_idx = {vocab:idx for idx, vocab in enumerate(idx_to_vocab)}
    return idx_to_vocab, vocab_to_idx

from collections import defaultdict

def cooccurrence(tokens, vocab_to_idx, window=2, min_cooccurrence=2):
    counter = defaultdict(int)
    for s, tokens_i in enumerate(tokens):
        vocabs = [vocab_to_idx[w] for w in tokens_i if w in vocab_to_idx]
        n = len(vocabs)
        for i, v in enumerate(vocabs):
            if window <= 0:
                b, e = 0, n
            else:
                b = max(0, i - window)
                e = min(i + window, n)
            for j in range(b, e):
                if i == j:
                    continue
                counter[(v, vocabs[j])] += 1
                counter[(vocabs[j], v)] += 1
    counter = {k:v for k,v in counter.items() if v >= min_cooccurrence}
    n_vocabs = len(vocab_to_idx)
    return dict_to_mat(counter, n_vocabs, n_vocabs)

from scipy.sparse import csr_matrix

def dict_to_mat(d, n_rows, n_cols):
    rows, cols, data = [], [], []
    for (i, j), v in d.items():
        rows.append(i)
        cols.append(j)
        data.append(v)
    return csr_matrix((data, (rows, cols)), shape=(n_rows, n_cols))