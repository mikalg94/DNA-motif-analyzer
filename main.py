from src.io_utils import load_sequence_from_txt
from src.motif_analysis import find_motif_positions, count_motif_occurrences


def main():
    sequence = load_sequence_from_txt("data/example_sequence.txt")
    motif = "ATG"

    positions = find_motif_positions(sequence, motif)
    count = count_motif_occurrences(sequence, motif)

    print("Motif:", motif)
    print("Positions:", positions)
    print("Occurrences:", count)


if __name__ == "__main__":
    main()