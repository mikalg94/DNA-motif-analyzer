def load_sequence_from_txt(path):
    with open(path, "r") as file:
        sequence = file.read()

    sequence = sequence.replace("\n", "")
    sequence = sequence.replace(" ", "")
    sequence = sequence.upper()

    return sequence


def load_sequence_from_fasta(path):
    sequence = ""

    with open(path, "r") as file:
        for line in file:
            if line.startswith(">"):
                continue
            sequence += line.strip()

    return sequence.upper()