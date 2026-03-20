import matplotlib.pyplot as plt
import plotly.express as px
import os
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages


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

    fig.update_layout(xaxis_title="Position in sequence", yaxis_title="Motif")
    fig.write_html(output_html)
    return output_html


def export_results_to_csv(df, output_path):
    df.to_csv(output_path, index=False)


def export_report_to_pdf(df, motif, sequence_length, output_path):
    with PdfPages(output_path) as pdf:
        fig, ax = plt.subplots(figsize=(8.27, 11.69))
        ax.axis("off")

        summary_text = (
            f"DNA Motif Analyzer Report\n\n"
            f"Motif: {motif}\n"
            f"Sequence length: {sequence_length}\n"
            f"Total motif count: {df['motif_count'].sum()}\n"
            f"Number of segments: {len(df)}\n\n"
            f"Segment statistics:\n"
        )

        segment_lines = []
        for _, row in df.iterrows():
            segment_lines.append(
                f"Segment {row['segment_id']}: "
                f"{row['start']}-{row['end']}, "
                f"count={row['motif_count']}, "
                f"positions={row['motif_positions']}"
            )

        full_text = summary_text + "\n".join(segment_lines[:25])

        ax.text(0.05, 0.95, full_text, fontsize=10, va="top")
        pdf.savefig(fig)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(df["segment_id"], df["motif_count"])
        ax.set_xlabel("Segment")
        ax.set_ylabel("Motif count")
        ax.set_title(f"Distribution of motif {motif}")
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

def save_analysis_history(entry, output_path="results/analysis_history.csv"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    new_row = pd.DataFrame([entry])

    if os.path.exists(output_path):
        existing_df = pd.read_csv(output_path)
        updated_df = pd.concat([existing_df, new_row], ignore_index=True)
    else:
        updated_df = new_row

    updated_df.to_csv(output_path, index=False)