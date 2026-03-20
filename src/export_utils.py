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


def export_report_to_pdf(df, motif, output_path):
    with PdfPages(output_path) as pdf:
        plt.figure(figsize=(8, 5))
        plt.bar(df["segment_id"], df["motif_count"])
        plt.xlabel("Segment")
        plt.ylabel("Motif count")
        plt.title(f"Distribution of motif {motif}")
        plt.tight_layout()
        pdf.savefig()
        plt.close()