from dataclasses import dataclass


@dataclass
class SequenceSlot:
    sequence: str = ""
    file_path: str | None = None
    source_label: str = ""


def build_sequences_state():
    return {
        1: SequenceSlot(source_label="No first file selected"),
        2: SequenceSlot(source_label="No second file selected"),
    }