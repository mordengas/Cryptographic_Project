import time
import random
from Utils import Utils
from Ngrams import Ngram_score

#Zamienia dwie losowe litery w kluczu
def mutuj_klucz(klucz):
    klucz_lista = list(klucz)
    i, j = random.sample(range(len(klucz)), 2)
    klucz_lista[i], klucz_lista[j] = klucz_lista[j], klucz_lista[i]
    return ''.join(klucz_lista)

# Zamienia dwie ostatnie cyfry miejscami
def mutuj_2_ostatnie_cyfry(cyfry):
    cyfry_lista = list(cyfry)
    cyfry_lista[8], cyfry_lista[9] = cyfry_lista[9], cyfry_lista[8]
    return ''.join(cyfry_lista)

# Sprawdza czy odszyfrowany tekst jest wystarczająco podobny do oryginalnego
def sprawdz_poprawnosc(odszyfrowany, oryginalny, tolerancja=0.9):
    if len(odszyfrowany) == 0:
        return False, 0.0
    
    # Porównujemy pierwsze min(len) znaków
    min_len = min(len(odszyfrowany), len(oryginalny))
    poprawne = sum(1 for i in range(min_len) if odszyfrowany[i] == oryginalny[i])
    
    procent_podobienstwa = (poprawne / min_len) * 100
    czy_sukces = procent_podobienstwa >= (tolerancja * 100)
    
    return czy_sukces, procent_podobienstwa

def test_efektywnosci():

    # Parametry testów
    dlugosci_tekstu = [150, 300, 500, 750, 1000]  # różne długości kryptotekstu
    liczba_prob = 20  # liczba powtórzeń dla każdej długości
    max_iter = 100000  # zmniejszone dla szybszych testów
    
    print("=== TEST EFEKTYWNOŚCI ATAKU HILL CLIMB ===\n")
    
    # Wczytanie modelu n-gramów
    ngram_scorer = Ngram_score("english_quadgrams_fixed.txt")

    # Wczytanie przykładowego tekstu
    with open("plaintext2_en.txt", "r", encoding="utf-8") as f:
            bazowy_tekst = f.read()

    bazowy_tekst = Utils.normalizuj_tekst(bazowy_tekst)
    
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
            klucz_prawdziwy = Utils.generuj_losowy_klucz()
            cyfry_prawdziwe = Utils.generuj_losowy_klucz_cyfrowy()
            
            # Zaszyfruj tekst
            zaszyfrowany = Utils.szyfruj_monome_dinome(tekst_test, klucz_prawdziwy, cyfry_prawdziwe)
            
            # Przygotuj punkt startowy dla ataku
            start_klucz = Utils.generuj_losowy_klucz()
            most_common = Utils.find_two_most_frequent_followers(zaszyfrowany)
            all_digits = set("0123456789")
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
            odszyfrowany = Utils.deszyfruj_monome_dinome(zaszyfrowany, najlepszy_klucz, najlepszy_cyfry)
            
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

def hill_climb_quiet(szyfrogram, start_klucz, start_cyfry, ngram_scorer, max_iter, max_brak_postepu=20000):
    """Wersja hill_climb bez printów dla testów"""
    najlepszy_klucz = start_klucz
    najlepszy_cyfry = start_cyfry
    odszyfrowany = Utils.deszyfruj_monome_dinome(szyfrogram, najlepszy_klucz, najlepszy_cyfry)
    najlepszy_wynik = ngram_scorer.score(odszyfrowany)

    brak_postepu = 0

    for iteracja in range(max_iter):
        if random.random() < 0.15:
            nowy_klucz = najlepszy_klucz
            nowy_cyfry = mutuj_2_ostatnie_cyfry(najlepszy_cyfry)
        else:
            nowy_klucz = mutuj_klucz(najlepszy_klucz)
            nowy_cyfry = najlepszy_cyfry

        odszyfrowany = Utils.deszyfruj_monome_dinome(szyfrogram, nowy_klucz, nowy_cyfry)
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

if __name__ == "__main__":
    test_efektywnosci()

'''--- TESTOWANIE DŁUGOŚCI: 150 znaków ---
  Próba 1/20... PORAŻKA (23.3%)
  Próba 2/20... PORAŻKA (9.2%)
  Próba 3/20... PORAŻKA (42.0%)
  Próba 4/20... SUKCES (100.0%)
  Próba 5/20... SUKCES (100.0%)
  Próba 6/20... SUKCES (100.0%)
  Próba 7/20... PORAŻKA (1.3%)
  Próba 8/20... PORAŻKA (4.7%)
  Próba 9/20... PORAŻKA (11.3%)
  Próba 10/20... PORAŻKA (4.7%)
  Próba 11/20... SUKCES (100.0%)
  Próba 12/20... SUKCES (100.0%)
  Próba 13/20... PORAŻKA (6.9%)
  Próba 14/20... PORAŻKA (5.6%)
  Próba 15/20... PORAŻKA (9.0%)
  Próba 16/20... SUKCES (100.0%)
  Próba 17/20... PORAŻKA (0.0%)
  Próba 18/20... PORAŻKA (3.3%)
  Próba 19/20... PORAŻKA (34.0%)
  Próba 20/20... SUKCES (100.0%)
  Wyniki: 7/20 sukcesów (35.0%)
  Średni czas: 2.5s (min: 2.1s, max: 2.8s)
  Średnie podobieństwo: 42.8%

--- TESTOWANIE DŁUGOŚCI: 300 znaków ---
  Próba 1/20... SUKCES (100.0%)
  Próba 2/20... SUKCES (100.0%)
  Próba 3/20... PORAŻKA (7.2%)
  Próba 4/20... PORAŻKA (2.0%)
  Próba 5/20... SUKCES (100.0%)
  Próba 6/20... SUKCES (100.0%)
  Próba 7/20... SUKCES (100.0%)
  Próba 8/20... PORAŻKA (5.6%)
  Próba 9/20... SUKCES (100.0%)
  Próba 10/20... SUKCES (100.0%)
  Próba 11/20... SUKCES (100.0%)
  Próba 12/20... PORAŻKA (6.7%)
  Próba 13/20... PORAŻKA (6.1%)
  Próba 14/20... SUKCES (100.0%)
  Próba 15/20... SUKCES (100.0%)
  Próba 16/20... SUKCES (100.0%)
  Próba 17/20... SUKCES (100.0%)
  Próba 18/20... SUKCES (100.0%)
  Próba 19/20... PORAŻKA (8.4%)
  Próba 20/20... SUKCES (100.0%)
  Wyniki: 14/20 sukcesów (70.0%)
  Średni czas: 5.3s (min: 5.0s, max: 6.1s)
  Średnie podobieństwo: 71.8%

--- TESTOWANIE DŁUGOŚCI: 500 znaków ---
  Próba 1/20... SUKCES (100.0%)
  Próba 2/20... SUKCES (100.0%)
  Próba 3/20... SUKCES (100.0%)
  Próba 4/20... SUKCES (100.0%)
  Próba 5/20... PORAŻKA (8.5%)
  Próba 6/20... SUKCES (100.0%)
  Próba 7/20... PORAŻKA (15.0%)
  Próba 8/20... SUKCES (100.0%)
  Próba 9/20... SUKCES (100.0%)
  Próba 10/20... PORAŻKA (24.2%)
  Próba 11/20... SUKCES (100.0%)
  Próba 12/20... SUKCES (100.0%)
  Próba 13/20... PORAŻKA (19.8%)
  Próba 14/20... SUKCES (100.0%)
  Próba 15/20... SUKCES (100.0%)
  Próba 16/20... PORAŻKA (6.6%)
  Próba 17/20... SUKCES (100.0%)
  Próba 18/20... SUKCES (100.0%)
  Próba 19/20... SUKCES (100.0%)
  Próba 20/20... SUKCES (100.0%)
  Wyniki: 15/20 sukcesów (75.0%)
  Średni czas: 10.0s (min: 9.1s, max: 12.2s)
  Średnie podobieństwo: 78.7%

--- TESTOWANIE DŁUGOŚCI: 750 znaków ---
  Próba 1/20... SUKCES (100.0%)
  Próba 2/20... PORAŻKA (6.9%)
  Próba 3/20... SUKCES (100.0%)
  Próba 4/20... SUKCES (100.0%)
  Próba 5/20... PORAŻKA (16.0%)
  Próba 6/20... SUKCES (100.0%)
  Próba 7/20... PORAŻKA (5.9%)
  Próba 8/20... SUKCES (100.0%)
  Próba 9/20... PORAŻKA (7.0%)
  Próba 10/20... SUKCES (100.0%)
  Próba 11/20... SUKCES (100.0%)
  Próba 12/20... SUKCES (100.0%)
  Próba 13/20... PORAŻKA (19.9%)
  Próba 14/20... SUKCES (100.0%)
  Próba 15/20... SUKCES (100.0%)
  Próba 16/20... SUKCES (100.0%)
  Próba 17/20... SUKCES (100.0%)
  Próba 18/20... SUKCES (100.0%)
  Próba 19/20... SUKCES (100.0%)
  Próba 20/20... SUKCES (100.0%)
  Wyniki: 15/20 sukcesów (75.0%)
  Średni czas: 14.9s (min: 13.2s, max: 16.2s)
  Średnie podobieństwo: 77.8%

--- TESTOWANIE DŁUGOŚCI: 1000 znaków ---
  Próba 1/20... SUKCES (100.0%)
  Próba 2/20... SUKCES (100.0%)
  Próba 3/20... SUKCES (100.0%)
  Próba 4/20... SUKCES (100.0%)
  Próba 5/20... PORAŻKA (9.3%)
  Próba 6/20... SUKCES (100.0%)
  Próba 7/20... SUKCES (100.0%)
  Próba 8/20... SUKCES (100.0%)
  Próba 9/20... SUKCES (100.0%)
  Próba 10/20... PORAŻKA (6.1%)
  Próba 11/20... PORAŻKA (6.7%)
  Próba 12/20... SUKCES (100.0%)
  Próba 13/20... SUKCES (100.0%)
  Próba 14/20... SUKCES (100.0%)
  Próba 15/20... SUKCES (100.0%)
  Próba 16/20... PORAŻKA (33.7%)
  Próba 17/20... SUKCES (100.0%)
  Próba 18/20... PORAŻKA (0.0%)
  Próba 19/20... PORAŻKA (7.9%)
  Próba 20/20... SUKCES (100.0%)
  Wyniki: 14/20 sukcesów (70.0%)
  Średni czas: 24.8s (min: 21.2s, max: 29.4s)
  Średnie podobieństwo: 73.2%

============================================================
PODSUMOWANIE WYNIKÓW
============================================================
Długość    Sukces %   Śr. czas     Min czas   Max czas
------------------------------------------------------------
150        35.0       2.5          2.1        2.8
300        70.0       5.3          5.0        6.1
500        75.0       10.0         9.1        12.2
750        75.0       14.9         13.2       16.2
1000       70.0       24.8         21.2       29.4'''    