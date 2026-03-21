# DNA Motif Analyzer

DNA Motif Analyzer to aplikacja napisana w Pythonie do analizy sekwencji DNA i wyszukiwania motywów takich jak ATG, TATA czy CGCG.

---

## 🧬 Opis projektu

Aplikacja umożliwia:

- wczytywanie sekwencji DNA z plików TXT, FASTA i FA,
- pobieranie sekwencji z bazy NCBI,
- wyszukiwanie jednego lub wielu motywów,
- wyznaczanie pozycji wystąpień motywów,
- zliczanie liczby wystąpień,
- analizę segmentową sekwencji,
- porównanie dwóch sekwencji,
- wizualizację wyników (Matplotlib, Plotly),
- eksport wyników do CSV, PDF i JSON,
- interaktywną wizualizację pozycji motywów,
- pracę w trybie GUI oraz CLI.

---

## 🚀 Instalacja i uruchomienie

### 1. Klonowanie repozytorium

```bash
git clone https://github.com/TWOJE_NAZWA_REPO.git
cd dna_motif_analyzer_project
```
### 2. Utworzenie środowiska wirtualnego
```
python -m venv venv
```
### 3. Aktywacja środowiska

Windows:
```
venv\Scripts\activate
```
Linux / macOS:
```
source venv/bin/activate
```
### 4. Instalacja zależności
```
pip install -r requirements.txt
```
### 5. Uruchomienie aplikacji GUI
```
python main.py
```
##### 🧪 Uruchamianie testów
```
pytest
```
#### 💻 Tryb CLI (bez GUI)

Aplikację można uruchomić również w trybie tekstowym:
```
python main.py --file data/example_sequence.fasta --motifs ATG,TATA --segment 10
```
Parametry:

--file – ścieżka do pliku (TXT/FASTA),

--motifs – motywy oddzielone przecinkami,

--segment – długość segmentu (opcjonalnie, domyślnie 10).

#### 📊 Przykładowe użycie GUI
Wybierz plik z sekwencją (Choose first sequence file)
lub pobierz sekwencję z NCBI

Wpisz motywy, np.:

ATG, TATA, CGCG
Ustaw długość segmentu (np. 10)
Kliknij Analyze
Przeglądaj wyniki:
podsumowanie tekstowe,
tabelę wyników,
wykresy,
interaktywną wizualizację.
🧬 Przykładowe accession ID (NCBI)

Możesz użyć:

NM_000518 – ludzka hemoglobina
NC_012920 – mitochondrialne DNA człowieka
📸 Zrzuty ekranu

(Dodaj po wykonaniu screenów)

![Main window](screenshots/main_window.png)
![Results](screenshots/results.png)
![Plots](screenshots/plots.png)

👉 Utwórz folder:

screenshots/
🧠 Funkcjonalności projektu
Wariant minimalny
wczytywanie sekwencji z pliku FASTA/TXT,
wyszukiwanie motywów i ich pozycji,
zliczanie liczby wystąpień,
segmentacja sekwencji,
analiza statystyczna (Pandas),
wykres słupkowy rozmieszczenia motywów,
GUI do wyboru pliku i motywu,
eksport wyników do CSV.
Wariant rozszerzony
pobieranie sekwencji z NCBI (Biopython),
obsługa wielu motywów,
porównanie dwóch sekwencji,
interaktywna wizualizacja (Plotly),
eksport PDF i JSON (pełna sesja),
tryb CLI,
obsługa symboli IUPAC (np. N, R, Y),
dodatkowe statystyki:
GC-content,
AT-content,
gęstość motywów,
tabela wyników (Treeview),
historia analiz,
ulepszone GUI (ttk, układ kolumnowy, status bar).
🧱 Struktura projektu
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
│   └── .gitkeep
│
└── tests
    ├── test_io_utils.py
    ├── test_motif_analysis.py
    └── test_validation_utils.py
🛠 Technologie
Python
Tkinter / ttk
Pandas
NumPy
Matplotlib
Plotly
Biopython
Pytest
📌 Uwagi końcowe
Motywy nakładające się na siebie są poprawnie wykrywane.
Statystyki segmentowe bazują na pozycji startowej motywu.
Wyniki dostępne są w formie tekstowej, tabelarycznej i graficznej.
Aplikacja działa zarówno w trybie GUI, jak i CLI.
👨‍💻 Autor

Projekt wykonany w ramach projektu zaliczeniowego.


---

# 📌 Git (na koniec)

```bash
git add README.md
git commit -m "Finalna wersja README z pełną dokumentacją projektu"
git push

### Segmentacja sekwencji

Motywy przypisywane są do segmentów na podstawie:

- pozycji startowej (domyślnie),
- lub pełnego zawarcia w segmencie.

Opcja ta może być wybrana w ustawieniach analizy.

### Uwagi dotyczące statystyk

Statystyki segmentowe bazują na pozycji startowej motywu lub pełnym jego zawarciu w segmencie (zależnie od wybranej opcji).

W przypadku dłuższych motywów może to wpływać na przypisanie ich do segmentów.