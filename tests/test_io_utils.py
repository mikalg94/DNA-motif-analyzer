import os
import tempfile

from src.io_utils import load_sequence_from_fasta, load_sequence_from_txt


def test_load_sequence_from_txt():
    with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False) as f:
        f.write("ATGC ATGC\nATGC")
        path = f.name

    try:
        sequence = load_sequence_from_txt(path)
        assert sequence == "ATGCATGCATGC"
    finally:
        if os.path.exists(path):
            os.remove(path)


def test_load_sequence_from_fasta():
    with tempfile.NamedTemporaryFile("w+", suffix=".fasta", delete=False) as f:
        f.write(">Example\nATGCATGC\nATGC")
        path = f.name

    try:
        sequence = load_sequence_from_fasta(path)
        assert sequence == "ATGCATGCATGC"
    finally:
        if os.path.exists(path):
            os.remove(path)