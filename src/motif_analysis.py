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
    positions = find_motif_positions(sequence, motif)
    segment_count = (len(sequence) + segment_length - 1) // segment_length
    counts = [0] * segment_count

    for position in positions:
        segment_index = position // segment_length
        counts[segment_index] += 1

    return counts


def build_statistics_dataframe(sequence, motif, segment_length=10):
    segments = segment_sequence(sequence, segment_length)
    motif_positions = find_motif_positions(sequence, motif)
    motif_counts = count_motif_in_segments(sequence, motif, segment_length)
    gc_values = calculate_gc_content_per_segment(sequence, segment_length)

    data = []

    for i, segment in enumerate(segments):
        start = i * segment_length
        end = start + len(segment) - 1

        segment_positions = [
            pos for pos in motif_positions
            if start <= pos <= end
        ]

        data.append({
            "segment_id": i + 1,
            "start": start,
            "end": end,
            "segment_length": len(segment),
            "motif_count": motif_counts[i],
            "motif_positions": ", ".join(map(str, segment_positions)) if segment_positions else "",
            "gc_content": gc_values[i],
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

    len1 = len(sequence1)
    len2 = len(sequence2)

    for motif in motifs:
        motif = motif.strip().upper()
        if motif:
            count1 = count_motif_occurrences(sequence1, motif)
            count2 = count_motif_occurrences(sequence2, motif)

            freq1 = round((count1 / len1) * 1000, 3) if len1 else 0
            freq2 = round((count2 / len2) * 1000, 3) if len2 else 0

            comparison_data.append({
                "motif": motif,
                "sequence_1_length": len1,
                "sequence_2_length": len2,
                "sequence_1_count": count1,
                "sequence_2_count": count2,
                "sequence_1_per_1000_nt": freq1,
                "sequence_2_per_1000_nt": freq2,
                "count_difference": count1 - count2
            })

    return pd.DataFrame(comparison_data)

def calculate_gc_content(sequence):
    if not sequence:
        return 0.0

    sequence = sequence.upper()
    gc_count = sequence.count("G") + sequence.count("C")

    return round((gc_count / len(sequence)) * 100, 3)


def calculate_gc_content_per_segment(sequence, segment_length=10):
    segments = segment_sequence(sequence, segment_length)
    gc_values = []

    for segment in segments:
        if not segment:
            gc_values.append(0.0)
            continue

        gc_count = segment.count("G") + segment.count("C")
        gc_percent = (gc_count / len(segment)) * 100
        gc_values.append(round(gc_percent, 3))

    return gc_values