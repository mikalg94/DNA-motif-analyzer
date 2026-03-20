import os
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from src.export_utils import (
    export_report_to_pdf,
    export_results_to_csv,
    interactive_motif_positions,
    plot_motif_distribution,
    plot_motif_positions,
)

from src.io_utils import load_sequence_from_fasta, load_sequence_from_txt
from src.motif_analysis import (
    analyze_multiple_motifs,
    build_statistics_dataframe,
    compare_sequences,
)
from src.ncbi_utils import fetch_sequence_from_ncbi
from src.validation_utils import normalize_motifs


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("DNA Motif Analyzer")
        self.root.geometry("900x760")

        self.file_path = None
        self.file_path_2 = None
        self.sequence = ""
        self.sequence_2 = ""

        self.last_results = []
        self.last_statistics_df = None
        self.last_selected_motif = None
        self.last_comparison_df = None

        self.title_label = tk.Label(root, text="DNA Motif Analyzer", font=("Arial", 16))
        self.title_label.pack(pady=10)

        self.file_button = tk.Button(root, text="Choose first sequence file", command=self.choose_file)
        self.file_button.pack(pady=5)

        self.file_label = tk.Label(root, text="No first file selected")
        self.file_label.pack(pady=5)

        self.file_button_2 = tk.Button(root, text="Choose second sequence file", command=self.choose_file_2)
        self.file_button_2.pack(pady=5)

        self.file_label_2 = tk.Label(root, text="No second file selected")
        self.file_label_2.pack(pady=5)

        self.ncbi_label = tk.Label(root, text="First NCBI accession ID:")
        self.ncbi_label.pack(pady=5)

        self.ncbi_entry = tk.Entry(root, width=30)
        self.ncbi_entry.pack(pady=5)

        self.ncbi_label_2 = tk.Label(root, text="Second NCBI accession ID:")
        self.ncbi_label_2.pack(pady=5)

        self.ncbi_entry_2 = tk.Entry(root, width=30)
        self.ncbi_entry_2.pack(pady=5)

        self.email_label = tk.Label(root, text="Email for NCBI:")
        self.email_label.pack(pady=5)

        self.email_entry = tk.Entry(root, width=30)
        self.email_entry.pack(pady=5)

        self.fetch_button = tk.Button(root, text="Fetch first from NCBI", command=self.fetch_from_ncbi)
        self.fetch_button.pack(pady=5)

        self.fetch_button_2 = tk.Button(root, text="Fetch second from NCBI", command=self.fetch_from_ncbi_2)
        self.fetch_button_2.pack(pady=5)

        self.motif_label = tk.Label(root, text="Enter motifs separated by commas:")
        self.motif_label.pack(pady=5)

        self.motif_entry = tk.Entry(root, width=40)
        self.motif_entry.pack(pady=5)

        self.selected_motif_label = tk.Label(root, text="Select motif for plot/PDF:")
        self.selected_motif_label.pack(pady=5)

        self.selected_motif_var = tk.StringVar()
        self.selected_motif_combobox = ttk.Combobox(
            root,
            textvariable=self.selected_motif_var,
            state="readonly",
            width=20
        )
        self.selected_motif_combobox.pack(pady=5)

        self.segment_label = tk.Label(root, text="Segment length:")
        self.segment_label.pack(pady=5)

        self.segment_entry = tk.Entry(root, width=10)
        self.segment_entry.insert(0, "10")
        self.segment_entry.pack(pady=5)

        self.analyze_button = tk.Button(root, text="Analyze", command=self.run_analysis)
        self.analyze_button.pack(pady=5)

        self.compare_button = tk.Button(root, text="Compare Sequences", command=self.run_comparison)
        self.compare_button.pack(pady=5)

        self.export_csv_button = tk.Button(root, text="Export CSV", command=self.export_csv)
        self.export_csv_button.pack(pady=5)

        self.show_plot_button = tk.Button(root, text="Show Distribution Plot", command=self.show_plot)
        self.show_plot_button.pack(pady=5)

        self.show_positions_button = tk.Button(root, text="Show Motif Positions", command=self.show_positions_plot)
        self.show_positions_button.pack(pady=5)

        self.show_interactive_button = tk.Button(
            root,
            text="Open Interactive Motif Plot",
            command=self.show_interactive_positions_plot
        )
        self.show_interactive_button.pack(pady=5)

        self.save_plot_button = tk.Button(root, text="Save Plot as PNG", command=self.save_plot)
        self.save_plot_button.pack(pady=5)

        self.export_pdf_button = tk.Button(root, text="Export PDF", command=self.export_pdf)
        self.export_pdf_button.pack(pady=5)

        self.result_text = tk.Text(root, height=22, width=110)
        self.result_text.pack(pady=10)

    def _load_sequence_from_path(self, path):
        lowered = path.lower()

        if lowered.endswith(".txt"):
            return load_sequence_from_txt(path)
        if lowered.endswith(".fasta") or lowered.endswith(".fa"):
            return load_sequence_from_fasta(path)

        raise ValueError("Unsupported file format. Please choose TXT, FASTA, or FA.")

    def choose_file(self):
        self.file_path = filedialog.askopenfilename(
            filetypes=[("Sequence files", "*.txt *.fasta *.fa"), ("All files", "*.*")]
        )

        if self.file_path:
            self.file_label.config(text=self.file_path)

            try:
                self.sequence = self._load_sequence_from_path(self.file_path)
                messagebox.showinfo("Success", "First sequence loaded successfully.")
            except Exception as e:
                self.sequence = ""
                messagebox.showerror("Error", f"Failed to load first sequence: {e}")

    def choose_file_2(self):
        self.file_path_2 = filedialog.askopenfilename(
            filetypes=[("Sequence files", "*.txt *.fasta *.fa"), ("All files", "*.*")]
        )

        if self.file_path_2:
            self.file_label_2.config(text=self.file_path_2)

            try:
                self.sequence_2 = self._load_sequence_from_path(self.file_path_2)
                messagebox.showinfo("Success", "Second sequence loaded successfully.")
            except Exception as e:
                self.sequence_2 = ""
                messagebox.showerror("Error", f"Failed to load second sequence: {e}")

    def fetch_from_ncbi(self):
        accession_id = self.ncbi_entry.get().strip()
        email = self.email_entry.get().strip()

        if not accession_id or not email:
            messagebox.showerror("Error", "Please enter first accession ID and email.")
            return

        try:
            self.sequence = fetch_sequence_from_ncbi(accession_id, email)
            self.file_label.config(text=f"Loaded first from NCBI: {accession_id}")
            messagebox.showinfo("Success", "First sequence downloaded from NCBI.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download first sequence: {e}")

    def fetch_from_ncbi_2(self):
        accession_id = self.ncbi_entry_2.get().strip()
        email = self.email_entry.get().strip()

        if not accession_id or not email:
            messagebox.showerror("Error", "Please enter second accession ID and email.")
            return

        try:
            self.sequence_2 = fetch_sequence_from_ncbi(accession_id, email)
            self.file_label_2.config(text=f"Loaded second from NCBI: {accession_id}")
            messagebox.showinfo("Success", "Second sequence downloaded from NCBI.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download second sequence: {e}")

    def _get_motifs_and_segment_length(self):
        motifs_text = self.motif_entry.get().strip()

        if not motifs_text:
            raise ValueError("Please enter at least one motif.")

        motifs = normalize_motifs(motifs_text.split(","))

        if not motifs:
            raise ValueError("Please enter at least one valid motif.")

        segment_text = self.segment_entry.get().strip()
        if not segment_text:
            raise ValueError("Segment length cannot be empty.")

        try:
            segment_length = int(segment_text)
        except ValueError:
            raise ValueError("Segment length must be an integer.")

        if segment_length <= 0:
            raise ValueError("Segment length must be a positive integer.")

        return motifs, segment_length

    def _refresh_statistics_for_selected_motif(self):
        if not self.sequence:
            raise ValueError("Sequence is not loaded.")

        motif = self.selected_motif_var.get().strip()
        if not motif:
            raise ValueError("Please select a motif.")

        segment_text = self.segment_entry.get().strip()
        if not segment_text:
            raise ValueError("Segment length cannot be empty.")

        segment_length = int(segment_text)
        if segment_length <= 0:
            raise ValueError("Segment length must be a positive integer.")

        self.last_selected_motif = motif
        self.last_statistics_df = build_statistics_dataframe(self.sequence, motif, segment_length)

    def show_interactive_positions_plot(self):
        if not self.last_results or not self.sequence:
            messagebox.showerror("Error", "No motif analysis results available.")
            return

        try:
            os.makedirs("results", exist_ok=True)
            output_html = interactive_motif_positions(self.last_results, len(self.sequence))
            webbrowser.open(output_html)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate interactive plot: {e}")

    def run_analysis(self):
        if not self.sequence:
            messagebox.showerror("Error", "Please load a sequence from file or NCBI.")
            return

        try:
            motifs, segment_length = self._get_motifs_and_segment_length()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        results = analyze_multiple_motifs(self.sequence, motifs)

        self.last_results = results
        self.last_comparison_df = None

        self.selected_motif_combobox["values"] = motifs
        self.selected_motif_combobox.set(motifs[0])

        self.last_selected_motif = motifs[0]
        self.last_statistics_df = build_statistics_dataframe(self.sequence, self.last_selected_motif, segment_length)

        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, f"Sequence length: {len(self.sequence)}\n")
        self.result_text.insert(tk.END, f"Segment length: {segment_length}\n\n")

        for result in results:
            line = f"Motif: {result['motif']} | Count: {result['count']} | Positions: {result['positions']}\n"
            self.result_text.insert(tk.END, line)

        self.result_text.insert(tk.END, "\nSegment statistics for first motif:\n")
        self.result_text.insert(tk.END, self.last_statistics_df.to_string(index=False))
        self.result_text.insert(tk.END, "\n")

    def run_comparison(self):
        if not self.sequence or not self.sequence_2:
            messagebox.showerror("Error", "Please load two sequences before comparison.")
            return

        try:
            motifs, _ = self._get_motifs_and_segment_length()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        self.last_comparison_df = compare_sequences(self.sequence, self.sequence_2, motifs)

        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, "Sequence comparison results:\n\n")
        self.result_text.insert(tk.END, self.last_comparison_df.to_string(index=False))
        self.result_text.insert(tk.END, "\n")

    def export_csv(self):
        if self.last_statistics_df is None and self.last_comparison_df is None:
            messagebox.showerror("Error", "No analysis results available for export.")
            return

        output_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )

        if not output_path:
            return

        try:
            if self.last_comparison_df is not None:
                export_results_to_csv(self.last_comparison_df, output_path)
            else:
                export_results_to_csv(self.last_statistics_df, output_path)

            messagebox.showinfo("Success", f"CSV exported to:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV: {e}")

    def show_plot(self):
        if not self.last_results or not self.sequence:
            messagebox.showerror("Error", "No analysis results available for plotting.")
            return

        try:
            self._refresh_statistics_for_selected_motif()
            plot_motif_distribution(self.last_statistics_df, self.last_selected_motif, show_plot=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate plot: {e}")

    def show_positions_plot(self):
        if not self.last_results or not self.sequence:
            messagebox.showerror("Error", "No motif analysis results available.")
            return

        try:
            plot_motif_positions(self.last_results, len(self.sequence), show_plot=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate motif position plot: {e}")

    def save_plot(self):
        if not self.last_results or not self.sequence:
            messagebox.showerror("Error", "No analysis results available for saving.")
            return

        output_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")]
        )

        if not output_path:
            return

        try:
            self._refresh_statistics_for_selected_motif()
            plot_motif_distribution(
                self.last_statistics_df,
                self.last_selected_motif,
                output_path=output_path,
                show_plot=False
            )
            messagebox.showinfo("Success", f"Plot saved to:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save plot: {e}")

    def export_pdf(self):
        if not self.last_results or not self.sequence:
            messagebox.showerror("Error", "No analysis results available for PDF export.")
            return

        output_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )

        if not output_path:
            return

        try:
            self._refresh_statistics_for_selected_motif()
            export_report_to_pdf(
                self.last_statistics_df,
                self.last_selected_motif,
                len(self.sequence),
                output_path
            )
            messagebox.showinfo("Success", f"PDF report exported to:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF: {e}")