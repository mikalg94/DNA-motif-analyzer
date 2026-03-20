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

### Wczytywanie danych
- obsługa plików **TXT**
- obsługa plików **FASTA**
- pobieranie sekwencji z **NCBI GenBank**

### Analiza motywów
- wyszukiwanie jednego motywu
- wyszukiwanie wielu motywów jednocześnie
- określanie pozycji wystąpień
- zliczanie liczby wystąpień

### Analiza statystyczna
- podział sekwencji na segmenty
- liczenie wystąpień motywów w segmentach
- tworzenie zestawień statystycznych (Pandas)

### Wizualizacja
- wykres słupkowy rozmieszczenia motywów
- generowanie wykresów przy użyciu Matplotlib

### Eksport danych
- zapis wyników do pliku **CSV**
- zapis wykresów do **PNG**
- generowanie raportu **PDF**

### Interfejs graficzny
- wybór pliku
- wpisywanie motywów
- uruchamianie analizy
- wyświetlanie wyników

---

## Technologie

Projekt wykorzystuje następujące technologie:

- Python
- Tkinter (GUI)
- Pandas (analiza danych)
- NumPy (operacje numeryczne)
- Matplotlib (wizualizacja)
- Biopython (NCBI API)

---

## Struktura projektu
dna_motif_analyzer_project
│
├── main.py
├── README.md
├── requirements.txt
│
├── src
│   ├── app.py
│   ├── io_utils.py
│   ├── motif_analysis.py
│   ├── export_utils.py
│   └── ncbi_utils.py
│
├── data
│   ├── example_sequence.txt
│   └── example_sequence.fasta
│
└── results