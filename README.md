# 🧬 DNA Motif Analyzer

Aplikacja w Pythonie do analizy sekwencji DNA i wyszukiwania motywów takich jak **ATG, TATA, CGCG** oraz motywów z symbolami **IUPAC**.

Projekt realizuje zarówno wariant minimalny, jak i rozszerzony projektu zaliczeniowego.

---

# 📌 Opis projektu

Aplikacja umożliwia:

## ✅ Wariant minimalny
- wczytywanie sekwencji DNA z plików **TXT / FASTA / FA**
- wyszukiwanie motywów i ich pozycji
- zliczanie liczby wystąpień
- segmentację sekwencji (NumPy / Pandas)
- analizę statystyczną
- wizualizację (wykres słupkowy)
- GUI do wyboru pliku i motywu
- eksport wyników do **CSV**

## 🚀 Wariant rozszerzony
- pobieranie sekwencji z **NCBI (GenBank API – Biopython)**
- obsługa wielu motywów jednocześnie
- porównanie dwóch sekwencji
- interaktywna wizualizacja (Plotly – HTML)
- eksport:
  - CSV
  - PDF (raport)
  - JSON (sesja)
- dodatkowe statystyki:
  - GC-content
  - AT-content
  - gęstość motywów
- historia analiz
- tryb CLI (bez GUI)
- obsługa symboli IUPAC (np. N, R, Y)

---

# 🧠 Funkcjonalności biologiczne

### 🔬 Obsługa motywów IUPAC
Motywy mogą zawierać symbole:
A, C, G, T, R, Y, S, W, K, M, B, D, H, V, N

Np.:
- ATN → AT + dowolna baza
- AR → A + (A lub G)

---

### 📊 Segmentacja sekwencji

Motywy przypisywane są do segmentów na podstawie:
- pozycji startowej (domyślnie)
- lub pełnego zawarcia w segmencie

---

### ⚠️ Uwagi
- motywy nakładające się są wykrywane poprawnie
- sekwencje mogą zawierać symbole niejednoznaczne (IUPAC)
- analiza działa na dopasowaniu regex (motyw → sekwencja)

---

# 🧱 Struktura projektu

dna_motif_analyzer_project
│
├── main.py
├── README.md
├── requirements.txt
├── .gitignore
│
├── src
│   ├── __init__.py
│   ├── app.py
│   ├── gui_sections.py
│   ├── io_utils.py
│   ├── motif_analysis.py
│   ├── export_utils.py
│   ├── ncbi_utils.py
│   └── validation_utils.py
│
├── data
│   ├── example_sequence.txt
│   └── example_sequence.fasta
│
├── results
│   ├── interactive_motif_positions.html
│   └── .gitkeep
│
└── tests
    ├── test_io_utils.py
    ├── test_motif_analysis.py
    ├── test_validation_utils.py
    ├── test_export_utils.py
    └── test_ncbi_utils.py

---

# 🚀 Instalacja i uruchomienie

## 1. Klonowanie repozytorium
```
git clone https://github.com/mikalg94.git
cd dna_motif_analyzer_project
```
## 2. Środowisko wirtualne
```
python -m venv venv
```
Windows:
```
venv\Scripts\activate
```
Linux / macOS:
```
source venv/bin/activate
```
## 3. Instalacja zależności
```
pip install -r requirements.txt
```
---

# ▶️ Uruchomienie aplikacji

## GUI
```
python main.py
```
## CLI
```
python main.py --file data/example_sequence.fasta --motifs ATG,TATA --segment 10
```
---

# 🧪 Testy
```
pytest
```
---

# 📊 Wizualizacje

Aplikacja oferuje:
- wykres rozmieszczenia motywów
- wykres pozycji motywów
- wykres GC-content
- porównanie GC między sekwencjami
- interaktywny wykres HTML (Plotly)

---

# 📦 Eksport danych

- CSV – tabela wyników
- JSON – cała sesja analizy
- PDF – raport z wykresami

---

# ⚙️ Technologie

- Python
- Tkinter / ttk
- Pandas
- NumPy
- Matplotlib
- Plotly
- Biopython
- Pytest

---

# 🧑‍💻 Autor
## Michał Grzybała

Projekt wykonany w ramach projektu zaliczeniowego.
