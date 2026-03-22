# 🧬 DNA Motif Analyzer

Aplikacja desktopowa i terminalowa w Pythonie do analizy sekwencji DNA pod kątem występowania motywów takich jak **ATG**, **TATA**, **CGCG** oraz motywów zawierających symbole **IUPAC**.

Projekt realizuje zarówno **wariant minimalny**, jak i **wariant rozszerzony** projektu zaliczeniowego, a dodatkowo został uporządkowany architektonicznie w stylu bardziej zbliżonym do praktycznych aplikacji desktopowych:
- warstwa **GUI**,
- warstwa **controller**,
- warstwa **services**,
- warstwa **state/models**,
- moduły pomocnicze i eksportowe.

---

# 📌 Opis projektu

Program umożliwia analizę sekwencji DNA w dwóch trybach:

- **GUI** — interfejs graficzny oparty o **Tkinter**
- **CLI** — tryb terminalowy uruchamiany z argumentami

Aplikacja pozwala:

- wczytać jedną lub dwie sekwencje z pliku,
- pobrać sekwencję z bazy **NCBI**,
- analizować jeden lub wiele motywów jednocześnie,
- wyznaczać pozycje motywów w sekwencji,
- obliczać statystyki segmentowe,
- porównywać dwie sekwencje,
- generować wykresy statyczne i interaktywne,
- eksportować wyniki do kilku formatów,
- zapisywać historię analiz.

---

# ✅ Spełnienie założeń projektu

## Wariant minimalny

Projekt zawiera:

- wczytanie sekwencji z pliku **FASTA / TXT / FA**
- wyszukiwanie jednego motywu i wyznaczanie jego pozycji
- obliczanie liczby wystąpień motywu
- segmentację sekwencji z użyciem **NumPy / Pandas**
- wizualizację rozmieszczenia motywów na wykresie
- interfejs GUI do wyboru pliku i motywu
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
- testy jednostkowe i prosty test integracyjny dla CLI

---

# 🧠 Funkcjonalności biologiczne

## 🔬 Obsługa motywów IUPAC

Aplikacja obsługuje motywy zawierające symbole IUPAC:

`A, C, G, T, R, Y, S, W, K, M, B, D, H, V, N`

Przykłady:

- `ATN` → `AT` + dowolna baza
- `AR` → `A` + (`A` lub `G`)
- `TGY` → `TG` + (`C` lub `T`)

## Ważna uwaga o interpretacji IUPAC

W aplikacji **symbole IUPAC są aktywnie interpretowane w motywie**, natomiast **niejednoznaczne symbole występujące w samej sekwencji są traktowane dosłownie**.

To oznacza, że:

- motyw `ATN` dopasuje `ATA`, `ATC`, `ATG`, `ATT`, a także `ATN`,
- ale sekwencja zawierająca np. `R`, `Y`, `S` nie jest rozwijana do wszystkich możliwych wariantów.

Takie podejście upraszcza implementację i jest wystarczające dla celów projektu, ale może wpływać na interpretację wyników dla sekwencji zawierających wiele symboli niejednoznacznych.

---

# 📊 Segmentacja sekwencji

Motywy mogą być przypisywane do segmentów na dwa sposoby:

- **start** — motyw przypisywany jest do segmentu na podstawie pozycji początkowej
- **full** — motyw liczony jest tylko wtedy, gdy cały mieści się w obrębie jednego segmentu

---

# 📈 Statystyki obliczane przez program

Aplikacja potrafi wyliczyć m.in.:

- liczbę wystąpień danego motywu,
- pozycje motywu w sekwencji,
- liczbę wystąpień motywu w segmentach,
- **GC-content** całej sekwencji,
- **AT-content** całej sekwencji,
- liczbę nieznanych zasad (`N`),
- gęstość motywów na 1000 nukleotydów,
- średnią liczbę motywów na segment,
- segment o największej liczbie motywów,
- porównanie liczebności motywów między dwiema sekwencjami,
- porównanie częstości motywów w przeliczeniu na 1000 nt.

---

# ⚠️ Dodatkowe uwagi

- motywy nakładające się są wykrywane poprawnie,
- sekwencje mogą zawierać symbole niejednoznaczne IUPAC,
- analiza dopasowań opiera się o regex generowany z motywu,
- logika analityczna została oddzielona od warstwy GUI,
- projekt został uporządkowany architektonicznie względem pierwotnej wersji.

---

# 🏗️ Architektura projektu

Projekt został uporządkowany w bardziej profesjonalny sposób, z podziałem na warstwy odpowiedzialności:

## 1. Controller
- `app_controller.py`

## 2. State / Models
- `app_state.py`

## 3. GUI / View
- `gui_sections.py`
- `gui_helpers.py`
- `gui_windows.py`

## 4. Services
- `analysis_service.py`
- `analysis_handlers.py`
- `export_service.py`
- `motif_analysis.py`
- `report_utils.py`
- `history_utils.py`
- `ncbi_utils.py`
- `validation_utils.py`
- `io_utils.py`

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
│   ├── app_controller.py
│   ├── app_state.py
│   ├── gui_sections.py
│   ├── gui_helpers.py
│   ├── gui_windows.py
│   ├── io_utils.py
│   ├── motif_analysis.py
│   ├── analysis_service.py
│   ├── analysis_handlers.py
│   ├── export_utils.py
│   ├── export_service.py
│   ├── report_utils.py
│   ├── history_utils.py
│   ├── ncbi_utils.py
│   ├── validation_utils.py
│   └── constants.py
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
# 🔧 Instalacja i uruchomienie
## Wymagania
- Python 3.9+
- pip
## Instalacja zależności
```
pip install -r requirements.txt
```
## Uruchomienie aplikacji (GUI)
```
python main.py
```
## Uruchomienie w trybie CLI
```
python main.py data/example_sequence.txt ATG
```
## Uruchomienie testów
```
pytest
```
---
# 🌐 Pobieranie danych z NCBI

### Aplikacja umożliwia pobieranie sekwencji DNA z bazy NCBI GenBank przy użyciu biblioteki Biopython.

Przykład:

- podaj identyfikator sekwencji (np. NM_001200025)
- aplikacja pobierze dane przez API Entrez

⚠️ Uwaga:

- wymagane jest połączenie z Internetem
- NCBI może ograniczać liczbę zapytań (rate limiting)
---
# 🧪 Testy

### Projekt zawiera testy jednostkowe dla:

- analizy motywów
- walidacji danych
- operacji I/O
- integracji aplikacji
- komunikacji z NCBI

### Uruchomienie:
```
pytest
```
---
# 🐙 Repozytorium GitHub

### Projekt dostępny jest w repozytorium:
```
https://github.com/mikalg94/DNA-motif-analyzer
```
### Repozytorium zawiera:

- pełną historię zmian
- kod źródłowy
- testy
- dokumentację
---
# 👨‍💻 Autor

### Michał Grzybała

---

## ⭐ Status projektu

Projekt ukończony w ramach pracy zaliczeniowej i rozwinięty o dodatkowe funkcjonalności oraz refaktoryzację architektury.

---