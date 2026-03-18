from src.io_utils import load_sequence_from_txt
from src.motif_analysis import build_statistics_dataframe


def main():
    sequence = load_sequence_from_txt("data/example_sequence.txt")
    motif = "ATG"

    df = build_statistics_dataframe(sequence, motif, segment_length=10)

    print(df)


if __name__ == "__main__":
    main()