import matplotlib.pyplot as plt
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
            f"Number of segments: {len(df)}\n"
        )

        ax.text(0.1, 0.9, summary_text, fontsize=12, va="top")
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