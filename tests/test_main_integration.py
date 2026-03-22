import os
import tempfile
from argparse import Namespace

from main import run_cli


def test_run_cli_outputs_analysis(capsys):
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as temp_file:
        temp_file.write("ATGCGTATGCGTTATA")
        path = temp_file.name

    try:
        args = Namespace(
            file=path,
            motifs="ATG,TATA",
            segment=5,
            mode="start"
        )

        run_cli(args)
        captured = capsys.readouterr()

        assert "DNA MOTIF ANALYZER (CLI)" in captured.out
        assert "Sequence length:" in captured.out
        assert "Motif: ATG" in captured.out
        assert "Motif: TATA" in captured.out
        assert "Segment statistics for motif ATG" in captured.out
        assert "=== DONE ===" in captured.out
    finally:
        if os.path.exists(path):
            os.remove(path)