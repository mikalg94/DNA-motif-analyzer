from src.motif_analysis import (
    build_statistics_dataframe,
    compare_sequences,
    count_motif_occurrences,
    count_motif_in_segments,
    find_motif_positions,
    segment_sequence,
)


def test_find_motif_positions():
    sequence = "ATGCGTATGCGTATG"
    motif = "ATG"
    assert find_motif_positions(sequence, motif) == [0, 6, 12]


def test_find_overlapping_motif_positions():
    sequence = "ATATA"
    motif = "ATA"
    assert find_motif_positions(sequence, motif) == [0, 2]


def test_count_motif_occurrences():
    sequence = "ATGCGTATGCGTATG"
    motif = "ATG"
    assert count_motif_occurrences(sequence, motif) == 3


def test_segment_sequence():
    sequence = "ATGCGTATGCGT"
    assert segment_sequence(sequence, 4) == ["ATGC", "GTAT", "GCGT"]


def test_count_motif_in_segments():
    sequence = "ATGAAATGCCATG"
    motif = "ATG"
    counts = count_motif_in_segments(sequence, motif, segment_length=5)
    assert counts == [1, 1, 1]


def test_count_motif_in_segments_full_mode():
    sequence = "ATGAAATG"
    motif = "TGA"
    counts = count_motif_in_segments(sequence, motif, segment_length=4, mode="full")
    assert counts == [1, 0]


def test_build_statistics_dataframe():
    sequence = "ATGATGATG"
    motif = "ATG"
    df = build_statistics_dataframe(sequence, motif, segment_length=3)

    assert len(df) == 3
    assert df["motif_count"].sum() == 3
    assert "motif_positions" in df.columns
    assert "segment_length" in df.columns


def test_build_statistics_dataframe_full_mode():
    sequence = "ATGAAATG"
    motif = "TGA"
    df = build_statistics_dataframe(sequence, motif, segment_length=4, mode="full")

    assert df["motif_count"].sum() == 1
    assert df.loc[0, "motif_count"] == 1
    assert df.loc[1, "motif_count"] == 0


def test_compare_sequences():
    seq1 = "ATGATGTATA"
    seq2 = "ATGTATATATA"
    motifs = ["ATG", "TATA"]

    df = compare_sequences(seq1, seq2, motifs)

    assert "motif" in df.columns
    assert "sequence_1_count" in df.columns
    assert "sequence_2_count" in df.columns
    assert "sequence_1_per_1000_nt" in df.columns
    assert "sequence_2_per_1000_nt" in df.columns
    assert "count_difference" in df.columns
    assert len(df) == 2


def test_find_motif_positions_with_iupac_n():
    sequence = "ATGATCATAATT"
    motif = "ATN"
    assert find_motif_positions(sequence, motif) == [0, 3, 6, 9]


def test_find_motif_positions_with_iupac_r():
    sequence = "AAAGACAT"
    motif = "AR"
    assert find_motif_positions(sequence, motif) == [0, 1, 2]


def test_count_motif_occurrences_with_iupac():
    sequence = "ATGATCATA"
    motif = "ATN"
    assert count_motif_occurrences(sequence, motif) == 3