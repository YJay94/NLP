from konlpy.tag import Okt

okt = Okt()
tokens = okt.morphs("나는 자연어처리를 배운다")
print(tokens)