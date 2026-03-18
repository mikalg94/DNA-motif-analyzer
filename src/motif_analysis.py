def find_motif_positions(sequence, motif):
    positions = []
    sequence = sequence.upper()
    motif = motif.upper()
    motif_length = len(motif)

    for i in range(len(sequence) - motif_length + 1):
        if sequence[i:i + motif_length] == motif:
            positions.append(i)

    return positions


def count_motif_occurrences(sequence, motif):
    positions = find_motif_positions(sequence, motif)
    return len(positions)


def segment_sequence(sequence, segment_length=10):
    segments = []

    for i in range(0, len(sequence), segment_length):
        segment = sequence[i:i + segment_length]
        segments.append(segment)

    return segments


def count_motif_in_segments(sequence, motif, segment_length=10):
    segments = segment_sequence(sequence, segment_length)
    counts = []

    for segment in segments:
        count = count_motif_occurrences(segment, motif)
        counts.append(count)

    return counts