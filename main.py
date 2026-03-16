from src.io_utils import load_sequence_from_txt


def main():
    sequence = load_sequence_from_txt("data/example_sequence.txt")
    print("Sequence length:", len(sequence))


if __name__ == "__main__":
    main()