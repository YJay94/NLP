pip install beautifulsoup4

import os, re, csv
import requests
import urllib.request as ur
from bs4 import BeautifulSoup as bs

url = 'https://www.yna.co.kr/news?site=navi_latest_depth01'

html = ur.urlopen(url)
soup = bs(html.read(), 'html.parser')

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
print(sum_text)

# https://lovit.github.io/nlp/2019/04/30/textrank/ 참고하기

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

def word_graph(sents, tokenize=None, min_count=2, window=2, min_cooccurrence=2):
    idx_to_vocab, vocab_to_idx = scan_vocabulary(sents, tokenize, min_count)
    tokens = [tokenize(sent) for sent in sents]
    g = cooccurrence(tokens, vocab_to_idx, window, min_cooccurrence, verbose)
    return g, idx_to_vocab

import numpy as np
from sklearn.preprocessing import normalize

def pagerank(x, df=0.85, max_iter=30):
    assert 0 < df < 1

    # initialize
    A = normalize(x, axis=0, norm='l1')
    R = np.ones(A.shape[0]).reshape(-1,1)
    bias = (1 - df) * np.ones(A.shape[0]).reshape(-1,1)

    # iteration
    for _ in range(max_iter):
        R = df * (A * R) + bias

    return R

def textrank_keyword(sents, tokenize, min_count, window, min_cooccurrence, df=0.85, max_iter=30, topk=30):
    g, idx_to_vocab = word_graph(sents, tokenize, min_count, window, min_cooccurrence)
    R = pagerank(g, df, max_iter).reshape(-1)
    idxs = R.argsort()[-topk:]
    keywords = [(idx_to_vocab[idx], R[idx]) for idx in reversed(idxs)]
    return keywords

from collections import Counter
from scipy.sparse import csr_matrix
import math

def sent_graph(sents, tokenize, similarity, min_count=2, min_sim=0.3):
    _, vocab_to_idx = scan_vocabulary(sents, tokenize, min_count)

    tokens = [[w for w in tokenize(sent) if w in vocab_to_idx] for sent in sents]
    rows, cols, data = [], [], []
    n_sents = len(tokens)
    for i, tokens_i in enumerate(tokens):
        for j, tokens_j in enumerate(tokens):
            if i >= j:
                continue
            sim = similarity(tokens_i, tokens_j)
            if sim < min_sim:
                continue
            rows.append(i)
            cols.append(j)
            data.append(sim)
    return csr_matrix((data, (rows, cols)), shape=(n_sents, n_sents))

def textrank_sent_sim(s1, s2):
    n1 = len(s1)
    n2 = len(s2)
    if (n1 <= 1) or (n2 <= 1):
        return 0
    common = len(set(s1).intersection(set(s2)))
    base = math.log(n1) + math.log(n2)
    return common / base

def cosine_sent_sim(s1, s2):
    if (not s1) or (not s2):
        return 0

    s1 = Counter(s1)
    s2 = Counter(s2)
    norm1 = math.sqrt(sum(v ** 2 for v in s1.values()))
    norm2 = math.sqrt(sum(v ** 2 for v in s2.values()))
    prod = 0
    for k, v in s1.items():
        prod += v * s2.get(k, 0)
    return prod / (norm1 * norm2)

from summarizer import KeywordSummarizer

def textrank_keysentence(sents, tokenize, min_count, similarity, df=0.85, max_iter=30, topk=5):
    g = sent_graph(sents, tokenize, min_count, min_sim, similarity)
    R = pagerank(g, df, max_iter).reshape(-1)
    idxs = R.argsort()[-topk:]
    keysents = [(idx, R[idx], sents[idx]) for idx in reversed(idxs)]
    return keysents

pip install konlpy

from konlpy.tag import Komoran

komoran = Komoran()
def komoran_tokenize(sent):
    words = komoran.pos(sent, join=True)
    words = [w for w in words if ('/NN' in w or '/XR' in w or '/VA' in w or '/VV' in w)]
    return words

pip install git+https://github.com/lovit/textrank.git

from textrank import KeywordSummarizer

keyword_extractor = KeywordSummarizer(
    tokenize = komoran_tokenize,
    window = -1,
    verbose = False
)

from textrank import KeysentenceSummarizer
import pprint

summarizer = KeysentenceSummarizer(tokenize = komoran_tokenize, min_sim = 0.5)
keysents = summarizer.summarize(arr_sum_text, topk=10)
pprint.pprint(keysents)