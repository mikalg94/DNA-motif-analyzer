import re

import numpy as np
import pandas as pd

IUPAC_MAP = {
    "A": "A",
    "T": "T",
    "C": "C",
    "G": "G",
    "R": "[AG]",
    "Y": "[CT]",
    "S": "[GC]",
    "W": "[AT]",
    "K": "[GT]",
    "M": "[AC]",
    "B": "[CGT]",
    "D": "[AGT]",
    "H": "[ACT]",
    "V": "[ACG]",
    "N": "[ATCGN]",
}


def motif_to_regex(motif):
    motif = motif.upper()
    return "".join(IUPAC_MAP.get(char, re.escape(char)) for char in motif)


def find_motif_positions(sequence, motif):
    positions = []
    sequence = sequence.upper()
    motif = motif.upper()

    pattern = motif_to_regex(motif)

    for i in range(len(sequence) - len(motif) + 1):
        fragment = sequence[i:i + len(motif)]
        if re.fullmatch(pattern, fragment):
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


def count_motif_in_segments(sequence, motif, segment_length=10, mode="start"):
    positions = find_motif_positions(sequence, motif)
    segment_count = (len(sequence) + segment_length - 1) // segment_length
    counts = [0] * segment_count
    motif_len = len(motif)

    for position in positions:
        segment_index = position // segment_length
        segment_start = segment_index * segment_length
        segment_end = min(segment_start + segment_length - 1, len(sequence) - 1)

        if mode == "start":
            counts[segment_index] += 1
        elif mode == "full":
            if position + motif_len - 1 <= segment_end:
                counts[segment_index] += 1
        else:
            raise ValueError("Mode must be 'start' or 'full'.")

    return counts


def calculate_gc_content(sequence):
    if not sequence:
        return 0.0

    sequence_array = np.array(list(sequence.upper()))
    gc_count = np.sum((sequence_array == "G") | (sequence_array == "C"))

    return round(float((gc_count / len(sequence_array)) * 100), 3)


def calculate_gc_content_per_segment(sequence, segment_length=10):
    segments = segment_sequence(sequence, segment_length)

    if not segments:
        return []

    gc_values = []
    for segment in segments:
        segment_array = np.array(list(segment.upper()))

        if segment_array.size == 0:
            gc_values.append(0.0)
            continue

        gc_count = np.sum((segment_array == "G") | (segment_array == "C"))
        gc_percent = (gc_count / segment_array.size) * 100
        gc_values.append(round(float(gc_percent), 3))

    return gc_values


def build_statistics_dataframe(sequence, motif, segment_length=10, mode="start"):
    segments = segment_sequence(sequence, segment_length)
    motif_positions = find_motif_positions(sequence, motif)
    motif_counts = count_motif_in_segments(
        sequence,
        motif,
        segment_length,
        mode=mode
    )
    gc_values = calculate_gc_content_per_segment(sequence, segment_length)

    data = []
    motif_len = len(motif)

    for i, segment in enumerate(segments):
        start = i * segment_length
        end = start + len(segment) - 1

        if mode == "start":
            segment_positions = [
                pos for pos in motif_positions
                if start <= pos <= end
            ]
        elif mode == "full":
            segment_positions = [
                pos for pos in motif_positions
                if start <= pos and (pos + motif_len - 1) <= end
            ]
        else:
            raise ValueError("Mode must be 'start' or 'full'.")

        data.append({
            "segment_id": i + 1,
            "start": start,
            "end": end,
            "segment_length": len(segment),
            "motif_count": motif_counts[i],
            "motif_positions": ", ".join(map(str, segment_positions)) if segment_positions else "",
            "gc_content": gc_values[i],
        })

    return pd.DataFrame(data)


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


def calculate_at_content(sequence):
    if not sequence:
        return 0.0

    sequence_array = np.array(list(sequence.upper()))
    at_count = np.sum((sequence_array == "A") | (sequence_array == "T"))

    return round(float((at_count / len(sequence_array)) * 100), 3)


def count_unknown_bases(sequence):
    sequence_array = np.array(list(sequence.upper()))
    return int(np.sum(sequence_array == "N"))


def calculate_motif_density_per_1000_nt(sequence, motif):
    sequence_length = len(sequence)
    if sequence_length == 0:
        return 0.0

    count = count_motif_occurrences(sequence, motif)
    return round((count / sequence_length) * 1000, 3)


def calculate_average_motifs_per_segment(sequence, motif, segment_length=10, mode="start"):
    counts = np.array(
        count_motif_in_segments(sequence, motif, segment_length, mode=mode),
        dtype=float
    )

    if counts.size == 0:
        return 0.0

    return round(float(np.mean(counts)), 3)


def calculate_segment_motif_statistics(sequence, motif, segment_length=10, mode="start"):
    counts = np.array(
        count_motif_in_segments(sequence, motif, segment_length, mode=mode),
        dtype=float
    )

    if counts.size == 0:
        return {
            "mean": 0.0,
            "std": 0.0,
            "max": 0,
            "min": 0,
        }

    return {
        "mean": round(float(np.mean(counts)), 3),
        "std": round(float(np.std(counts)), 3),
        "max": int(np.max(counts)),
        "min": int(np.min(counts)),
    }


def get_segment_with_max_motifs(sequence, motif, segment_length=10, mode="start"):
    df = build_statistics_dataframe(sequence, motif, segment_length, mode=mode)

    if df.empty:
        return None

    max_row = df.loc[df["motif_count"].idxmax()]
    return {
        "segment_id": int(max_row["segment_id"]),
        "start": int(max_row["start"]),
        "end": int(max_row["end"]),
        "motif_count": int(max_row["motif_count"]),
    }