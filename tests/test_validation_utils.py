import pytest

from src.validation_utils import (
    get_sequence_warning,
    normalize_motifs,
    normalize_sequence,
    validate_dna_sequence,
    validate_motifs_against_sequence,
    validate_motif,
)


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


def test_normalize_sequence_removes_all_whitespace():
    sequence = "ATG C\tTA\nGG\r"
    assert normalize_sequence(sequence) == "ATGCTAGG"


def test_validate_motifs_against_sequence_too_long():
    with pytest.raises(ValueError):
        validate_motifs_against_sequence(["ATGCGT"], "ATG")


def test_validate_motifs_against_sequence_valid():
    validate_motifs_against_sequence(["ATG", "TA"], "ATGCGT")


def test_get_sequence_warning_for_many_unknown_bases():
    warning = get_sequence_warning("ATGNNNNNNN")
    assert warning is not None
    assert "unknown nucleotides" in warning


def test_get_sequence_warning_for_clean_sequence():
    warning = get_sequence_warning("ATGCGTATGC")
    assert warning is None

def test_validate_motif_iupac_valid():
    validate_motif("ATRYN")


def test_validate_motif_iupac_invalid():
    with pytest.raises(ValueError):
        validate_motif("ATZ")