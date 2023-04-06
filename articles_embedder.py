import numpy
import openai
import sys
import json
from tqdm import tqdm
articles_path = "./articlesscrape_21372.txt"
substacks_path = "./stacks_json_good_final.txt"
checkpoint_path = "./embeddings_checkpoint_21372.txt"
load_checkpoint = False
articles = []
substacks = []
embeddings = []
max_retries = 2

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
        substacks.append(stack)
        currentSegment = ""
f.close()

f2 = open(articles_path, "r")
for line in f2:
    articles.append(eval(line.strip()))
f2.close()

start = 0
if load_checkpoint:
    f3 = open(checkpoint_path, "r")
    for line in f3:
        embedding = json.loads(line)["embedding"]
        embeddings.append(embedding)
        if substacks[len(embeddings)-1]["url"] != json.loads(line)["url"]:
            print("Error loading checkpoint: " + line)
            sys.exit(1)
    print("Loaded " + str(len(embeddings)) + " urls from checkpoint: " + checkpoint_path)
    start = len(embeddings)



def save_checkpoint(i):
    global embeddings
    f = open("embeddings_checkpoint_" + str(i) + ".txt", "w")
    
    for i in range(len(embeddings)):
        out = {}
        out["url"] = substacks[i]["url"]
        out["embedding"] = embeddings[i]
        f.write(json.dumps(out) + "\n")
    f.close()

f_key = open("../openai_key.txt", "r")
openai.api_key = f_key.read().strip()

def get_embedding(text):
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    embedding = response['data'][0]['embedding']
    return embedding

for i in tqdm(range(start, len(articles))):

    text = substacks[i]["name"] + "\n"
    for article in articles[i]:
        text += article + "\n"

    embedding = get_embedding(text)

    embeddings.append(embedding)

    if i % 200 == 0:
        save_checkpoint(i)

save_checkpoint(len(articles))