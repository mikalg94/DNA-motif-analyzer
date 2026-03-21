# 🧬 DNA Motif Analyzer

Aplikacja w Pythonie do analizy sekwencji DNA i wyszukiwania motywów takich jak **ATG, TATA, CGCG** oraz motywów zawierających symbole **IUPAC**.

Projekt realizuje zarówno wariant minimalny, jak i rozszerzony projektu zaliczeniowego.

---

# 📌 Opis projektu

Aplikacja umożliwia analizę sekwencji DNA w dwóch trybach:
- **GUI** (interfejs graficzny oparty o Tkinter),
- **CLI** (uruchamianie z terminala).

Program pozwala:
- wczytać sekwencję z pliku,
- pobrać sekwencję z bazy NCBI,
- wyszukiwać jeden lub wiele motywów,
- analizować ich rozmieszczenie w segmentach,
- porównywać dwie sekwencje,
- eksportować wyniki do plików.

---

# ✅ Spełnienie założeń projektu

## Wariant minimalny
- wczytanie sekwencji z pliku **FASTA / TXT / FA**
- wyszukiwanie jednego motywu i jego pozycji
- obliczanie liczby wystąpień
- segmentacja sekwencji z użyciem **NumPy / Pandas**
- wizualizacja rozmieszczenia motywów na wykresie słupkowym
- GUI do wyboru pliku i motywu
- eksport wyników do **CSV**

## Wariant rozszerzony
- pobieranie sekwencji z **NCBI** przez **Entrez API (Biopython)**
- obsługa wielu motywów jednocześnie
- porównanie dwóch sekwencji
- interaktywna wizualizacja rozmieszczenia motywów (**Plotly / HTML**)
- eksport rozszerzony:
  - **CSV**
  - **PDF**
  - **JSON**
- dodatkowe statystyki:
  - **GC-content**
  - **AT-content**
  - **gęstość motywów**
  - **średnia liczba motywów na segment**
- historia analiz
- tryb CLI

---

# 🧠 Funkcjonalności biologiczne

## 🔬 Obsługa motywów IUPAC

Motywy mogą zawierać symbole:
`A, C, G, T, R, Y, S, W, K, M, B, D, H, V, N`

Przykłady:
- `ATN` → `AT` + dowolna baza
- `AR` → `A` + (`A` lub `G`)

## Ważna uwaga o interpretacji IUPAC

W aplikacji **symbole IUPAC są interpretowane aktywnie w motywie**, natomiast **symbole niejednoznaczne występujące w samej sekwencji są traktowane dosłownie**.

To oznacza, że:
- motyw `ATN` dopasuje np. `ATA`, `ATC`, `ATG`, `ATT`,
- ale sekwencja zawierająca symbole takie jak `R`, `Y`, `S` nie jest rozwijana do wszystkich możliwych wariantów.

Takie rozwiązanie upraszcza implementację i jest wystarczające dla celów projektu, ale może wpływać na wyniki dla sekwencji zawierających wiele symboli niejednoznacznych.

---

# 📊 Segmentacja sekwencji

Motywy przypisywane są do segmentów na podstawie:
- pozycji startowej motywu (`start`) — domyślnie,
- lub pełnego zawarcia motywu w segmencie (`full`).

---

# ⚠️ Dodatkowe uwagi

- motywy nakładające się są wykrywane poprawnie,
- sekwencje mogą zawierać symbole niejednoznaczne IUPAC,
- analiza działa na dopasowaniu regex generowanym z motywu,
- GUI i logika analizy są rozdzielone na osobne moduły,
- logika aplikacji została pokryta testami jednostkowymi.

---

# 🧱 Struktura projektu

```text
dna_motif_analyzer_project
│
├── main.py
├── README.md
├── requirements.txt
├── .gitignore
├── pytest.ini
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
│   ├── .gitkeep
│   └── interactive_motif_positions.html
│
└── tests
    ├── test_export_utils.py
    ├── test_io_utils.py
    ├── test_main.py
    ├── test_motif_analysis.py
    ├── test_ncbi_utils.py
    └── test_validation_utils.py
```
---

# 🚀 Instalacja i uruchomienie

## 1. Klonowanie repozytorium
```
git clone https://github.com/mikalg94/DNA-motif-analyzer.git
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
### Ważna uwaga o CLI

Jeżeli użytkownik uruchamia program z argumentami CLI, musi podać jednocześnie:

--file

--motifs

#### W przeciwnym razie program zwróci błąd parsera zamiast uruchamiać GUI.



# 🧪 Testy
```
pytest
```

### Testy obejmują:

- wczytywanie danych,
- walidację sekwencji i motywów,
- analizę motywów,
- eksport wyników,
- logikę pobierania danych z NCBI,
- zachowanie trybu CLI.
---

# 📊 Wizualizacje

### Aplikacja oferuje:

- wykres rozmieszczenia motywu w segmentach,
- wykres pozycji motywów na osi sekwencji,
- wykres zbiorczy dla wielu motywów,
- wykres GC-content,
- porównanie GC-content dla dwóch sekwencji,
- wykres interaktywny HTML (Plotly),
- podświetlanie motywów bezpośrednio w sekwencji.

---

# 📦 Eksport danych

### Program pozwala eksportować:

- CSV – tabela wyników,
- JSON – zapis sesji analizy,
- PDF – raport z podsumowaniem i wykresami,
- PNG – zapis wykresu.

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

### Projekt wykonany w ramach pracy zaliczeniowej.
