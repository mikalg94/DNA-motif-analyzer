import argparse
import sys
import tkinter as tk

from src.app_controller import AppController
from src.io_utils import load_sequence_from_fasta, load_sequence_from_txt
from src.motif_analysis import analyze_multiple_motifs, build_statistics_dataframe
from src.validation_utils import normalize_motifs


def load_sequence(path):
    path_lower = path.lower()

    if path_lower.endswith(".txt"):
        return load_sequence_from_txt(path)
    if path_lower.endswith(".fasta") or path_lower.endswith(".fa"):
        return load_sequence_from_fasta(path)

    raise ValueError("Unsupported file format. Use TXT, FASTA, or FA.")


def run_cli(args):
    try:
        sequence = load_sequence(args.file)

        motifs = normalize_motifs(args.motifs.split(","))
        if not motifs:
            raise ValueError("Please provide at least one valid motif.")

        segment_length = args.segment
        if segment_length <= 0:
            raise ValueError("Segment length must be a positive integer.")

        mode = args.mode

        results = analyze_multiple_motifs(sequence, motifs)

        print("\n=== DNA MOTIF ANALYZER (CLI) ===")
        print(f"Sequence length: {len(sequence)}")
        print(f"Motifs: {', '.join(motifs)}")
        print(f"Segment length: {segment_length}")
        print(f"Segment assignment mode: {mode}\n")

        for result in results:
            print(
                f"Motif: {result['motif']} | "
                f"Count: {result['count']} | "
                f"Positions: {result['positions']}"
            )

        selected_motif = motifs[0]
        df = build_statistics_dataframe(
            sequence,
            selected_motif,
            segment_length,
            mode=mode
        )

        print(f"\n--- Segment statistics for motif {selected_motif} ---")
        print(df.to_string(index=False))
        print("\n=== DONE ===\n")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="DNA Motif Analyzer")

    parser.add_argument("--file", type=str, help="Path to sequence file (TXT/FASTA)")
    parser.add_argument("--motifs", type=str, help="Motifs separated by commas")
    parser.add_argument("--segment", type=int, default=10, help="Segment length")
    parser.add_argument(
        "--mode",
        type=str,
        default="start",
        choices=["start", "full"],
        help="Segment assignment mode: start or full"
    )

    args = parser.parse_args()

    cli_requested = args.file is not None or args.motifs is not None

    if cli_requested:
        if not args.file or not args.motifs:
            parser.error("For CLI mode, both --file and --motifs are required.")
        run_cli(args)
        return

    root = tk.Tk()
    app = AppController(root)
    root.mainloop()


if __name__ == "__main__":
    main()