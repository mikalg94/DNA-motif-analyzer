from src.io_utils import load_sequence_from_txt
from src.motif_analysis import build_statistics_dataframe
from src.export_utils import plot_motif_distribution, export_results_to_csv


def main():
    sequence = load_sequence_from_txt("data/example_sequence.txt")
    motif = "ATG"

    df = build_statistics_dataframe(sequence, motif, segment_length=10)
    print(df)

    export_results_to_csv(df, "results/motif_statistics.csv")
    plot_motif_distribution(df, motif, output_path="results/motif_plot.png")


if __name__ == "__main__":
    main()