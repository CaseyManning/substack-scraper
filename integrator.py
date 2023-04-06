import json
import sys
import numpy as np
import matplotlib.pyplot as plt

substacks = []
categories = []
embeddings = {}


substacks_path = "./stacks_json_good_final.txt"
categories_path = "./categories.txt"
embeddings_path = "./embeddings.txt"

def embeddings_pca(embeddings):
    embed_list = []
    for stack in substacks:
        embed_list.append(embeddings[stack["url"]])
    embed_list = np.array(embed_list)
    embed_list -= np.mean(embed_list, axis=0)
    embed_list /= np.std(embed_list, axis=0)
    # embed_list = embed_list.T
    # Z = np.dot(embed_list.T, embed_list)
    covariance_matrix = np.cov(embed_list.T)
    eigenvalues, eigenvectors = np.linalg.eig(covariance_matrix)
    # D = np.diag(eigenvalues)
    # P = eigenvectors
    # Z_new = np.dot(Z, P)
    # #get 2 principal components of each substack
    # Z_new = Z_new[:, 0:2]
    
    projection_matrix = (eigenvectors.T[:][:2]).T
    X_pca = embed_list.dot(projection_matrix)
    print(X_pca.shape)

    #plot the PCA data
    # plt.scatter(X_pca[:, 0], X_pca[:, 1])
    # plt.show()
    return X_pca
    


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

f2 = open(categories_path, "r")
for line in f2:
    categories.append(json.loads(line.strip()))
f2.close()

f3 = open(embeddings_path, "r")
for line in f3:
    embedding = json.loads(line)["embedding"]
    url = json.loads(line)["url"]
    embeddings[url] = np.array(embedding)
f3.close()

embed_PCA = embeddings_pca(embeddings)

print("Loaded " + str(len(substacks)) + " substacks")
print("Loaded " + str(len(categories)) + " categories")

minDist = 10
maxDist = 0

for i in range(len(substacks)):
    substacks[i]["category"] = categories[i]["category"]
    if substacks[i]["url"] != categories[i]["url"]:
        print("Error loading categories: " + substacks[i]["url"] + " != " + categories[i]["url"])
        sys.exit(1)
    substacks[i]["pca"] = embed_PCA[i].tolist()
    outlinks = substacks[i]["outlinks"]
    substacks[i]["outdists"] = []
    for j in range(len(outlinks)):
        if not outlinks[j] in embeddings:
            print("Error loading embedding: " + outlinks[j])
            dist = 0.65
        else:
            dist = np.linalg.norm(embeddings[substacks[i]["url"]] - embeddings[outlinks[j]])
        substacks[i]["outdists"].append(dist)
        if dist < minDist and dist > 0.05:
            minDist = dist
            print("min dist: " + str(minDist) + " " + substacks[i]["url"] + " " + outlinks[j])
        if dist > maxDist:
            maxDist = dist

f3 = open("integrated.txt", "w")
for stack in substacks:
    f3.write(json.dumps(stack) + ",\n")
f3.close()
print("min dist: " + str(minDist))
print("max dist: " + str(maxDist))
print("integrated into file: integrated.txt")