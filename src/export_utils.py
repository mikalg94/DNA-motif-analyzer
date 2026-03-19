import matplotlib.pyplot as plt


def plot_motif_distribution(df, motif, output_path=None):
    plt.figure(figsize=(8, 5))
    plt.bar(df["segment_id"], df["motif_count"])
    plt.xlabel("Segment")
    plt.ylabel("Motif count")
    plt.title(f"Distribution of motif {motif}")
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path)

    plt.show()


def export_results_to_csv(df, output_path):
    df.to_csv(output_path, index=False)