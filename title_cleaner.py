import json
import sys
from bs4 import BeautifulSoup
import requests
import time

substacks = []

substacks_path = "./integrated.txt"

f = open(substacks_path, "r")
currentSegment = ""
for line in f:
    line = line.replace("},", "}")
    try:
        stack = json.loads(line)
    except:
        print("Error loading stack: " + line)
        break
    substacks.append(stack)
f.close()

print("loaded: "  + str(len(substacks)) + " substacks")

for i in range(len(substacks)):
    if substacks[i]["name"] == "":

        page = requests.get(substacks[i]["url"] + "recommendations", headers = {'User-Agent': 'Googlebot'})
        soup = BeautifulSoup(page.content, 'html.parser')
        # print(soup.title.string)
        time.sleep(2)
        if soup.title:
            title = soup.title.string.split(" | ")[0]
            substacks[i]["name"] = title
            print("fixing bad name: " + substacks[i]["url"] + " as " + title)
        else:
            print("could not fix bad name: " + substacks[i]["url"])
            print(page.content)


f3 = open("cleaned.txt", "w")
for stack in substacks:
    f3.write(json.dumps(stack) + ",\n")
f3.close()

print("saving cleaned substacks to cleaned.txt")