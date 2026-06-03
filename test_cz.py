import time
import random
from UtilsCz import UtilsCz
from Ngrams import Ngram_score

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

def sprawdz_poprawnosc(odszyfrowany, oryginalny, tolerancja=0.9):
    """Sprawdza czy odszyfrowany tekst jest wystarczająco podobny do oryginalnego"""
    if len(odszyfrowany) == 0:
        return False, 0.0
    
    # Porównujemy pierwsze min(len) znaków
    min_len = min(len(odszyfrowany), len(oryginalny))
    poprawne = sum(1 for i in range(min_len) if odszyfrowany[i] == oryginalny[i])
    
    procent_podobienstwa = (poprawne / min_len) * 100
    czy_sukces = procent_podobienstwa >= (tolerancja * 100)
    
    return czy_sukces, procent_podobienstwa

# Wersja hill_climb bez printów dla testów
def hill_climb_quiet(szyfrogram, start_klucz, start_cyfry, ngram_scorer, max_iter, max_brak_postepu=10000):
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
            brak_postepu = 0
        else:
            brak_postepu += 1

        if brak_postepu >= max_brak_postepu:
            break

    return najlepszy_klucz, najlepszy_cyfry

def test_efektywnosci():

    # Parametry testów
    dlugosci_tekstu = [150, 300, 500, 750, 1000]  # różne długości kryptotekstu
    liczba_prob = 20  # liczba powtórzeń dla każdej długości
    max_iter = 100000  # maksimalna liczba iteracji
    
    print("=== TEST EFEKTYWNOŚCI ATAKU HILL CLIMB - SYSTEM CZESKI ===\n")
    
    # Wczytanie modelu n-gramów
    ngram_scorer = Ngram_score("czech_quadgrams_fixed.txt")

    # Wczytanie przykładowego tekstu czeskiego
    with open("plaintext_cz.txt", "r", encoding="utf-8") as f:
        bazowy_tekst = f.read()

    bazowy_tekst = UtilsCz.normalizuj_tekst(bazowy_tekst)
    
    # Wyniki testów
    wyniki = {}
    
    for dlugosc in dlugosci_tekstu:
        print(f"\n--- TESTOWANIE DŁUGOŚCI: {dlugosc} znaków ---")
        
        sukcesy = 0
        czasy = []
        podobienstwa = []
        
        # Przygotuj tekst odpowiedniej długości
        tekst_test = bazowy_tekst[:dlugosc]
        
        for proba in range(liczba_prob):
            print(f"  Próba {proba + 1}/{liczba_prob}...", end=" ")
            
            # Generuj losowy klucz do szyfrowania
            klucz_prawdziwy = UtilsCz.generuj_losowy_klucz()
            cyfry_prawdziwe = UtilsCz.generuj_losowy_klucz_cyfrowy()
            
            # Zaszyfruj tekst
            zaszyfrowany = UtilsCz.szyfruj_monome_dinome(tekst_test, klucz_prawdziwy, cyfry_prawdziwe)
            
            # Przygotuj punkt startowy dla ataku
            start_klucz = UtilsCz.generuj_losowy_klucz()
            most_common = UtilsCz.find_three_most_frequent_followers(zaszyfrowany)
            all_digits = set("0123456789ABC")
            others = sorted(all_digits - set(most_common))
            start_cyfry = ''.join(others) + most_common
            
            # Zmierz czas ataku
            start_time = time.time()
            
            # Wykonaj atak (z wyłączonymi printami)
            najlepszy_klucz, najlepszy_cyfry = hill_climb_quiet(
                zaszyfrowany, start_klucz, start_cyfry, ngram_scorer, max_iter
            )
            
            czas_ataku = time.time() - start_time
            czasy.append(czas_ataku)
            
            # Sprawdź poprawność
            odszyfrowany = UtilsCz.deszyfruj_monome_dinome(zaszyfrowany, najlepszy_klucz, najlepszy_cyfry)
            
            czy_sukces, procent_podobienstwa = sprawdz_poprawnosc(odszyfrowany, tekst_test, tolerancja=0.9)
            podobienstwa.append(procent_podobienstwa)
            
            if czy_sukces:
                sukcesy += 1
                print(f"SUKCES ({procent_podobienstwa:.1f}%)")
            else:
                print(f"PORAŻKA ({procent_podobienstwa:.1f}%)")
        
        # Oblicz statystyki
        procent_sukcesu = (sukcesy / liczba_prob) * 100
        sredni_czas = sum(czasy) / len(czasy)
        srednie_podobienstwo = sum(podobienstwa) / len(podobienstwa)
        
        wyniki[dlugosc] = {
            'sukcesy': procent_sukcesu,
            'sredni_czas': sredni_czas,
            'min_czas': min(czasy),
            'max_czas': max(czasy),
            'srednie_podobienstwo': srednie_podobienstwo
        }
        
        print(f"  Wyniki: {sukcesy}/{liczba_prob} sukcesów ({procent_sukcesu:.1f}%)")
        print(f"  Średni czas: {sredni_czas:.1f}s (min: {min(czasy):.1f}s, max: {max(czasy):.1f}s)")
        print(f"  Średnie podobieństwo: {srednie_podobienstwo:.1f}%")
    
    # Podsumowanie wyników
    print("\n" + "="*60)
    print("PODSUMOWANIE WYNIKÓW")
    print("="*60)
    print(f"{'Długość':<10} {'Sukces %':<10} {'Śr. czas':<12} {'Min czas':<10} {'Max czas':<10}")
    print("-" * 60)
    
    for dlugosc, stats in wyniki.items():
        print(f"{dlugosc:<10} {stats['sukcesy']:<10.1f} {stats['sredni_czas']:<12.1f} "
              f"{stats['min_czas']:<10.1f} {stats['max_czas']:<10.1f}")
    
    # Analiza wyników
    print("\n" + "="*60)
    print("ANALIZA")
    print("="*60)
    
    skuteczne_dlugosci = [d for d, s in wyniki.items() if s['sukcesy'] >= 90]
    if skuteczne_dlugosci:
        min_dlugosc = min(skuteczne_dlugosci)
        print(f"Minimalna skuteczna długość (≥90% sukcesu): {min_dlugosc} znaków")
    else:
        print("Żadna z testowanych długości nie osiągnęła 90% skuteczności")
    
    najszybsze = min(wyniki.items(), key=lambda x: x[1]['sredni_czas'])
    print(f"Najszybszy średni czas: {najszybsze[1]['sredni_czas']:.1f}s dla {najszybsze[0]} znaków")
    
    return wyniki

if __name__ == "__main__":
    test_efektywnosci()

    '''--- TESTOWANIE DŁUGOŚCI: 150 znaków ---
  Próba 1/20... PORAŻKA (0.0%)
  Próba 2/20... PORAŻKA (6.7%)
  Próba 3/20... PORAŻKA (3.3%)
  Próba 4/20... PORAŻKA (0.0%)
  Próba 5/20... PORAŻKA (30.0%)
  Próba 6/20... PORAŻKA (5.0%)
  Próba 7/20... PORAŻKA (6.4%)
  Próba 8/20... PORAŻKA (0.7%)
  Próba 9/20... PORAŻKA (3.4%)
  Próba 10/20... PORAŻKA (7.6%)
  Próba 11/20... PORAŻKA (1.5%)
  Próba 12/20... PORAŻKA (1.3%)
  Próba 13/20... PORAŻKA (3.5%)
  Próba 14/20... PORAŻKA (7.1%)
  Próba 15/20... PORAŻKA (2.1%)
  Próba 16/20... PORAŻKA (2.8%)
  Próba 17/20... PORAŻKA (7.3%)
  Próba 18/20... PORAŻKA (1.4%)
  Próba 19/20... PORAŻKA (4.3%)
  Próba 20/20... PORAŻKA (3.3%)
  Wyniki: 0/20 sukcesów (0.0%)
  Średni czas: 4.5s (min: 2.7s, max: 6.6s)
  Średnie podobieństwo: 4.9%

--- TESTOWANIE DŁUGOŚCI: 300 znaków ---
  Próba 1/20... PORAŻKA (0.0%)
  Próba 2/20... PORAŻKA (6.1%)
  Próba 3/20... PORAŻKA (5.8%)
  Próba 4/20... PORAŻKA (6.9%)
  Próba 5/20... PORAŻKA (6.7%)
  Próba 6/20... PORAŻKA (6.4%)
  Próba 7/20... PORAŻKA (13.3%)
  Próba 8/20... PORAŻKA (0.7%)
  Próba 9/20... PORAŻKA (8.5%)
  Próba 10/20... PORAŻKA (0.0%)
  Próba 11/20... PORAŻKA (3.2%)
  Próba 12/20... PORAŻKA (0.0%)
  Próba 13/20... PORAŻKA (1.7%)
  Próba 14/20... PORAŻKA (0.3%)
  Próba 15/20... PORAŻKA (24.3%)
  Próba 16/20... PORAŻKA (6.1%)
  Próba 17/20... PORAŻKA (3.9%)
  Próba 18/20... PORAŻKA (23.7%)
  Próba 19/20... PORAŻKA (0.0%)
  Próba 20/20... PORAŻKA (18.7%)
  Wyniki: 0/20 sukcesów (0.0%)
  Średni czas: 10.9s (min: 4.7s, max: 20.5s)
  Średnie podobieństwo: 6.8%

--- TESTOWANIE DŁUGOŚCI: 500 znaków ---
  Próba 1/20... PORAŻKA (15.4%)
  Próba 2/20... PORAŻKA (26.2%)
  Próba 3/20... PORAŻKA (6.6%)
  Próba 4/20... PORAŻKA (5.5%)
  Próba 5/20... PORAŻKA (3.2%)
  Próba 6/20... SUKCES (96.4%)
  Próba 7/20... PORAŻKA (0.0%)
  Próba 8/20... PORAŻKA (19.8%)
  Próba 9/20... PORAŻKA (4.3%)
  Próba 10/20... PORAŻKA (9.2%)
  Próba 11/20... PORAŻKA (5.3%)
  Próba 12/20... PORAŻKA (4.1%)
  Próba 13/20... PORAŻKA (4.3%)
  Próba 14/20... PORAŻKA (4.2%)
  Próba 15/20... PORAŻKA (24.4%)
  Próba 16/20... PORAŻKA (26.6%)
  Próba 17/20... PORAŻKA (5.6%)
  Próba 18/20... PORAŻKA (4.5%)
  Próba 19/20... PORAŻKA (6.3%)
  Próba 20/20... PORAŻKA (3.8%)
  Wyniki: 1/20 sukcesów (5.0%)
  Średni czas: 15.3s (min: 10.2s, max: 26.2s)
  Średnie podobieństwo: 13.8%

--- TESTOWANIE DŁUGOŚCI: 750 znaków ---
  Próba 1/20... PORAŻKA (5.3%)
  Próba 2/20... PORAŻKA (4.7%)
  Próba 3/20... PORAŻKA (4.8%)
  Próba 4/20... SUKCES (96.4%)
  Próba 5/20... PORAŻKA (8.9%)
  Próba 6/20... PORAŻKA (3.9%)
  Próba 7/20... PORAŻKA (29.9%)
  Próba 8/20... PORAŻKA (5.2%)
  Próba 9/20... PORAŻKA (4.7%)
  Próba 10/20... PORAŻKA (3.0%)
  Próba 11/20... PORAŻKA (4.7%)
  Próba 12/20... PORAŻKA (4.3%)
  Próba 13/20... PORAŻKA (3.5%)
  Próba 14/20... PORAŻKA (4.1%)
  Próba 15/20... PORAŻKA (38.7%)
  Próba 16/20... PORAŻKA (4.1%)
  Próba 17/20... PORAŻKA (4.1%)
  Próba 18/20... PORAŻKA (5.2%)
  Próba 19/20... PORAŻKA (5.1%)
  Próba 20/20... PORAŻKA (19.5%)
  Wyniki: 1/20 sukcesów (5.0%)
  Średni czas: 24.7s (min: 15.9s, max: 38.1s)
  Średnie podobieństwo: 13.0%

--- TESTOWANIE DŁUGOŚCI: 1000 znaków ---
  Próba 1/20... PORAŻKA (1.9%)
  Próba 2/20... PORAŻKA (5.8%)
  Próba 3/20... PORAŻKA (0.0%)
  Próba 4/20... PORAŻKA (0.2%)
  Próba 5/20... PORAŻKA (4.6%)
  Próba 6/20... PORAŻKA (4.1%)
  Próba 7/20... PORAŻKA (8.8%)
  Próba 8/20... PORAŻKA (5.5%)
  Próba 9/20... SUKCES (96.6%)
  Próba 10/20... PORAŻKA (0.0%)
  Próba 11/20... SUKCES (97.3%)
  Próba 12/20... PORAŻKA (5.9%)
  Próba 13/20... PORAŻKA (5.6%)
  Próba 14/20... PORAŻKA (5.5%)
  Próba 15/20... PORAŻKA (29.1%)
  Próba 16/20... PORAŻKA (4.9%)
  Próba 17/20... PORAŻKA (0.0%)
  Próba 18/20... SUKCES (96.6%)
  Próba 19/20... PORAŻKA (4.5%)
  Próba 20/20... PORAŻKA (4.6%)
  Wyniki: 3/20 sukcesów (15.0%)
  Średni czas: 38.8s (min: 23.3s, max: 60.5s)
  Średnie podobieństwo: 19.1%

============================================================
PODSUMOWANIE WYNIKÓW
============================================================
Długość    Sukces %   Śr. czas     Min czas   Max czas
------------------------------------------------------------
150        0.0        4.5          2.7        6.6
300        0.0        10.9         4.7        20.5
500        5.0        15.3         10.2       26.2
750        5.0        24.7         15.9       38.1
1000       15.0       38.8         23.3       60.5'''