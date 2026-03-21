import pytest

from src.ncbi_utils import fetch_sequence_from_ncbi


class MockHandle:
    def __init__(self, data):
        self.data = data

    def read(self):
        return self.data

    def close(self):
        pass


def test_fetch_sequence_from_ncbi_success(monkeypatch):
    fasta_data = ">Mock sequence\nATGCGTATGC\n"

    def mock_efetch(db, id, rettype, retmode):
        return MockHandle(fasta_data)

    monkeypatch.setattr("src.ncbi_utils.Entrez.efetch", mock_efetch)

    sequence = fetch_sequence_from_ncbi("TEST123", "test@example.com")
    assert sequence == "ATGCGTATGC"


def test_fetch_sequence_from_ncbi_empty_accession():
    with pytest.raises(ValueError, match="Accession ID cannot be empty."):
        fetch_sequence_from_ncbi("", "test@example.com")


def test_fetch_sequence_from_ncbi_empty_email():
    with pytest.raises(ValueError, match="Email is required for NCBI access."):
        fetch_sequence_from_ncbi("TEST123", "")


def test_fetch_sequence_from_ncbi_empty_response(monkeypatch):
    def mock_efetch(db, id, rettype, retmode):
        return MockHandle("")

    monkeypatch.setattr("src.ncbi_utils.Entrez.efetch", mock_efetch)

    with pytest.raises(RuntimeError, match="NCBI download failed"):
        fetch_sequence_from_ncbi("TEST123", "test@example.com")