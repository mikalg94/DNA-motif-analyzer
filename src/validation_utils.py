import re


DNA_PATTERN = re.compile(r"^[ATCGN]+$", re.IGNORECASE)


def normalize_sequence(sequence: str) -> str:
    return "".join(sequence.split()).upper()


def validate_dna_sequence(sequence: str) -> None:
    if not sequence:
        raise ValueError("DNA sequence is empty.")

    if not DNA_PATTERN.fullmatch(sequence):
        raise ValueError("DNA sequence contains invalid characters. Allowed: A, T, C, G, N.")


def validate_motif(motif: str) -> None:
    if not motif:
        raise ValueError("Motif cannot be empty.")

    if not DNA_PATTERN.fullmatch(motif):
        raise ValueError("Motif contains invalid characters. Allowed: A, T, C, G, N.")


def validate_motifs_against_sequence(motifs: list[str], sequence: str) -> None:
    too_long_motifs = [motif for motif in motifs if len(motif) > len(sequence)]

    if too_long_motifs:
        joined = ", ".join(too_long_motifs)
        raise ValueError(
            f"Motif is longer than the loaded sequence: {joined}. "
            f"Please enter motifs shorter than or equal to sequence length."
        )


def get_sequence_warning(sequence: str) -> str | None:
    if not sequence:
        return None

    n_count = sequence.upper().count("N")
    n_ratio = n_count / len(sequence)

    if n_ratio >= 0.1:
        return (
            f"Warning: the sequence contains {n_count} unknown nucleotides ('N'), "
            f"which is {n_ratio:.1%} of the sequence length. "
            f"This may affect motif analysis results."
        )

    return None


def normalize_motifs(motifs: list[str]) -> list[str]:
    normalized = []
    seen = set()

    for motif in motifs:
        clean = motif.strip().upper()
        if clean and clean not in seen:
            validate_motif(clean)
            normalized.append(clean)
            seen.add(clean)

    return normalized