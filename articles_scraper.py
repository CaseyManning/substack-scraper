import json
import time
from tqdm import tqdm
from bs4 import BeautifulSoup
import requests
substacks_path = "./stacks_json_test_final.txt"
urls = []
checkpoint_path = "./articlesscrape_21300.txt"
load_checkpoint = True
articles = []

f = open(substacks_path, "r")
currentSegment = ""
for line in f:
    line = line.replace("},", "}")
    currentSegment += line
    if "}" in line and len(line) < 3:
        try:
            stack = json.loads(currentSegment)
        except:
            print("Error loading stack: " + currentSegment)
            break
        urls.append(stack["url"])
        currentSegment = ""
f.close()
print("Loaded " + str(len(urls)) + " urls")

if load_checkpoint:
    f = open(checkpoint_path, "r")
    for line in f:
        articles.append(line.strip())
    f.close()
    print("Loaded " + str(len(articles)) + " article lists from checkpoint")

def save_checkpoint(i):
    global articles
    f = open("articlesscrape_" + str(i) + ".txt", "a")
    for list in articles:
        f.write(str(list) + "\n")
    f.close()

def scrape_articles(url):
    page = requests.get(url + "archive?sort=top")
    soup = BeautifulSoup(page.content, 'html.parser')
    articles = soup.find_all('a', class_='post-preview-title')
    if('Too Many Requests' in page.content.decode('utf-8')):
        time.sleep(13)
        return scrape_articles(url)
    return [article.text for article in articles]

for i in tqdm(range(len(articles), len(urls))):
    url = urls[i]
    articles.append(scrape_articles(url))
    if i % 100 == 0:
        save_checkpoint(i)

save_checkpoint(len(urls))