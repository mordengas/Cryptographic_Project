quadgramsDict = {}

with open('english_quadgrams.txt', 'r', encoding='utf-8') as plik:
    for line in plik:
        line = line.strip()
        if not line:
            continue
        key, count = line.split(' ')
        key = key.lower()  # zamiana na małe litery
        quadgramsDict[key] = int(count)

def unify_letters(quadgram):
    return quadgram.replace('j', 'i').replace('v', 'w')

newDict = {}

for k in quadgramsDict:
    unified_key = unify_letters(k)
    if unified_key in newDict:
        newDict[unified_key] += quadgramsDict[k]
    else:
        newDict[unified_key] = quadgramsDict[k]

sorted_list = sorted(newDict.items(), key=lambda x: x[1], reverse=True)
sortedDictionary = dict(sorted_list)

with open('english_quadgrams_fixed.txt', 'w', encoding='utf-8') as plik:
    for k, v in sortedDictionary.items():
        plik.write(f"{k} {v}\n")