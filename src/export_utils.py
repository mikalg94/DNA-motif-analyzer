import json
import os
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure


def export_session_to_json(session_data, output_path):
    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(session_data, json_file, indent=4, ensure_ascii=False)


def create_motif_distribution_figure(df, motif):
    fig = Figure(figsize=(8, 5))
    ax = fig.add_subplot(111)
    ax.bar(df["segment_id"], df["motif_count"])
    ax.set_xlabel("Segment")
    ax.set_ylabel("Motif count")
    ax.set_title(f"Distribution of motif {motif}")
    fig.tight_layout()
    return fig


def create_motif_positions_figure(results, sequence_length):
    fig = Figure(figsize=(10, 4))
    ax = fig.add_subplot(111)

    y_level = 1
    labels_added = set()

    for result in results:
        positions = result["positions"]
        motif = result["motif"]

        if positions:
            label = motif if motif not in labels_added else None
            ax.scatter(positions, [y_level] * len(positions), label=label)
            labels_added.add(motif)

        y_level += 1

    ax.set_xlim(0, sequence_length)
    ax.set_xlabel("Position in sequence")
    ax.set_ylabel("Motif index")
    ax.set_title("Motif positions on DNA sequence axis")

    if labels_added:
        ax.legend()

    fig.tight_layout()
    return fig


def create_multiple_motifs_summary_figure(results):
    motifs = [result["motif"] for result in results]
    counts = [result["count"] for result in results]

    fig = Figure(figsize=(8, 5))
    ax = fig.add_subplot(111)
    ax.bar(motifs, counts)
    ax.set_xlabel("Motif")
    ax.set_ylabel("Count")
    ax.set_title("Summary of motif occurrences")
    fig.tight_layout()
    return fig


def create_gc_content_figure(df):
    fig = Figure(figsize=(8, 5))
    ax = fig.add_subplot(111)

    ax.plot(df["segment_id"], df["gc_content"], marker="o")

    ax.set_xlabel("Segment")
    ax.set_ylabel("GC content (%)")
    ax.set_title("GC-content distribution across sequence")

    fig.tight_layout()
    return fig


def create_gc_comparison_figure(df1, df2):
    fig = Figure(figsize=(9, 5))
    ax = fig.add_subplot(111)

    ax.plot(df1["segment_id"], df1["gc_content"], marker="o", label="Sequence 1")
    ax.plot(df2["segment_id"], df2["gc_content"], marker="s", label="Sequence 2")

    ax.set_xlabel("Segment")
    ax.set_ylabel("GC content (%)")
    ax.set_title("GC-content comparison between sequences")

    ax.legend()
    fig.tight_layout()

    return fig


def create_gc_motif_overlay_figure(df, results, sequence_length):
    fig = Figure(figsize=(10, 5))
    ax = fig.add_subplot(111)

    if not df.empty:
        segment_centers = (df["start"] + df["end"]) / 2
        ax.plot(segment_centers, df["gc_content"], marker="o", label="GC content (%)")
        y_offset = max(df["gc_content"]) + 5
    else:
        y_offset = 5

    for result in results:
        motif = result["motif"]
        positions = result["positions"]

        if positions:
            ax.scatter(
                positions,
                [y_offset] * len(positions),
                label=f"{motif} positions",
                marker="x"
            )

    ax.set_xlim(0, sequence_length)
    ax.set_xlabel("Position in sequence")
    ax.set_ylabel("GC content (%)")
    ax.set_title("GC-content with motif positions overlay")

    if results:
        ax.legend()

    fig.tight_layout()
    return fig


def plot_motif_distribution(df, motif, output_path=None, show_plot=True):
    plt.figure(figsize=(8, 5))
    plt.bar(df["segment_id"], df["motif_count"])
    plt.xlabel("Segment")
    plt.ylabel("Motif count")
    plt.title(f"Distribution of motif {motif}")
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path)

    if show_plot:
        plt.show()
    else:
        plt.close()


def plot_motif_positions(results, sequence_length, output_path=None, show_plot=True):
    plt.figure(figsize=(10, 4))

    y_level = 1
    labels_added = set()

    for result in results:
        positions = result["positions"]
        motif = result["motif"]

        if positions:
            label = motif if motif not in labels_added else None
            plt.scatter(positions, [y_level] * len(positions), label=label)
            labels_added.add(motif)

        y_level += 1

    plt.xlim(0, sequence_length)
    plt.xlabel("Position in sequence")
    plt.ylabel("Motif index")
    plt.title("Motif positions on DNA sequence axis")

    if labels_added:
        plt.legend()

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path)

    if show_plot:
        plt.show()
    else:
        plt.close()


def plot_multiple_motifs_summary(results, output_path=None, show_plot=True):
    motifs = [result["motif"] for result in results]
    counts = [result["count"] for result in results]

    plt.figure(figsize=(8, 5))
    plt.bar(motifs, counts)
    plt.xlabel("Motif")
    plt.ylabel("Count")
    plt.title("Summary of motif occurrences")
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path)

    if show_plot:
        plt.show()
    else:
        plt.close()


def interactive_motif_positions(results, sequence_length, output_html="results/interactive_motif_positions.html"):
    rows = []

    for result in results:
        motif = result["motif"]
        for position in result["positions"]:
            rows.append({
                "motif": motif,
                "position": position,
                "sequence_length": sequence_length
            })

    if not rows:
        df = pd.DataFrame([{
            "motif": "No motifs found",
            "position": 0,
            "sequence_length": sequence_length
        }])
    else:
        df = pd.DataFrame(rows)

    fig = px.scatter(
        df,
        x="position",
        y="motif",
        hover_data=["position"],
        title="Interactive motif positions on sequence axis"
    )

    fig.update_layout(
        xaxis_title="Position in sequence",
        yaxis_title="Motif"
    )

    directory = os.path.dirname(output_html)
    if directory:
        os.makedirs(directory, exist_ok=True)

    fig.write_html(output_html)

    return output_html


def export_results_to_csv(df, output_path):
    df.to_csv(output_path, index=False)


def export_report_to_pdf(df, motif, sequence_length, output_path):
    total_motif_count = int(df["motif_count"].sum())
    number_of_segments = len(df)
    average_per_segment = round(total_motif_count / number_of_segments, 3) if number_of_segments else 0

    if not df.empty:
        max_count_row = df.loc[df["motif_count"].idxmax()]
        max_segment_text = (
            f"Segment {int(max_count_row['segment_id'])} "
            f"({int(max_count_row['start'])}-{int(max_count_row['end'])}) "
            f"- count: {int(max_count_row['motif_count'])}"
        )
    else:
        max_segment_text = "No segment data available."

    with PdfPages(output_path) as pdf:
        fig, ax = plt.subplots(figsize=(8.27, 11.69))
        ax.axis("off")

        summary_lines = [
            "DNA Motif Analyzer Report",
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Motif: {motif}",
            f"Sequence length: {sequence_length}",
            f"Total motif count: {total_motif_count}",
            f"Number of segments: {number_of_segments}",
            f"Average motif count per segment: {average_per_segment}",
            f"Segment with highest count: {max_segment_text}",
            "",
            "Report contents:",
            "- Summary page",
            "- Motif distribution chart",
            "- Segment statistics table",
        ]

        ax.text(
            0.05,
            0.95,
            "\n".join(summary_lines),
            fontsize=11,
            va="top"
        )
        pdf.savefig(fig)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(df["segment_id"], df["motif_count"])
        ax.set_xlabel("Segment")
        ax.set_ylabel("Motif count")
        ax.set_title(f"Distribution of motif {motif}")
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(11.69, 8.27))
        ax.axis("off")

        table_df = df.copy()
        table_df["motif_positions"] = table_df["motif_positions"].astype(str)

        table_df["motif_positions"] = table_df["motif_positions"].apply(
            lambda x: x if len(x) <= 25 else x[:22] + "..."
        )

        table = ax.table(
            cellText=table_df.values,
            colLabels=table_df.columns,
            loc="center"
        )

        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.4)

        ax.set_title("Segment statistics", pad=20)
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)


def save_analysis_history(entry, output_path="results/analysis_history.csv"):
    directory = os.path.dirname(output_path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    new_row = pd.DataFrame([entry])

    if os.path.exists(output_path):
        existing_df = pd.read_csv(output_path)
        updated_df = pd.concat([existing_df, new_row], ignore_index=True)
    else:
        updated_df = new_row

    updated_df.to_csv(output_path, index=False)