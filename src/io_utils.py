from src.validation_utils import normalize_sequence, validate_dna_sequence


def load_sequence_from_txt(path):
    with open(path, "r", encoding="utf-8") as file:
        sequence = file.read()

    sequence = normalize_sequence(sequence)
    validate_dna_sequence(sequence)

    return sequence


def load_sequence_from_fasta(path):
    sequence = ""

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            if line.startswith(">"):
                continue
            sequence += line.strip()

    sequence = normalize_sequence(sequence)
    validate_dna_sequence(sequence)

    return sequence