# DNA Motif Analyzer

DNA Motif Analyzer to aplikacja napisana w Pythonie służąca do analizy sekwencji DNA oraz wykrywania wybranych motywów sekwencyjnych, takich jak ATG, TATA czy CGCG.

## Opis projektu

Celem projektu jest stworzenie narzędzia umożliwiającego:
- wczytywanie sekwencji DNA z plików,
- wyszukiwanie motywów w sekwencji,
- analizę statystyczną ich występowania,
- wizualizację rozmieszczenia motywów,
- eksport wyników,
- pobieranie danych z bazy NCBI.

Projekt łączy elementy programowania w Pythonie z podstawami bioinformatyki.

---

## Funkcjonalności

### Aktualnie zaimplementowane
- obsługa plików TXT
- obsługa plików FASTA
- pobieranie sekwencji z NCBI GenBank
- wyszukiwanie jednego lub wielu motywów
- określanie pozycji wystąpień
- zliczanie liczby wystąpień
- podział sekwencji na segmenty
- generowanie statystyk segmentowych

### Rozwijane funkcje
- eksport wyników do CSV
- zapis wykresów do PNG
- generowanie raportów PDF
- porównanie dwóch sekwencji
- rozszerzona wizualizacja rozmieszczenia motywów

---

## Technologie

- Python
- Tkinter
- Pandas
- NumPy
- Matplotlib
- Biopython

---

## Uruchomienie projektu

```bash
pip install -r requirements.txt
python main.py
```

---

## Testy

Aby uruchomić testy:

```bash
pytest
```