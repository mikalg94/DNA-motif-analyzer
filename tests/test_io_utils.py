import tempfile
from src.io_utils import load_sequence_from_txt, load_sequence_from_fasta


def test_load_sequence_from_txt():
    with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False) as f:
        f.write("ATGC ATGC\nATGC")
        path = f.name

    sequence = load_sequence_from_txt(path)
    assert sequence == "ATGCATGCATGC"


def test_load_sequence_from_fasta():
    with tempfile.NamedTemporaryFile("w+", suffix=".fasta", delete=False) as f:
        f.write(">Example\nATGCATGC\nATGC")
        path = f.name

    sequence = load_sequence_from_fasta(path)
    assert sequence == "ATGCATGCATGC"