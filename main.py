from src.io_utils import load_sequence_from_txt
from src.motif_analysis import count_motif_in_segments


def main():
    sequence = load_sequence_from_txt("data/example_sequence.txt")
    motif = "ATG"

    counts = count_motif_in_segments(sequence, motif, segment_length=10)

    print("Motif:", motif)
    print("Counts in segments:", counts)


if __name__ == "__main__":
    main()