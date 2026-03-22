import os
import tempfile

import pandas as pd

from src.export_utils import (
    export_comparison_report_to_pdf,
    export_report_to_pdf,
    export_results_to_csv,
    interactive_motif_positions,
    plot_motif_positions,
    save_analysis_history,
)


def sample_statistics_df():
    return pd.DataFrame(
        [
            {
                "segment_id": 1,
                "start": 0,
                "end": 9,
                "segment_length": 10,
                "motif_count": 2,
                "motif_positions": "0, 6",
            },
            {
                "segment_id": 2,
                "start": 10,
                "end": 19,
                "segment_length": 10,
                "motif_count": 1,
                "motif_positions": "12",
            },
        ]
    )


def test_export_results_to_csv():
    df = sample_statistics_df()

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_file:
        output_path = temp_file.name

    try:
        export_results_to_csv(df, output_path)
        loaded_df = pd.read_csv(output_path)

        assert not loaded_df.empty
        assert list(loaded_df.columns) == list(df.columns)
        assert len(loaded_df) == 2
    finally:
        if os.path.exists(output_path):
            os.remove(output_path)


def test_save_analysis_history():
    entry = {
        "timestamp": "2026-03-21 12:00:00",
        "operation": "analysis",
        "sequence_1_length": 50,
        "sequence_2_length": "",
        "motifs": "ATG, TATA",
        "segment_length": 10,
        "details": "ATG=3; TATA=1",
    }

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_file:
        output_path = temp_file.name

    try:
        os.remove(output_path)  # chcemy sprawdzić tworzenie pliku od zera
        save_analysis_history(entry, output_path=output_path)

        history_df = pd.read_csv(output_path)
        assert len(history_df) == 1
        assert history_df.loc[0, "operation"] == "analysis"
        assert history_df.loc[0, "motifs"] == "ATG, TATA"
    finally:
        if os.path.exists(output_path):
            os.remove(output_path)


def test_interactive_motif_positions_creates_html():
    results = [
        {"motif": "ATG", "count": 2, "positions": [0, 6]},
        {"motif": "TATA", "count": 1, "positions": [15]},
    ]

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as temp_file:
        output_path = temp_file.name

    try:
        returned_path = interactive_motif_positions(
            results,
            sequence_length=30,
            output_html=output_path,
        )

        assert returned_path == output_path
        assert os.path.exists(output_path)

        with open(output_path, "r", encoding="utf-8") as file:
            content = file.read()

        assert "Interactive motif positions on sequence axis" in content
        assert "ATG" in content
        assert "TATA" in content
    finally:
        if os.path.exists(output_path):
            os.remove(output_path)


def test_export_report_to_pdf_creates_file():
    df = sample_statistics_df()

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        output_path = temp_file.name

    try:
        export_report_to_pdf(
            df=df,
            motif="ATG",
            sequence_length=20,
            output_path=output_path,
        )

        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0
    finally:
        if os.path.exists(output_path):
            os.remove(output_path)

def test_export_comparison_report_to_pdf_creates_file():
    df = pd.DataFrame(
        [
            {
                "motif": "ATG",
                "sequence_1_length": 50,
                "sequence_2_length": 60,
                "sequence_1_count": 3,
                "sequence_2_count": 5,
                "sequence_1_per_1000_nt": 60.0,
                "sequence_2_per_1000_nt": 83.333,
                "count_difference": -2,
            },
            {
                "motif": "TATA",
                "sequence_1_length": 50,
                "sequence_2_length": 60,
                "sequence_1_count": 1,
                "sequence_2_count": 2,
                "sequence_1_per_1000_nt": 20.0,
                "sequence_2_per_1000_nt": 33.333,
                "count_difference": -1,
            },
        ]
    )

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        output_path = temp_file.name

    try:
        export_comparison_report_to_pdf(df, output_path)
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0
    finally:
        if os.path.exists(output_path):
            os.remove(output_path)

def test_plot_motif_positions_saves_png():
    results = [
        {"motif": "ATG", "count": 2, "positions": [0, 6]},
        {"motif": "TATA", "count": 1, "positions": [15]},
    ]

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
        output_path = temp_file.name

    try:
        plot_motif_positions(
            results,
            sequence_length=30,
            output_path=output_path,
            show_plot=False
        )

        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0
    finally:
        if os.path.exists(output_path):
            os.remove(output_path)