from src.io_utils import load_sequence_from_txt, load_sequence_from_fasta


def main():
    txt_sequence = load_sequence_from_txt("data/example_sequence.txt")
    fasta_sequence = load_sequence_from_fasta("data/example_sequence.fasta")

    print("TXT length:", len(txt_sequence))
    print("FASTA length:", len(fasta_sequence))
    print("Sequences are equal:", txt_sequence == fasta_sequence)


if __name__ == "__main__":
    main()