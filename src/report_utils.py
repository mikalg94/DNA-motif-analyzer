from datetime import datetime


def format_analysis_results_for_sequence(
    sequence,
    sequence_label,
    motifs,
    segment_length,
    results,
    selected_motif,
    statistics_df,
    extended_stats,
    segment_mode,
):
    output = [
        f"{sequence_label.upper()} ANALYSIS RESULTS\n",
        f"Sequence length: {len(sequence)}",
        f"GC content: {extended_stats['gc_content']}%",
        f"AT content: {extended_stats['at_content']}%",
        f"Unknown bases (N): {extended_stats['unknown_bases']}",
        f"Recognized motifs: {', '.join(motifs)}",
        f"Segment length: {segment_length}",
        f"Segment assignment mode: {segment_mode}",
        f"Selected motif for detailed statistics: {selected_motif}",
        f"Motif density per 1000 nt: {extended_stats['motif_density_per_1000_nt']}",
        f"Average motifs per segment: {extended_stats['average_motifs_per_segment']}",
        f"Segment with highest count: {extended_stats['max_segment_text']}\n",
    ]

    for result in results:
        output.append(
            f"Motif: {result['motif']} | "
            f"Count: {result['count']} | "
            f"Positions: {result['positions']}"
        )

    output.append("\nSegment statistics for selected motif:\n")
    output.append(statistics_df.to_string(index=False))

    return "\n".join(output)


def format_comparison_results(sequence_1, sequence_2, motifs, comparison_df):
    output = [
        "COMPARISON RESULTS\n",
        f"Sequence 1 length: {len(sequence_1)}",
        f"Sequence 2 length: {len(sequence_2)}",
        f"Recognized motifs: {', '.join(motifs)}\n",
    ]

    if comparison_df.empty:
        output.append("No comparison data to display.")
    else:
        output.append(comparison_df.to_string(index=False))

    return "\n".join(output)


def build_session_data(
    sequence_1,
    sequence_2,
    file_path_1,
    file_path_2,
    last_analyzed_sequence_label,
    selected_motif,
    analysis_results,
    statistics_df,
    comparison_df,
):
    return {
        "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sequence_1_length": len(sequence_1) if sequence_1 else 0,
        "sequence_2_length": len(sequence_2) if sequence_2 else 0,
        "file_path_1": file_path_1,
        "file_path_2": file_path_2,
        "last_analyzed_sequence_label": last_analyzed_sequence_label,
        "selected_motif": selected_motif,
        "analysis_results": analysis_results,
        "statistics_dataframe": (
            statistics_df.to_dict(orient="records")
            if statistics_df is not None else []
        ),
        "comparison_results": (
            comparison_df.to_dict(orient="records")
            if comparison_df is not None else []
        ),
    }