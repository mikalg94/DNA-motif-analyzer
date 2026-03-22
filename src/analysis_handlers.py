from src.analysis_service import (
    build_motif_statistics,
    run_sequence_analysis,
    run_sequence_comparison,
)
from src.history_utils import (
    build_analysis_history_entry,
    build_comparison_history_entry,
)
from src.report_utils import (
    format_analysis_results_for_sequence,
    format_comparison_results,
)


def filter_and_sort_results(results, only_found=False, sort_mode="original", top_n_text=""):
    processed_results = results[:]

    if only_found:
        processed_results = [
            result for result in processed_results
            if result["count"] > 0
        ]

    if sort_mode == "count_desc":
        processed_results.sort(key=lambda item: item["count"], reverse=True)
    elif sort_mode == "count_asc":
        processed_results.sort(key=lambda item: item["count"])

    if top_n_text:
        try:
            top_n = int(top_n_text)
            if top_n > 0:
                processed_results = processed_results[:top_n]
        except ValueError:
            raise ValueError("Top N must be a positive integer.")

    return processed_results


def prepare_sequence_analysis(
    sequence,
    sequence_label,
    motifs,
    segment_length,
    mode,
    only_found=False,
    sort_mode="original",
    top_n_text="",
    extended_stats_builder=None,
):
    results = run_sequence_analysis(sequence, motifs)
    display_results = filter_and_sort_results(
        results,
        only_found=only_found,
        sort_mode=sort_mode,
        top_n_text=top_n_text,
    )

    selected_motif = motifs[0]
    statistics_df = build_motif_statistics(
        sequence,
        selected_motif,
        segment_length,
        mode=mode,
    )

    if extended_stats_builder is None:
        raise ValueError("extended_stats_builder is required.")

    extended_stats = extended_stats_builder(
        sequence,
        selected_motif,
        segment_length,
        mode,
    )

    final_text = format_analysis_results_for_sequence(
        sequence=sequence,
        sequence_label=sequence_label,
        motifs=motifs,
        segment_length=segment_length,
        results=display_results,
        selected_motif=selected_motif,
        statistics_df=statistics_df,
        extended_stats=extended_stats,
        segment_mode=mode,
    )

    history_entry = build_analysis_history_entry(
        sequence=sequence,
        sequence_label=sequence_label,
        motifs=motifs,
        segment_length=segment_length,
        results=results,
    )

    return {
        "results": results,
        "display_results": display_results,
        "selected_motif": selected_motif,
        "statistics_df": statistics_df,
        "final_text": final_text,
        "history_entry": history_entry,
    }


def prepare_sequence_comparison(
    sequence_1,
    sequence_2,
    motifs,
    only_found=False,
    sort_mode="original",
    top_n_text="",
):
    comparison_df = run_sequence_comparison(sequence_1, sequence_2, motifs)

    if only_found:
        comparison_df = comparison_df[
            (comparison_df["sequence_1_count"] > 0) |
            (comparison_df["sequence_2_count"] > 0)
        ]

    if sort_mode == "count_desc":
        comparison_df = comparison_df.sort_values(
            by=["sequence_1_count", "sequence_2_count"],
            ascending=False,
        )
    elif sort_mode == "count_asc":
        comparison_df = comparison_df.sort_values(
            by=["sequence_1_count", "sequence_2_count"],
            ascending=True,
        )

    if top_n_text:
        try:
            top_n = int(top_n_text)
            if top_n > 0:
                comparison_df = comparison_df.head(top_n)
        except ValueError:
            raise ValueError("Top N must be a positive integer.")

    final_text = format_comparison_results(
        sequence_1=sequence_1,
        sequence_2=sequence_2,
        motifs=motifs,
        comparison_df=comparison_df,
    )

    history_entry = build_comparison_history_entry(
        sequence_1=sequence_1,
        sequence_2=sequence_2,
        motifs=motifs,
        comparison_df=comparison_df,
    )

    return {
        "comparison_df": comparison_df,
        "final_text": final_text,
        "history_entry": history_entry,
    }