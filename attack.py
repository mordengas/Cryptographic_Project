import random
from Ngrams import Ngram_score
from Utils import Utils

"""
Szyfr Monome-Dinome - Atak wspinaczkowy (Hill Climbing)
Student: Dominik Machnik
Szyfr: Monome-Dinome - szyfr podstawieniowy używający tabeli 3x8 dla jezyka angielskiego 
        oraz  4x10 dla czeskiego.
Metoda rozwiązania: Hill Climbing z analizą n-gramów, oraz analizą czestotliwości jak często dana liczba
        w kryptotekście występuje po innej. Analiza ta pozwala na ustalenie liczb które odpowiadaja za wiersze
        w tabeli szyfrującej. 
Klucze: 24-znakowy klucz literowy + 2-cyfrowy klucz numeryczny dla angielskiego
        40-znakowy klucz literowy + 3-cyfrowy klucz numeryczny dla czeskiego
Najlepsze wyniki dla języka angielskiego występowały przy tekście o długości conajmniej 500 znaków,
natomiast dla czeskiego przy długości 1000 znaków. Jednakże, teksty języka czeskiego są znacznie trudniejsze do odszyfrowania,
ponieważ zawierają więcej znaków diakrytycznych.  
"""

def mutuj_klucz(klucz):
    klucz = list(klucz)
    mutacja = random.random()

    if mutacja < 0.3:
        # Prosty swap dwóch losowych liter
        i, j = random.sample(range(len(klucz)), 2)
        klucz[i], klucz[j] = klucz[j], klucz[i]

    elif mutacja < 0.5:
        # Zamiana dwóch całych kolumn (zachowuje strukturę tablicy)
        c1, c2 = random.sample(range(8), 2)
        for r in range(3):
            i = r * 8 + c1
            j = r * 8 + c2
            klucz[i], klucz[j] = klucz[j], klucz[i]

    elif mutacja < 0.65:
        # Zamiana dwóch wierszy
        r1, r2 = random.sample(range(3), 2)
        for k in range(8):
            i = r1 * 8 + k
            j = r2 * 8 + k
            klucz[i], klucz[j] = klucz[j], klucz[i]

    elif mutacja < 0.8:
        # Odwróć losowy wiersz lub kolumnę (czasem dobry ruch)
        if random.random() < 0.5:
            r = random.randint(0, 2)
            start = r * 8
            klucz[start:start+8] = klucz[start:start+8][::-1]
        else:
            c = random.randint(0, 7)
            col = [klucz[r*8 + c] for r in range(3)]
            col.reverse()
            for r in range(3):
                klucz[r*8 + c] = col[r]

    elif mutacja < 0.9:
        # Przesuń losową literę o jedną pozycję w lewo/prawo
        i = random.randint(0, len(klucz) - 1)
        if i < len(klucz) - 1:
            klucz[i], klucz[i+1] = klucz[i+1], klucz[i]

    else:
        # Duży skok: losowe przesunięcie segmentu
        start = random.randint(0, 16)
        end = min(start + random.randint(3, 6), 24)
        segment = klucz[start:end]
        del klucz[start:end]
        insert_at = random.randint(0, len(klucz))
        for i, lit in enumerate(segment):
            klucz.insert(insert_at + i, lit)

    return ''.join(klucz)


def mutuj_2_ostatnie_cyfry(cyfry):
    cyfry = list(cyfry)
    cyfry[8], cyfry[9] = cyfry[9], cyfry[8]
    return ''.join(cyfry)


def hill_climb(szyfrogram, start_klucz, start_cyfry, ngram_scorer, max_iter, max_brak_postepu=5000):
    najlepszy_klucz = start_klucz
    najlepszy_cyfry = start_cyfry
    odszyfrowany = Utils.deszyfruj_monome_dinome(szyfrogram, najlepszy_klucz, najlepszy_cyfry)
    najlepszy_wynik = ngram_scorer.score(odszyfrowany)

    brak_postepu = 0

    for iteracja in range(max_iter):
        if random.random() < 0.15:
            # Mutuj tylko 2 ostatnie cyfry
            nowy_klucz = najlepszy_klucz
            nowy_cyfry = mutuj_2_ostatnie_cyfry(najlepszy_cyfry)
        else:
            # Mutuj klucz literowy
            nowy_klucz = mutuj_klucz(najlepszy_klucz)
            nowy_cyfry = najlepszy_cyfry

        odszyfrowany = Utils.deszyfruj_monome_dinome(szyfrogram, nowy_klucz, nowy_cyfry)
        wynik = ngram_scorer.score(odszyfrowany)

        if wynik > najlepszy_wynik:
            najlepszy_klucz = nowy_klucz
            najlepszy_cyfry = nowy_cyfry
            najlepszy_wynik = wynik
            brak_postepu = 0  # resetujemy licznik
            print(f"Iteracja {iteracja}: Nowy najlepszy wynik = {wynik:.2f}")
            print(f"  Klucz literowy: {najlepszy_klucz}")
            print(f"  Klucz cyfrowy: {najlepszy_cyfry}")
            print(f"  Kluczowe cyfry (ostatnie 2): {najlepszy_cyfry[8:]}")
            print(f"  Odszyfrowany fragment: {odszyfrowany[:50]}...\n")
        else:
            brak_postepu += 1

        if brak_postepu >= max_brak_postepu:
            print(f"Brak postępu przez {max_brak_postepu} iteracji. Przerywam.")
            break

    return najlepszy_klucz, najlepszy_cyfry

# --- Przykład użycia ---
if __name__ == "__main__":
    #plik_ngramy = "english_bigrams_fixed.txt"
    #plik_ngramy = "english_trigrams_fixed.txt"
    plik_ngramy = "english_quadgrams_fixed.txt"

    # Wczytanie modelu n-gramów
    ngram_scorer = Ngram_score(plik_ngramy)

    # Generujemy losowy klucz literowy i cyfrowy
    klucz = Utils.generuj_losowy_klucz()
    cyfry = Utils.generuj_losowy_klucz_cyfrowy()

    # Wyświetlamy tablicę i klucz cyfrowy
    Utils.wyswietl_tablice(klucz)
    print("Klucz literowy:", klucz)
    print("Klucz cyfrowy:", cyfry)

    # Przykładowy tekst do szyfrowania
    with open("plaintext2_en.txt", "r", encoding="utf-8") as f:
        tekst = f.read()
    przygotowany_tekst = Utils.normalizuj_tekst(tekst)
    print("\nPrzygotowany tekst do szyfrowania:", przygotowany_tekst[:150])

    # Szyfrujemy przygotowany tekst
    zaszyfrowany = Utils.szyfruj_monome_dinome(przygotowany_tekst, klucz, cyfry)
    #print("\nZaszyfrowany tekst:", zaszyfrowany[:150])

    start_klucz = Utils.generuj_losowy_klucz()
    most_common = Utils.find_two_most_frequent_followers(zaszyfrowany)
    all_digits = set("0123456789")
    others = sorted(all_digits - set(most_common))
    start_cyfry = ''.join(others) + most_common
     
    # Atak hill climb - próbujemy odgadnąć klucz literowy
    print("\nRozpoczynam atak hill climb...")
    najlepszy_klucz, najlepszy_cyfry = hill_climb(zaszyfrowany, start_klucz, start_cyfry, ngram_scorer, max_iter=200000)

    odszyfrowany = Utils.deszyfruj_monome_dinome(zaszyfrowany, najlepszy_klucz, najlepszy_cyfry)
    print("\nNajlepszy znaleziony klucz literowy:", najlepszy_klucz)
    print("Najlepszy znaleziony klucz cyfrowy:", najlepszy_cyfry)
    print("\nZaszyfrowany tekst:", zaszyfrowany[:150])
    print("Odszyfrowany tekst:", odszyfrowany[:150])