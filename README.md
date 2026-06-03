# Cryptographic_Project: Monome-Dinome Cipher Attack

**Author:** Dominik Machnik

## 🧠 Project Overview
This is a simple university project focused on breaking the **Monome-Dinome** substitution cipher. It implements a **Hill Climbing** attack combined with **n-gram analysis** to automatically decrypt ciphertexts without knowing the key.

The project supports breaking ciphertexts in two language variants: **English** and **Czech**.

## ⚙️ Specifications and Versions

### 🇬🇧 English Language (`attack.py`)
* **Cipher Table:** 3x8
* **Key:** 24-character letter key + 2-digit numerical key (representing rows).
* **Efficiency:** Best decryption results are achieved with ciphertexts of at least **500 characters** in length.

### 🇨🇿 Czech Language (`attack_cz.py`)
* **Cipher Table:** 4x10
* **Key:** 40-character letter key + 3-character numerical key (containing digits and letters A, B, C).
* **Efficiency:** The attack requires texts of at least **1000 characters**. Cryptanalysis of the Czech language is significantly harder due to the heavy presence of diacritics.

## 🛠️ Architecture and Files
* `attack.py` - Main script executing the Hill Climbing attack for the English language.
* `attack_cz.py` - Script performing the attack for the Czech language, accommodating the larger 4x10 table.
* `Ngrams.py` - Module responsible for loading n-gram datasets and calculating the logarithmic probability score for the evaluated text.
* `Utils.py` / `UtilsCz.py` - Utility classes handling encryption, decryption, text normalization, and detection of the most frequent consecutive digits.

## 🚀 How to Run
Ensure that the necessary n-gram text files (e.g., `english_quadgrams_fixed.txt`, `czech_quadgrams_fixed.txt`) and sample plaintexts (`plaintext2_en.txt`, `plaintext_cz.txt`) are present in the root directory.

Then, run one of the scripts in your terminal:

```bash
# For the English version:
python attack.py

# For the Czech version:
python attack_cz.py
