from src.export_utils import (
    export_comparison_report_to_pdf,
    export_report_to_pdf,
    export_results_to_csv,
    export_session_to_json,
    plot_motif_distribution,
    plot_motif_positions,
)


def export_session_json(session_data, output_path):
    export_session_to_json(session_data, output_path)


def export_analysis_or_comparison_csv(statistics_df, comparison_df, output_path):
    if comparison_df is not None:
        export_results_to_csv(comparison_df, output_path)
    elif statistics_df is not None:
        export_results_to_csv(statistics_df, output_path)
    else:
        raise ValueError("No analysis results available for CSV export.")


def export_distribution_plot_png(statistics_df, selected_motif, output_path):
    if statistics_df is None:
        raise ValueError("No statistics available for plot export.")

    if not selected_motif:
        raise ValueError("No motif selected for plot export.")

    plot_motif_distribution(
        statistics_df,
        selected_motif,
        output_path=output_path,
        show_plot=False,
    )


def export_positions_plot_png(results, sequence_length, output_path):
    if not results:
        raise ValueError("No motif analysis results available for positions plot export.")

    if sequence_length <= 0:
        raise ValueError("Sequence length must be positive.")

    plot_motif_positions(
        results,
        sequence_length,
        output_path=output_path,
        show_plot=False,
    )


def export_analysis_or_comparison_pdf(
    comparison_df,
    analysis_results,
    statistics_df,
    selected_motif,
    analyzed_sequence_length,
    output_path,
):
    if comparison_df is not None:
        export_comparison_report_to_pdf(comparison_df, output_path)
        return

    if not analysis_results or statistics_df is None:
        raise ValueError("No analysis or comparison results available.")

    if not selected_motif:
        raise ValueError("No motif selected for PDF export.")

    export_report_to_pdf(
        statistics_df,
        selected_motif,
        analyzed_sequence_length,
        output_path,
    )