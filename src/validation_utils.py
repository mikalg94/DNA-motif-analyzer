import re


DNA_PATTERN = re.compile(r"^[ATCGN]+$", re.IGNORECASE)


def normalize_sequence(sequence: str) -> str:
    return sequence.replace("\n", "").replace(" ", "").strip().upper()


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