import pandas as pd


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


def build_statistics_dataframe(sequence, motif, segment_length=10):
    segments = segment_sequence(sequence, segment_length)
    data = []

    for i, segment in enumerate(segments):
        count = count_motif_occurrences(segment, motif)
        start = i * segment_length
        end = start + len(segment) - 1

        data.append({
            "segment_id": i + 1,
            "start": start,
            "end": end,
            "motif_count": count
        })

    df = pd.DataFrame(data)
    return df


def analyze_multiple_motifs(sequence, motifs):
    results = []

    for motif in motifs:
        motif = motif.strip().upper()
        if motif:
            count = count_motif_occurrences(sequence, motif)
            positions = find_motif_positions(sequence, motif)

            results.append({
                "motif": motif,
                "count": count,
                "positions": positions
            })

    return results


def compare_sequences(sequence1, sequence2, motifs):
    comparison_data = []

    for motif in motifs:
        motif = motif.strip().upper()
        if motif:
            count1 = count_motif_occurrences(sequence1, motif)
            count2 = count_motif_occurrences(sequence2, motif)

            comparison_data.append({
                "motif": motif,
                "sequence_1_count": count1,
                "sequence_2_count": count2
            })

    return pd.DataFrame(comparison_data)