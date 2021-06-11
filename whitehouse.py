import requests
from bs4 import BeautifulSoup
from transformers import pipeline


url = 'https://www.whitehouse.gov/briefing-room/statements-releases/2021/05/21/u-s-rok-leaders-joint-statement/'
r = requests.get(url)
bs = BeautifulSoup(r.text)

bc = bs.find(attrs={'class': 'body-content'})
bct = bc.text

max_token = 1024
num_chunks = int(len(bct)/max_token)

summarizer = pipeline("summarization")
summary = ""
for i in range(num_chunks):
    chunk = bct[i*max_token:(i+1)*max_token]
    summary += summarizer(chunk)[0]['summary_text']
    pass


if __name__ == "__main__":
    pass

