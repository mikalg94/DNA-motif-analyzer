import tkinter as tk
from tkinter import filedialog, messagebox

from src.io_utils import load_sequence_from_txt, load_sequence_from_fasta
from src.motif_analysis import analyze_multiple_motifs


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("DNA Motif Analyzer")
        self.root.geometry("600x400")

        self.file_path = None

        self.title_label = tk.Label(root, text="DNA Motif Analyzer", font=("Arial", 16))
        self.title_label.pack(pady=10)

        self.file_button = tk.Button(root, text="Choose sequence file", command=self.choose_file)
        self.file_button.pack(pady=5)

        self.file_label = tk.Label(root, text="No file selected")
        self.file_label.pack(pady=5)

        self.motif_label = tk.Label(root, text="Enter motifs separated by commas:")
        self.motif_label.pack(pady=5)

        self.motif_entry = tk.Entry(root, width=40)
        self.motif_entry.pack(pady=5)

        self.analyze_button = tk.Button(root, text="Analyze", command=self.run_analysis)
        self.analyze_button.pack(pady=10)

        self.result_text = tk.Text(root, height=12, width=70)
        self.result_text.pack(pady=10)

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

        motifs_text = self.motif_entry.get().strip()

        if not motifs_text:
            messagebox.showerror("Error", "Please enter at least one motif.")
            return

        motifs = motifs_text.split(",")

        if self.file_path.endswith(".txt"):
            sequence = load_sequence_from_txt(self.file_path)
        else:
            sequence = load_sequence_from_fasta(self.file_path)

        results = analyze_multiple_motifs(sequence, motifs)

        self.result_text.delete("1.0", tk.END)

        for result in results:
            line = f"Motif: {result['motif']} | Count: {result['count']} | Positions: {result['positions']}\n"
            self.result_text.insert(tk.END, line)