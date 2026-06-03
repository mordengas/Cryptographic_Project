import random
from collections import defaultdict
class Utils:
    # Normalizacja tekstu
    def normalizuj_tekst(tekst):
        tekst = tekst.lower()
        tekst = tekst.replace('j', 'i')  # łączymy I i J
        tekst = tekst.replace('v', 'w')  # łączymy W i V
        tekst = ''.join([c for c in tekst if c.isalpha()])
        return tekst

    # Funkcja generująca losowy klucz literowy (tablicę 3x8)
    def generuj_losowy_klucz():
        alfabet = list("abcdefghiklmnopqrstuwxyz")  # 24 litery, bez J i V
        random.shuffle(alfabet)
        klucz = ''.join(alfabet)
        return klucz

    # Funkcja generująca losowy klucz cyfrowy (10 unikalnych cyfr)
    def generuj_losowy_klucz_cyfrowy():
        cyfry = list("0123456789")
        random.shuffle(cyfry)
        cyfry = sorted(cyfry[:8]) + cyfry[8:]
        return ''.join(cyfry)

    # Funkcja wyświetlająca tablicę
    def wyswietl_tablice(klucz):
        print("Tablica Monome-Dinome (3 wiersze x 8 kolumn):")
        for wiersz in range(3):
            row_letters = klucz[wiersz*8:(wiersz+1)*8]
            print(f"Wiersz {wiersz+1}: {' '.join(row_letters)}")

    # Funkcje szyfrowania i deszyfrowania
    def szyfruj_monome_dinome(tekst, klucz, cyfry):
        wynik = ""
        for znak in tekst:
            if znak not in klucz:
                wynik += znak
                continue
            pozycja = klucz.index(znak)
            wiersz = pozycja // 8
            kolumna = pozycja % 8
            if wiersz == 0:
                wynik += cyfry[kolumna]
            else:
                wynik += cyfry[8 + wiersz - 1] + cyfry[kolumna]
        return wynik

    def deszyfruj_monome_dinome(szyfrogram, klucz, cyfry):
        wynik = ""
        i = 0
        while i < len(szyfrogram):
            znak = szyfrogram[i]
            if znak not in cyfry:
                wynik += znak
                i += 1
                continue
            if znak in cyfry[8:10]:
                wiersz = cyfry.index(znak) - 7
                i += 1
                if i >= len(szyfrogram):
                    break
                kolumna_znak = szyfrogram[i]
                if kolumna_znak not in cyfry[:8]:
                    i += 1
                    continue
                kolumna = cyfry.index(kolumna_znak)
                pozycja = wiersz * 8 + kolumna
                wynik += klucz[pozycja]
                i += 1
                
            else:
                kolumna = cyfry.index(znak)
                pozycja = kolumna
                wynik += klucz[pozycja]
                i += 1
                
        return wynik
    
    def find_two_most_frequent_followers(digits):

        # Zliczamy ile razy każda cyfra występuje PO danej cyfrze
        follower_counts = defaultdict(int)

        for i in range(len(digits) - 1):
            pair = digits[i:i+2]
            follower = pair[1]
            follower_counts[follower] += 1

        # Sortujemy po liczbie wystąpień malejąco i bierzemy 2 najczęstsze cyfry
        most_common = sorted(follower_counts.items(), key=lambda x: -x[1])[:2]

        # Zwracamy jako string, np. '08' jeśli '0' i '8' są najczęstsze
        return ''.join([digit for digit, _ in most_common])