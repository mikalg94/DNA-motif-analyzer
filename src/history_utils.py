from datetime import datetime


def build_analysis_history_entry(sequence, sequence_label, motifs, segment_length, results):
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "operation": f"analysis_{sequence_label.lower().replace(' ', '_')}",
        "sequence_1_length": len(sequence),
        "sequence_2_length": "",
        "motifs": ", ".join(motifs),
        "segment_length": segment_length,
        "details": "; ".join(
            [f"{result['motif']}={result['count']}" for result in results]
        ),
    }


def build_comparison_history_entry(sequence_1, sequence_2, motifs, comparison_df):
    comparison_details = []

    for _, row in comparison_df.iterrows():
        comparison_details.append(
            f"{row['motif']}: seq1={row['sequence_1_count']}, "
            f"seq2={row['sequence_2_count']}"
        )

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "operation": "comparison",
        "sequence_1_length": len(sequence_1),
        "sequence_2_length": len(sequence_2),
        "motifs": ", ".join(motifs),
        "segment_length": "",
        "details": "; ".join(comparison_details),
    }