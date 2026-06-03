import random
from collections import defaultdict
class UtilsCz:
    # Normalizacja tekstu
    def normalizuj_tekst(tekst):
        tekst = tekst.lower()
        tekst = tekst.replace('ó', 'o')  # łączymy ó i o
        tekst = ''.join([c for c in tekst if c.isalpha()])
        return tekst

    # Funkcja generująca losowy klucz literowy (tablicę 4x10)
    def generuj_losowy_klucz():
        alfabet = list("abcdefghijklmnopqrstuvwxyzáčďéěíňřšťúůýž")  # 40 liter, bez ó
        random.shuffle(alfabet)
        klucz = ''.join(alfabet)
        return klucz

    # Funkcja generująca losowy klucz cyfrowy
    def generuj_losowy_klucz_cyfrowy():
        cyfry = list("0123456789ABC")
        random.shuffle(cyfry)
        cyfry = sorted(cyfry[:10]) + cyfry[10:]
        return ''.join(cyfry)

    # Funkcja wyświetlająca tablicę
    def wyswietl_tablice(klucz):
        print("Tablica Monome-Dinome (4wiersze x 10 kolumn):")
        for wiersz in range(4):
            row_letters = klucz[wiersz*10:(wiersz+1)*10]
            print(f"Wiersz {wiersz+1}: {' '.join(row_letters)}")

    # Szyfrowanie Monome-Dinome
    def szyfruj_monome_dinome(tekst, klucz, cyfry):
        wynik = ""
        for znak in tekst:
            if znak not in klucz:
                wynik += znak
                continue
            pozycja = klucz.index(znak)
            wiersz = pozycja // 10
            kolumna = pozycja % 10
            if wiersz == 0:
                wynik += cyfry[kolumna]
            else:
                wynik += cyfry[10 + wiersz - 1] + cyfry[kolumna]
        return wynik

    # Deszyfrowanie Monome-Dinome
    def deszyfruj_monome_dinome(szyfrogram, klucz, cyfry):
        wynik = ""
        i = 0
        while i < len(szyfrogram):
            znak = szyfrogram[i]
            if znak not in cyfry:
                wynik += znak
                i += 1
                continue
            if znak in cyfry[10:13]:  # zakładamy 3 cyfry dla wierszy 1-3
                wiersz = cyfry.index(znak) - 9
                i += 1
                if i >= len(szyfrogram):
                    break
                kolumna_znak = szyfrogram[i]
                if kolumna_znak not in cyfry[:10]:
                    i += 1
                    continue
                kolumna = cyfry.index(kolumna_znak)
                pozycja = wiersz * 10 + kolumna
                wynik += klucz[pozycja]
                i += 1
            else:
                kolumna = cyfry.index(znak)
                pozycja = kolumna
                wynik += klucz[pozycja]
                i += 1
        return wynik

    # Najczęstsze dwie cyfry po sobie
    def find_three_most_frequent_followers(digits):
        follower_counts = defaultdict(int)
        for i in range(len(digits) - 1):
            pair = digits[i:i+2]
            follower = pair[1]
            follower_counts[follower] += 1
        most_common = sorted(follower_counts.items(), key=lambda x: -x[1])[:3]
        return ''.join([digit for digit, _ in most_common])