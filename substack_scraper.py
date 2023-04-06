from bs4 import BeautifulSoup
import requests
import time
import json

startNode = "https://sashachapin.substack.com/"
max_iters = 100000
load_checkpoint = True
checkpoint_path = "./stacks_json_r5_final_edited.txt"

class StackData:
    def __init__(self, url, name, outlinks, n_subs):
        self.url = url
        self.name = name
        self.outlinks = outlinks
        self.n_subs = n_subs
    def __str__(self):
      return self.url + "," + self.name + "," + str(self.outlinks) + "," + str(self.n_subs)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

all_substacks = {}

to_visit = []
i=0
text = ""

if load_checkpoint:
    readingLinks = False
    f = open(checkpoint_path, "r")
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
            all_substacks[stack["url"]] = StackData(stack["url"], stack["name"], stack["outlinks"], stack["n_subs"])
            currentSegment = ""
        if "to_visit" in line:
            readingLinks = True
        elif readingLinks:
            if not line.strip() in to_visit:
                to_visit.append(line.strip())
    f.close()
    print("Loaded " + str(len(all_substacks)) + " stacks from checkpoint")
    print("Loaded " + str(len(to_visit)) + " visitable links from checkpoint")
    i = len(all_substacks)
else:
   to_visit.append(startNode)

def save_checkpoint(i):
    global all_substacks
    f = open("stacks_json_test_"+str(i)+".txt", "a")
    # f.write("[")
    for i in all_substacks:
        f.write(all_substacks[i].toJSON() + ",\n")
    # f.write("]")
    f.write("\nto_visit\n")
    for link in to_visit:
        f.write(link + "\n")
    f.close()

while len(to_visit) > 0 and i < max_iters:
    i += 1
    if i % 250 == 0:
        print("saving checkpoint with " + str(len(all_substacks)) + " pages and " + str(len(to_visit)) + " links to visit")
        save_checkpoint(i)
    url = to_visit.pop()
    if url in all_substacks:
        continue
    print("Visiting " + url)
    try:
        page = requests.get(url + "recommendations", headers = {'User-Agent': 'Googlebot'})
        soup = BeautifulSoup(page.content, 'html.parser')
        
        text = requests.get(url, headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_3_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}).content
        soup2 = BeautifulSoup(text, 'html.parser')
        
        name_elem = soup2.find("h1", {"class": "publication-name"})
        subs_elem = soup2.find("div", {"class" : "publication-meta"})
        if name_elem == None:
          name_elem = soup2.find("a", {"class": "navbar-title-link"})
        name = name_elem.text
        if name == "":
           name = soup2.find("title").text.split(" | ")[0]
        if not subs_elem == None:
          if "subscribers" in subs_elem.text:
            if not subs_elem.text.split(" ")[-2].replace(',', '') == "paid":
              n_subs = int(subs_elem.text.split(" ")[-2].replace(',', ''))
            # print(n_subs)
          else:
            n_subs = -1
        
        outlinks = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if href is not None and href.startswith("https://") and ".substack.com/?utm_source=recommendations_page" in href:
                href = href.split('?')[0].split('#')[0]
                outlinks.append(href)
                #print('adding a link:' + href)
                if not href in to_visit:
                    to_visit.append(href)
        all_substacks[url] = StackData(url, name, outlinks, n_subs)
    except Exception as e:
        print("Error visiting " + url + ": ")
        print(e)
        # print(text)
        time.sleep(10)
        if "Too Many" in str(text):
          to_visit.append(url)

# f = open("stacks_json.txt", "a")
# for i in all_substacks:
#     # print(all_substacks[i].toJSON())
#     f.write(all_substacks[i].toJSON() + "\n")
# f.close()

save_checkpoint("final")