def find_motif_positions(sequence, motif):
    positions = []
    motif_length = len(motif)

    for i in range(len(sequence) - motif_length + 1):
        if sequence[i:i + motif_length] == motif:
            positions.append(i)

    return positions


def count_motif_occurrences(sequence, motif):
    positions = find_motif_positions(sequence, motif)
    return len(positions)