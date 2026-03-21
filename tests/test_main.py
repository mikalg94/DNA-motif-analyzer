import pytest

from main import main


def test_main_requires_file_and_motifs_for_cli(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["main.py", "--file", "data/example_sequence.fasta"]
    )

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 2