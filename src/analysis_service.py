from src.motif_analysis import (
    analyze_multiple_motifs,
    build_statistics_dataframe,
    calculate_at_content,
    calculate_average_motifs_per_segment,
    calculate_gc_content,
    calculate_motif_density_per_1000_nt,
    compare_sequences,
    count_unknown_bases,
    get_segment_with_max_motifs,
)


def run_sequence_analysis(sequence, motifs):
    return analyze_multiple_motifs(sequence, motifs)


def build_motif_statistics(sequence, motif, segment_length, mode="start"):
    return build_statistics_dataframe(
        sequence,
        motif,
        segment_length,
        mode=mode,
    )


def build_extended_sequence_statistics(sequence, motif, segment_length, mode="start"):
    max_segment = get_segment_with_max_motifs(
        sequence,
        motif,
        segment_length,
        mode=mode,
    )

    if max_segment is None:
        max_segment_text = "No segment data available"
    else:
        max_segment_text = (
            f"Segment {max_segment['segment_id']} "
            f"({max_segment['start']}-{max_segment['end']}), "
            f"count={max_segment['motif_count']}"
        )

    return {
        "gc_content": calculate_gc_content(sequence),
        "at_content": calculate_at_content(sequence),
        "unknown_bases": count_unknown_bases(sequence),
        "motif_density_per_1000_nt": calculate_motif_density_per_1000_nt(
            sequence,
            motif,
        ),
        "average_motifs_per_segment": calculate_average_motifs_per_segment(
            sequence,
            motif,
            segment_length,
            mode=mode,
        ),
        "max_segment_text": max_segment_text,
    }


def run_sequence_comparison(sequence_1, sequence_2, motifs):
    return compare_sequences(sequence_1, sequence_2, motifs)