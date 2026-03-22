# 🧬 DNA Motif Analyzer

Aplikacja w Pythonie do analizy sekwencji DNA i wyszukiwania motywów takich jak **ATG, TATA, CGCG** oraz motywów zawierających symbole **IUPAC**.

Projekt realizuje zarówno wariant minimalny, jak i rozszerzony projektu zaliczeniowego.

---

# 📌 Opis projektu

Aplikacja umożliwia analizę sekwencji DNA w dwóch trybach:
- **GUI** (interfejs graficzny oparty o Tkinter),
- **CLI** (uruchamianie z terminala).

Program pozwala:
- wczytać jedną lub dwie sekwencje z pliku,
- pobrać sekwencję z bazy NCBI,
- wyszukiwać jeden lub wiele motywów,
- analizować ich rozmieszczenie w segmentach,
- porównywać dwie sekwencje,
- wizualizować wyniki,
- eksportować dane do wielu formatów.

---

# ✅ Spełnienie założeń projektu

## Wariant minimalny
Projekt zawiera:
- wczytanie sekwencji z pliku **FASTA / TXT / FA**
- wyszukiwanie jednego motywu i jego pozycji
- obliczanie liczby wystąpień
- segmentację sekwencji z użyciem **NumPy / Pandas**
- wizualizację rozmieszczenia motywów na wykresie słupkowym
- GUI do wyboru pliku i motywu
- eksport wyników do **CSV**

## Wariant rozszerzony
Projekt zawiera:
- pobieranie sekwencji z **NCBI** przez **Entrez API (Biopython)**
- obsługę wielu motywów jednocześnie
- porównanie dwóch sekwencji
- interaktywną wizualizację rozmieszczenia motywów (**Plotly / HTML**)
- eksport rozszerzony:
  - **CSV**
  - **PDF**
  - **JSON**
  - **PNG**
- osobny raport PDF dla porównania dwóch sekwencji
- dodatkowe statystyki:
  - **GC-content**
  - **AT-content**
  - **gęstość motywów**
  - **średnia liczba motywów na segment**
- historię analiz
- tryb CLI
- test integracyjny dla trybu CLI
- opcjonalny pasek postępu przy pobieraniu z NCBI

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

Dzięki temu użytkownik może zdecydować, czy motyw ma być liczony:
- bardziej liberalnie,
- czy tylko wtedy, gdy cały znajduje się w obrębie jednego segmentu.

---

# ⚠️ Dodatkowe uwagi

- motywy nakładające się są wykrywane poprawnie,
- sekwencje mogą zawierać symbole niejednoznaczne IUPAC,
- analiza działa na dopasowaniu regex generowanym z motywu,
- GUI i logika analizy są rozdzielone na osobne moduły,
- logika aplikacji została pokryta testami jednostkowymi i częściowo testami integracyjnymi.

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
    ├── test_main_integration.py
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
## 2. Utworzenie środowiska wirtualnego
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
### Przykład z innym trybem segmentacji
```
python main.py --file data/example_sequence.fasta --motifs ATG,TATA,CGCG --segment 8 --mode full
```
### Ważna uwaga o CLI

Jeżeli użytkownik uruchamia program z argumentami CLI, musi podać jednocześnie:

--file

--motifs

#### W przeciwnym razie program zwróci błąd parsera zamiast uruchamiać GUI.

# 🖥️ Obsługa interfejsu GUI
## Sekcja Sequence files
### - Choose first sequence file – wczytuje pierwszą sekwencję z pliku
### - Choose second sequence file – wczytuje drugą sekwencję z pliku

### - Obsługiwane formaty:
- .txt
- .fasta
- .fa
## - Sekcja NCBI download
### - First NCBI accession ID – identyfikator pierwszej sekwencji
### - Second NCBI accession ID – identyfikator drugiej sekwencji
### - Email for NCBI – adres wymagany przez Entrez API
### - Fetch first from NCBI – pobiera pierwszą sekwencję
### - Fetch second from NCBI – pobiera drugą sekwencję
### - Load Example (Human Hemoglobin) – przykładowa sekwencja testowa
### - Load Example (Mitochondrial DNA) – druga przykładowa sekwencja testowa

Podczas pobierania z NCBI aplikacja może wyświetlić okno z paskiem postępu.

## - Sekcja Analysis settings
Motif assignment mode
start – przypisanie do segmentu po pozycji startowej
full – przypisanie tylko jeśli motyw mieści się cały w segmencie
Enter motifs separated by commas – lista motywów oddzielonych przecinkami
Select motif for plot/PDF – wybór motywu do szczegółowego wykresu i raportu PDF
Segment length – długość segmentu
Sort results
original
count_desc
count_asc
Show only found motifs – ukrywa motywy z liczbą wystąpień równą zero
Top N motifs (optional) – ogranicza liczbę wyświetlanych wyników
Sekcja Actions
Analysis
Analyze Sequence 1
Analyze Sequence 2
Compare Sequences
Visualization
Show Distribution Plot – wykres słupkowy liczby motywów w segmentach
Show Multi-Motif Summary – wykres zbiorczy dla wielu motywów
Show Motif Positions – pozycje motywów na osi sekwencji
Save Positions Plot as PNG – zapis wykresu pozycji motywów do pliku PNG
Show Highlighted Sequence – wyświetlenie sekwencji z podświetlonymi motywami
Open Interactive Motif Plot – interaktywny wykres HTML
Show GC Content Plot – wykres GC-content
Compare GC Content – porównanie GC-content między dwiema sekwencjami
GC + Motif Overlay – nakładka GC-content i pozycji motywów
Export
Export CSV – zapis wyników do CSV
Export JSON – zapis sesji analizy do JSON
Save Plot as PNG – zapis wykresu rozkładu motywu do PNG
Export PDF
dla pojedynczej analizy tworzy raport analityczny,
dla porównania tworzy raport porównawczy.
Other
Show Analysis History – historia wykonanych analiz
Toggle Theme – zmiana motywu interfejsu
Sekcja Results
Text Summary – opis tekstowy wyników
Table – tabela ze statystykami segmentów lub porównaniem sekwencji

# 🧪 Testy
```
pytest
```

### Testy obejmują:

wczytywanie danych,
walidację sekwencji i motywów,
analizę motywów,
eksport wyników,
logikę pobierania danych z NCBI,
zachowanie trybu CLI,
integracyjny przepływ działania run_cli.
---

📊 Wizualizacje

Aplikacja oferuje:

- wykres rozmieszczenia motywu w segmentach,
- wykres pozycji motywów na osi sekwencji,
- wykres zbiorczy dla wielu motywów,
- wykres GC-content,
- porównanie GC-content dla dwóch sekwencji,
- wykres interaktywny HTML (Plotly),
- podświetlanie motywów bezpośrednio w sekwencji,
- zapis wykresów do PNG.
---

📦 Eksport danych

Program pozwala eksportować:

CSV – tabela wyników,
JSON – zapis sesji analizy,
PDF – raport z podsumowaniem i wykresami,
PDF porównawczy – raport dla dwóch sekwencji,
PNG – zapis wykresu rozkładu motywu,
PNG – zapis wykresu pozycji motywów.

---

# ⚙️ Technologie

Python
Tkinter / ttk
Pandas
NumPy
Matplotlib
Plotly
Biopython
Pytest

---

# 🧑‍💻 Autor
## Michał Grzybała

### Projekt wykonany w ramach pracy zaliczeniowej.
