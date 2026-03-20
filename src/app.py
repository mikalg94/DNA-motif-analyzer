import tkinter as tk
from tkinter import filedialog, messagebox

from src.io_utils import load_sequence_from_txt, load_sequence_from_fasta
from src.motif_analysis import count_motif_occurrences


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("DNA Motif Analyzer")
        self.root.geometry("500x300")

        self.file_path = None

        self.title_label = tk.Label(root, text="DNA Motif Analyzer", font=("Arial", 16))
        self.title_label.pack(pady=10)

        self.file_button = tk.Button(root, text="Choose sequence file", command=self.choose_file)
        self.file_button.pack(pady=5)

        self.file_label = tk.Label(root, text="No file selected")
        self.file_label.pack(pady=5)

        self.motif_label = tk.Label(root, text="Enter motif:")
        self.motif_label.pack(pady=5)

        self.motif_entry = tk.Entry(root, width=30)
        self.motif_entry.pack(pady=5)

        self.analyze_button = tk.Button(root, text="Analyze", command=self.run_analysis)
        self.analyze_button.pack(pady=10)

        self.result_label = tk.Label(root, text="")
        self.result_label.pack(pady=10)

    def choose_file(self):
        self.file_path = filedialog.askopenfilename(
            filetypes=[("Sequence files", "*.txt *.fasta *.fa"), ("All files", "*.*")]
        )

        if self.file_path:
            self.file_label.config(text=self.file_path)

    def run_analysis(self):
        if not self.file_path:
            messagebox.showerror("Error", "Please select a file.")
            return

        motif = self.motif_entry.get().strip().upper()

        if not motif:
            messagebox.showerror("Error", "Please enter a motif.")
            return

        if self.file_path.endswith(".txt"):
            sequence = load_sequence_from_txt(self.file_path)
        else:
            sequence = load_sequence_from_fasta(self.file_path)

        count = count_motif_occurrences(sequence, motif)
        self.result_label.config(text=f"Motif {motif} occurs {count} times.")