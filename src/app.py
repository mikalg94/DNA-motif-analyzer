import tkinter as tk
from tkinter import filedialog, messagebox

from src.io_utils import load_sequence_from_txt, load_sequence_from_fasta
from src.motif_analysis import analyze_multiple_motifs, build_statistics_dataframe
from src.ncbi_utils import fetch_sequence_from_ncbi
from src.validation_utils import normalize_motifs


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("DNA Motif Analyzer")
        self.root.geometry("800x600")

        self.file_path = None
        self.sequence = ""
        self.last_results = []
        self.last_statistics_df = None
        self.last_selected_motif = None

        self.title_label = tk.Label(root, text="DNA Motif Analyzer", font=("Arial", 16))
        self.title_label.pack(pady=10)

        self.file_button = tk.Button(root, text="Choose sequence file", command=self.choose_file)
        self.file_button.pack(pady=5)

        self.file_label = tk.Label(root, text="No file selected")
        self.file_label.pack(pady=5)

        self.ncbi_label = tk.Label(root, text="NCBI accession ID:")
        self.ncbi_label.pack(pady=5)

        self.ncbi_entry = tk.Entry(root, width=30)
        self.ncbi_entry.pack(pady=5)

        self.email_label = tk.Label(root, text="Email for NCBI:")
        self.email_label.pack(pady=5)

        self.email_entry = tk.Entry(root, width=30)
        self.email_entry.pack(pady=5)

        self.fetch_button = tk.Button(root, text="Fetch from NCBI", command=self.fetch_from_ncbi)
        self.fetch_button.pack(pady=5)

        self.motif_label = tk.Label(root, text="Enter motifs separated by commas:")
        self.motif_label.pack(pady=5)

        self.motif_entry = tk.Entry(root, width=40)
        self.motif_entry.pack(pady=5)

        self.segment_label = tk.Label(root, text="Segment length:")
        self.segment_label.pack(pady=5)

        self.segment_entry = tk.Entry(root, width=10)
        self.segment_entry.insert(0, "10")
        self.segment_entry.pack(pady=5)

        self.analyze_button = tk.Button(root, text="Analyze", command=self.run_analysis)
        self.analyze_button.pack(pady=10)

        self.result_text = tk.Text(root, height=20, width=95)
        self.result_text.pack(pady=10)

    def choose_file(self):
        self.file_path = filedialog.askopenfilename(
            filetypes=[("Sequence files", "*.txt *.fasta *.fa"), ("All files", "*.*")]
        )

        if self.file_path:
            self.file_label.config(text=self.file_path)

            try:
                if self.file_path.endswith(".txt"):
                    self.sequence = load_sequence_from_txt(self.file_path)
                else:
                    self.sequence = load_sequence_from_fasta(self.file_path)

                messagebox.showinfo("Success", "Sequence loaded successfully.")
            except Exception as e:
                self.sequence = ""
                messagebox.showerror("Error", f"Failed to load sequence: {e}")

    def fetch_from_ncbi(self):
        accession_id = self.ncbi_entry.get().strip()
        email = self.email_entry.get().strip()

        if not accession_id or not email:
            messagebox.showerror("Error", "Please enter accession ID and email.")
            return

        try:
            self.sequence = fetch_sequence_from_ncbi(accession_id, email)
            self.file_label.config(text=f"Loaded from NCBI: {accession_id}")
            messagebox.showinfo("Success", "Sequence downloaded from NCBI.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download sequence: {e}")

    def run_analysis(self):
        if not self.sequence:
            messagebox.showerror("Error", "Please load a sequence from file or NCBI.")
            return

        motifs_text = self.motif_entry.get().strip()

        if not motifs_text:
            messagebox.showerror("Error", "Please enter at least one motif.")
            return

        try:
            motifs = normalize_motifs(motifs_text.split(","))
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        try:
            segment_length = int(self.segment_entry.get().strip())
            if segment_length <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Segment length must be a positive integer.")
            return

        results = analyze_multiple_motifs(self.sequence, motifs)

        self.last_results = results
        self.last_selected_motif = motifs[0]
        self.last_statistics_df = build_statistics_dataframe(self.sequence, motifs[0], segment_length)

        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, f"Sequence length: {len(self.sequence)}\n")
        self.result_text.insert(tk.END, f"Segment length: {segment_length}\n\n")

        for result in results:
            line = f"Motif: {result['motif']} | Count: {result['count']} | Positions: {result['positions']}\n"
            self.result_text.insert(tk.END, line)

        self.result_text.insert(tk.END, "\nSegment statistics for first motif:\n")
        self.result_text.insert(tk.END, self.last_statistics_df.to_string(index=False))
        self.result_text.insert(tk.END, "\n")