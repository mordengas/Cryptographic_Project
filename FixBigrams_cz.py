ngramsDict = {}

with open('czech_bigrams.txt', 'r', encoding='utf-8') as plik:
    for line in plik:
        key, count = line.strip().split(' ')
        ngramsDict[key.lower()] = int(count)

newDict = {}

def unify_letters(bigram):
    return bigram.replace('ó', 'o')

for k in ngramsDict:
    unified_key = unify_letters(k)
    if unified_key in newDict:
        newDict[unified_key] += ngramsDict[k]
    else:
        newDict[unified_key] = ngramsDict[k]


# Sortowanie wyników malejąco według liczby wystąpień
srtDictList = sorted(newDict.items(), key=lambda x: x[1], reverse=True)
sortedDictionary = dict(srtDictList)

with open('czech_bigrams_fixed.txt', 'w', encoding='utf-8') as plik:
    for k in sortedDictionary:
        plik.write(f"{k} {sortedDictionary[k]}\n")