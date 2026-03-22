from dataclasses import dataclass, field


@dataclass
class SequenceSlot:
    sequence: str = ""
    file_path: str | None = None
    source_label: str = ""


@dataclass
class AnalysisState:
    last_results: list = field(default_factory=list)
    last_statistics_df: object | None = None
    last_selected_motif: str | None = None
    last_comparison_df: object | None = None
    last_analyzed_sequence: str = ""
    last_analyzed_sequence_label: str = ""


def build_sequences_state():
    return {
        1: SequenceSlot(source_label="No first file selected"),
        2: SequenceSlot(source_label="No second file selected"),
    }