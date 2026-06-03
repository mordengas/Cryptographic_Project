import random
from Ngrams import Ngram_score
from UtilsCz import UtilsCz

def mutuj_klucz(klucz):
    klucz = list(klucz)
    mutacja = random.random()

    if mutacja < 0.3:
        # Prosty swap dwóch losowych liter
        i, j = random.sample(range(len(klucz)), 2)
        klucz[i], klucz[j] = klucz[j], klucz[i]

    elif mutacja < 0.5:
        # Zamiana dwóch kolumn (4x10)
        c1, c2 = random.sample(range(10), 2)
        for r in range(4):
            i = r * 10 + c1
            j = r * 10 + c2
            klucz[i], klucz[j] = klucz[j], klucz[i]

    elif mutacja < 0.65:
        # Zamiana dwóch wierszy
        r1, r2 = random.sample(range(4), 2)
        for k in range(10):
            i = r1 * 10 + k
            j = r2 * 10 + k
            klucz[i], klucz[j] = klucz[j], klucz[i]

    elif mutacja < 0.8:
        # Odwróć wiersz lub kolumnę
        if random.random() < 0.5:
            r = random.randint(0, 3)
            start = r * 10
            klucz[start:start+10] = klucz[start:start+10][::-1]
        else:
            c = random.randint(0, 9)
            col = [klucz[r*10 + c] for r in range(4)]
            col.reverse()
            for r in range(4):
                klucz[r*10 + c] = col[r]

    elif mutacja < 0.9:
        # Przesuń literę w lewo/prawo
        i = random.randint(0, len(klucz) - 2)
        klucz[i], klucz[i+1] = klucz[i+1], klucz[i]

    else:
        # Duży skok: przeniesienie segmentu
        start = random.randint(0, 30)
        end = min(start + random.randint(3, 6), len(klucz))
        segment = klucz[start:end]
        del klucz[start:end]
        insert_at = random.randint(0, len(klucz))
        for i, lit in enumerate(segment):
            klucz.insert(insert_at + i, lit)

    return ''.join(klucz)

def mutuj_3_ostatnie_cyfry(cyfry):
    cyfry = list(cyfry)
    ostatnie_trzy = cyfry[-3:]
    random.shuffle(ostatnie_trzy)
    cyfry[-3:] = ostatnie_trzy
    return ''.join(cyfry)

def hill_climb(szyfrogram, start_klucz, start_cyfry, ngram_scorer, max_iter, max_brak_postepu=10000):
    najlepszy_klucz = start_klucz
    najlepszy_cyfry = start_cyfry
    odszyfrowany = UtilsCz.deszyfruj_monome_dinome(szyfrogram, najlepszy_klucz, najlepszy_cyfry)
    najlepszy_wynik = ngram_scorer.score(odszyfrowany)

    brak_postepu = 0

    for iteracja in range(max_iter):
        if random.random() < 0.20:
            # Mutuj tylko 3 ostatnie cyfry
            nowy_klucz = najlepszy_klucz
            nowy_cyfry = mutuj_3_ostatnie_cyfry(najlepszy_cyfry)
        else:
            # Mutuj klucz literowy
            nowy_klucz = mutuj_klucz(najlepszy_klucz)
            nowy_cyfry = najlepszy_cyfry

        odszyfrowany = UtilsCz.deszyfruj_monome_dinome(szyfrogram, nowy_klucz, nowy_cyfry)
        wynik = ngram_scorer.score(odszyfrowany)

        if wynik > najlepszy_wynik:
            najlepszy_klucz = nowy_klucz
            najlepszy_cyfry = nowy_cyfry
            najlepszy_wynik = wynik
            brak_postepu = 0  # resetujemy licznik
            print(f"Iteracja {iteracja}: Nowy najlepszy wynik = {wynik:.2f}")
            print(f"  Klucz literowy: {najlepszy_klucz}")
            print(f"  Klucz cyfrowy: {najlepszy_cyfry}")
            print(f"  Kluczowe cyfry (ostatnie 3): {najlepszy_cyfry[10:]}")
            print(f"  Odszyfrowany fragment: {odszyfrowany[:50]}...\n")
        else:
            brak_postepu += 1

        if brak_postepu >= max_brak_postepu:
            print(f"Brak postępu przez {max_brak_postepu} iteracji. Przerywam.")
            break

    return najlepszy_klucz, najlepszy_cyfry

if __name__ == "__main__":
    plik_ngramy = "czech_quadgrams_fixed.txt"

    # Wczytanie modelu n-gramów
    ngram_scorer = Ngram_score(plik_ngramy)

    # Generujemy losowy klucz literowy i cyfrowy
    klucz = UtilsCz.generuj_losowy_klucz()
    cyfry = UtilsCz.generuj_losowy_klucz_cyfrowy()

    UtilsCz.wyswietl_tablice(klucz)
    print("Klucz literowy:", klucz)
    print("Klucz cyfrowy:", cyfry)

    # Wczytujemy tekst w języku czeskim
    with open("plaintext_cz.txt", "r", encoding="utf-8") as f:
        tekst = f.read()
    przygotowany_tekst = UtilsCz.normalizuj_tekst(tekst)
    print("\nPrzygotowany tekst do szyfrowania:", przygotowany_tekst[:150])

    zaszyfrowany = UtilsCz.szyfruj_monome_dinome(przygotowany_tekst, klucz, cyfry)

    start_klucz = UtilsCz.generuj_losowy_klucz()
    most_common = UtilsCz.find_three_most_frequent_followers(zaszyfrowany)
    
    all_digits = set("0123456789ABC")
    others = sorted(all_digits - set(most_common))
    start_cyfry = ''.join(others) + most_common

    print("\nRozpoczynam atak hill climb...")
    najlepszy_klucz, najlepszy_cyfry = hill_climb(
        zaszyfrowany, start_klucz, start_cyfry, ngram_scorer, max_iter=200000
    )

    odszyfrowany = UtilsCz.deszyfruj_monome_dinome(zaszyfrowany, najlepszy_klucz, najlepszy_cyfry)

    print("\nNajlepszy znaleziony klucz literowy:", najlepszy_klucz)
    print("Najlepszy znaleziony klucz cyfrowy:", najlepszy_cyfry)
    print("\nZaszyfrowany tekst:", zaszyfrowany[:150])
    print("Odszyfrowany tekst:", odszyfrowany[:150])

    UtilsCz.wyswietl_tablice(najlepszy_klucz)
