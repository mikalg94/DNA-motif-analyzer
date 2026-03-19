from src.io_utils import load_sequence_from_txt
from src.motif_analysis import build_statistics_dataframe
from src.export_utils import plot_motif_distribution


def main():
    sequence = load_sequence_from_txt("data/example_sequence.txt")
    motif = "ATG"

    df = build_statistics_dataframe(sequence, motif, segment_length=10)
    print(df)

    plot_motif_distribution(df, motif)


if __name__ == "__main__":
    main()