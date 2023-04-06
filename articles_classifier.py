import openai
import sys
import json
from tqdm import tqdm
articles_path = "./articlesscrape_21372.txt"
substacks_path = "./stacks_json_good_final.txt"
checkpoint_path = "./classifier_checkpoint_21300.txt"
load_checkpoint = True
articles = []
substacks = []
classifications = []
categories = ["Tech", "Politics", "Business", "Sports", "Entertainment", "Finance", "Food", "Blockchain", "Science", "Personal", "Culture", "Other"]
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
        category = json.loads(line)["category"]
        if category not in categories:
            category = "Other"
        classifications.append(category)
        if substacks[len(classifications)-1]["url"] != json.loads(line)["url"]:
            print("Error loading checkpoint: " + line)
            sys.exit(1)
    print("Loaded " + str(len(classifications)) + " urls from checkpoint: " + checkpoint_path)
    start = len(classifications)



def save_checkpoint(i):
    global classifications
    f = open("classifier_checkpoint_" + str(i) + ".txt", "w")
    
    for i in range(len(classifications)):
        out = {}
        out["url"] = substacks[i]["url"]
        out["category"] = classifications[i]
        f.write(json.dumps(out) + "\n")
    f.close()

f_key = open("../openai_key.txt", "r")
openai.api_key = f_key.read().strip()

def get_category(prompt):
    response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[ {"role": "system", "content": prompt} ],
            temperature=0.5,
            max_tokens=5
        )
    category = response['choices'][0]['message']['content']
    return category

for i in tqdm(range(start, len(articles))):
    prompt = "The newsletter '" + substacks[i]["name"] + "' has the following articles:\n"
    for article in articles[i]:
        prompt += article + "\n"
    
    prompt += "Classify this newsletter into one of the following categories: "
    for cat in categories:
        prompt += cat + ", "
    prompt = prompt[:-2]
    prompt += "\n"
    prompt += "Output the category name as a single word with no other text."

    n_retry = 0
    category = get_category(prompt)
    if category == "Mixed":
        category = "Other"
    while category not in categories and n_retry < max_retries:
        n_retry += 1
        print("Retrying, got bad category: " + category)
        category = get_category(prompt)

    print(substacks[i]["name"] + " : " + category)
    category = category.replace(".", "")
    classifications.append(category)

    if i % 100 == 0:
        save_checkpoint(i)


save_checkpoint(len(classifications))