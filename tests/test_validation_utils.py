import pytest

from src.validation_utils import normalize_motifs, validate_dna_sequence, validate_motif


def test_validate_dna_sequence_valid():
    validate_dna_sequence("ATCGN")


def test_validate_dna_sequence_invalid():
    with pytest.raises(ValueError):
        validate_dna_sequence("ATXB")


def test_validate_motif_invalid():
    with pytest.raises(ValueError):
        validate_motif("ATX")


def test_normalize_motifs():
    motifs = normalize_motifs([" atg ", "TATA", "atg"])
    assert motifs == ["ATG", "TATA"]


def test_normalize_motifs_empty_values():
    motifs = normalize_motifs([" ", "   ", ""])
    assert motifs == []


def test_validate_dna_sequence_empty():
    with pytest.raises(ValueError):
        validate_dna_sequence("")