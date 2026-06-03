def createFile(input, fileName, alfabet):
    """Funkcja do generowania Bigramów"""
    print("Rozpoczęto tworzenie pliku z bigramami...")
    alfabet = alfabet.upper()
    dct = {a+b: 0 for a in alfabet for b in alfabet}
    prev_char = None

    with open(input, encoding='utf-8') as f:
        for line in f:
            prev_char = None
            line = ''.join([x for x in line.upper() if x.isalpha() and x in alfabet])
            for c in line:
                if prev_char is not None:
                    bigram = prev_char + c
                    if bigram in dct:
                        dct[bigram] += 1
                prev_char = c

    srt = [(count, k) for k, count in dct.items() if count > 0]
    srt.sort(reverse=True)
    with open(fileName, 'w', encoding='utf-8') as f:
        for elem in srt:
            f.write(elem[1] + ' ' + str(elem[0]) + '\n')

    print("Zakończono tworzenie pliku.")

# Przykład użycia:
if __name__ == "__main__":
    input = 'cs.txt'
    fileName = 'czech_bigrams.txt'
    alfabet = 'abcdefghijklmnopqrstuvwxyzáčďéěíňóřšťúůýž'
    createFile(input, fileName, alfabet)