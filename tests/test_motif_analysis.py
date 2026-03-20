from src.motif_analysis import (
    build_statistics_dataframe,
    compare_sequences,
    count_motif_occurrences,
    find_motif_positions,
    segment_sequence,
)


def test_find_motif_positions():
    sequence = "ATGCGTATGCGTATG"
    motif = "ATG"
    assert find_motif_positions(sequence, motif) == [0, 6, 12]


def test_count_motif_occurrences():
    sequence = "ATGCGTATGCGTATG"
    motif = "ATG"
    assert count_motif_occurrences(sequence, motif) == 3


def test_segment_sequence():
    sequence = "ATGCGTATGCGT"
    assert segment_sequence(sequence, 4) == ["ATGC", "GTAT", "GCGT"]


def test_build_statistics_dataframe():
    sequence = "ATGATGATG"
    motif = "ATG"
    df = build_statistics_dataframe(sequence, motif, segment_length=3)
    assert len(df) == 3
    assert df["motif_count"].sum() == 3


def test_compare_sequences():
    seq1 = "ATGATGTATA"
    seq2 = "ATGTATATATA"
    motifs = ["ATG", "TATA"]

    df = compare_sequences(seq1, seq2, motifs)

    assert "motif" in df.columns
    assert "sequence_1_count" in df.columns
    assert "sequence_2_count" in df.columns
    assert len(df) == 2