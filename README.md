# DNA Motif Analyzer

DNA Motif Analyzer to aplikacja napisana w Pythonie do analizy sekwencji DNA i wyszukiwania motywów takich jak ATG, TATA czy CGCG.

## Opis projektu

Aplikacja umożliwia:
- wczytywanie sekwencji DNA z plików TXT, FASTA i FA,
- pobieranie sekwencji z bazy NCBI,
- wyszukiwanie jednego lub wielu motywów,
- wyznaczanie pozycji wystąpień motywów,
- zliczanie liczby wystąpień,
- analizę segmentową sekwencji,
- porównanie dwóch sekwencji,
- eksport wyników do CSV,
- zapis wykresów do PNG,
- generowanie raportów PDF,
- interaktywną wizualizację pozycji motywów.

## Zaimplementowane funkcjonalności

### Wariant minimalny
- wczytywanie sekwencji z pliku FASTA/TXT,
- wyszukiwanie motywu i jego pozycji,
- obliczanie liczby wystąpień,
- segmentacja sekwencji,
- analiza statystyczna z użyciem Pandas,
- wykres słupkowy rozmieszczenia motywów,
- GUI do wyboru pliku i motywu,
- eksport wyników do CSV.

### Wariant rozszerzony
- pobieranie sekwencji z NCBI,
- obsługa wielu motywów jednocześnie,
- porównanie dwóch sekwencji,
- interaktywna wizualizacja pozycji motywów,
- eksport CSV i PDF z wykresem.

## Technologie
- Python
- Tkinter
- Pandas
- NumPy
- Matplotlib
- Plotly
- Biopython
- Pytest

## Struktura projektu

```text
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