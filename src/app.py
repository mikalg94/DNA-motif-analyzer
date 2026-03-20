import os
import webbrowser
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from src.export_utils import (
    create_motif_distribution_figure,
    create_motif_positions_figure,
    create_multiple_motifs_summary_figure,
    export_report_to_pdf,
    export_results_to_csv,
    interactive_motif_positions,
    plot_motif_distribution,
    plot_motif_positions,
    plot_multiple_motifs_summary,
    save_analysis_history,
)

from src.io_utils import load_sequence_from_fasta, load_sequence_from_txt
from src.motif_analysis import (
    analyze_multiple_motifs,
    build_statistics_dataframe,
    compare_sequences,
)
from src.ncbi_utils import fetch_sequence_from_ncbi
from src.validation_utils import normalize_motifs

from datetime import datetime

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("DNA Motif Analyzer")
        self.root.geometry("1000x900")
        self.root.resizable(True, True)

        self.file_path = None
        self.file_path_2 = None
        self.sequence = ""
        self.sequence_2 = ""

        self.last_results = []
        self.last_statistics_df = None
        self.last_selected_motif = None
        self.last_comparison_df = None

        self.main_canvas = tk.Canvas(self.root)
        self.main_scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.main_canvas.yview)

        self.scrollable_frame = tk.Frame(self.main_canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )

        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)

        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.main_scrollbar.pack(side="right", fill="y")

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.title_label = tk.Label(self.scrollable_frame, text="DNA Motif Analyzer", font=("Arial", 18, "bold"))
        self.title_label.pack(pady=10)

        self.files_frame = tk.LabelFrame(self.scrollable_frame, text="Sequence files", padx=10, pady=10)
        self.files_frame.pack(fill="x", padx=15, pady=5)

        self.file_button = tk.Button(self.files_frame, text="Choose first sequence file", command=self.choose_file, width=25)
        self.file_button.pack(pady=3)

        self.file_label = tk.Label(self.files_frame, text="No first file selected")
        self.file_label.pack(pady=3)

        self.file_button_2 = tk.Button(self.files_frame, text="Choose second sequence file", command=self.choose_file_2, width=25)
        self.file_button_2.pack(pady=3)

        self.file_label_2 = tk.Label(self.files_frame, text="No second file selected")
        self.file_label_2.pack(pady=3)

        self.ncbi_frame = tk.LabelFrame(self.scrollable_frame, text="NCBI download", padx=10, pady=10)
        self.ncbi_frame.pack(fill="x", padx=15, pady=5)

        self.ncbi_label = tk.Label(self.ncbi_frame, text="First NCBI accession ID:")
        self.ncbi_label.pack(pady=3)

        self.ncbi_entry = tk.Entry(self.ncbi_frame, width=35)
        self.ncbi_entry.pack(pady=3)

        self.ncbi_label_2 = tk.Label(self.ncbi_frame, text="Second NCBI accession ID:")
        self.ncbi_label_2.pack(pady=3)

        self.ncbi_entry_2 = tk.Entry(self.ncbi_frame, width=35)
        self.ncbi_entry_2.pack(pady=3)

        self.email_label = tk.Label(self.ncbi_frame, text="Email for NCBI:")
        self.email_label.pack(pady=3)

        self.email_entry = tk.Entry(self.ncbi_frame, width=35)
        self.email_entry.pack(pady=3)

        self.fetch_button = tk.Button(self.ncbi_frame, text="Fetch first from NCBI", command=self.fetch_from_ncbi, width=25)
        self.fetch_button.pack(pady=3)

        self.fetch_button_2 = tk.Button(self.ncbi_frame, text="Fetch second from NCBI", command=self.fetch_from_ncbi_2, width=25)
        self.fetch_button_2.pack(pady=3)

        self.analysis_frame = tk.LabelFrame(self.scrollable_frame, text="Analysis settings", padx=10, pady=10)
        self.analysis_frame.pack(fill="x", padx=15, pady=5)

        self.motif_label = tk.Label(self.analysis_frame, text="Enter motifs separated by commas:")
        self.motif_label.pack(pady=3)

        self.motif_entry = tk.Entry(self.analysis_frame, width=45)
        self.motif_entry.pack(pady=3)

        self.selected_motif_label = tk.Label(self.analysis_frame, text="Select motif for plot/PDF:")
        self.selected_motif_label.pack(pady=3)

        self.selected_motif_var = tk.StringVar()
        self.selected_motif_combobox = ttk.Combobox(
            self.analysis_frame,
            textvariable=self.selected_motif_var,
            state="readonly",
            width=25
        )
        self.selected_motif_combobox.pack(pady=3)

        self.segment_label = tk.Label(self.analysis_frame, text="Segment length:")
        self.segment_label.pack(pady=3)

        self.segment_entry = tk.Entry(self.analysis_frame, width=10)
        self.segment_entry.insert(0, "10")
        self.segment_entry.pack(pady=3)

        self.actions_frame = tk.LabelFrame(self.scrollable_frame, text="Actions", padx=10, pady=10)
        self.actions_frame.pack(fill="x", padx=15, pady=5)

        self.analyze_button = tk.Button(self.actions_frame, text="Analyze", command=self.run_analysis, width=25)
        self.analyze_button.pack(pady=3)

        self.compare_button = tk.Button(self.actions_frame, text="Compare Sequences", command=self.run_comparison, width=25)
        self.compare_button.pack(pady=3)

        self.export_csv_button = tk.Button(self.actions_frame, text="Export CSV", command=self.export_csv, width=25)
        self.export_csv_button.pack(pady=3)

        self.show_plot_button = tk.Button(self.actions_frame, text="Show Distribution Plot", command=self.show_plot, width=25)
        self.show_plot_button.pack(pady=3)

        self.show_multi_plot_button = tk.Button(
            self.actions_frame,
            text="Show Multi-Motif Summary",
            command=self.show_multi_motif_plot,
            width=25
        )
        self.show_multi_plot_button.pack(pady=3)

        self.show_positions_button = tk.Button(self.actions_frame, text="Show Motif Positions", command=self.show_positions_plot, width=25)
        self.show_positions_button.pack(pady=3)

        self.show_interactive_button = tk.Button(
            self.actions_frame,
            text="Open Interactive Motif Plot",
            command=self.show_interactive_positions_plot,
            width=25
        )
        self.show_interactive_button.pack(pady=3)

        self.save_plot_button = tk.Button(self.actions_frame, text="Save Plot as PNG", command=self.save_plot, width=25)
        self.save_plot_button.pack(pady=3)

        self.export_pdf_button = tk.Button(self.actions_frame, text="Export PDF", command=self.export_pdf, width=25)
        self.export_pdf_button.pack(pady=3)

        self.show_history_button = tk.Button(
            self.actions_frame,
            text="Show Analysis History",
            command=self.show_analysis_history,
            width=25
        )
        self.show_history_button.pack(pady=3)

        self.result_frame = tk.Frame(self.scrollable_frame)
        self.result_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.result_scrollbar = tk.Scrollbar(self.result_frame)
        self.result_scrollbar.pack(side="right", fill="y")

        self.result_text = tk.Text(
            self.result_frame,
            height=8,
            width=110,
            yscrollcommand=self.result_scrollbar.set
        )
        self.result_text.pack(side="left", fill="both", expand=True)

        self.result_scrollbar.config(command=self.result_text.yview)

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
                messagebox.showinfo("Success", f"First sequence loaded successfully.\nLength: {len(self.sequence)}")
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
                messagebox.showinfo("Success", f"Second sequence loaded successfully.\nLength: {len(self.sequence_2)}")
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
            messagebox.showinfo("Success", f"First sequence downloaded from NCBI.\nLength: {len(self.sequence)}")
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
            messagebox.showinfo("Success", f"Second sequence downloaded from NCBI.\nLength: {len(self.sequence_2)}")
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

        try:
            segment_length = int(segment_text)
        except ValueError:
            raise ValueError("Segment length must be an integer.")

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

    def show_multi_motif_plot(self):
        if not self.last_results:
            messagebox.showerror("Error", "No motif analysis results available.")
            return

        try:
            fig = create_multiple_motifs_summary_figure(self.last_results)
            self._show_figure_window("Multi-Motif Summary", fig)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate multi-motif plot: {e}")

    def _show_figure_window(self, title, fig):
        plot_window = tk.Toplevel(self.root)
        plot_window.title(title)
        plot_window.geometry("950x650")
        plot_window.resizable(True, True)

        frame = tk.Frame(plot_window)
        frame.pack(fill="both", expand=True)

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        toolbar = NavigationToolbar2Tk(canvas, frame)
        toolbar.update()

    def _show_results_window(self, title, content):
        result_window = tk.Toplevel(self.root)
        result_window.title(title)
        result_window.geometry("1000x700")
        result_window.resizable(True, True)

        frame = tk.Frame(result_window)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        text_widget = tk.Text(
            frame,
            wrap="word",
            yscrollcommand=scrollbar.set
        )
        text_widget.pack(side="left", fill="both", expand=True)

        scrollbar.config(command=text_widget.yview)

        text_widget.insert("1.0", content)
        text_widget.config(state="disabled")

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
        self.last_statistics_df = build_statistics_dataframe(
            self.sequence,
            self.last_selected_motif,
            segment_length
        )

        output = []
        output.append("ANALYSIS RESULTS\n")
        output.append(f"Sequence length: {len(self.sequence)}")
        output.append(f"Recognized motifs: {', '.join(motifs)}")
        output.append(f"Segment length: {segment_length}\n")

        for result in results:
            output.append(
                f"Motif: {result['motif']} | "
                f"Count: {result['count']} | "
                f"Positions: {result['positions']}"
            )

        output.append("\nSegment statistics for selected motif:\n")
        output.append(self.last_statistics_df.to_string(index=False))

        final_text = "\n".join(output)

        history_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operation": "analysis",
            "sequence_1_length": len(self.sequence),
            "sequence_2_length": "",
            "motifs": ", ".join(motifs),
            "segment_length": segment_length,
            "details": "; ".join([f"{result['motif']}={result['count']}" for result in results])
        }
        save_analysis_history(history_entry)

        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, final_text)

        self._show_results_window("Analysis Results", final_text)

    def run_comparison(self):
        if not self.sequence:
            messagebox.showerror("Error", "First sequence is not loaded.")
            return

        if not self.sequence_2:
            messagebox.showerror("Error", "Second sequence is not loaded.")
            return

        try:
            motifs, _ = self._get_motifs_and_segment_length()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        try:
            self.last_comparison_df = compare_sequences(self.sequence, self.sequence_2, motifs)

            output = []
            output.append("COMPARISON RESULTS\n")
            output.append(f"Sequence 1 length: {len(self.sequence)}")
            output.append(f"Sequence 2 length: {len(self.sequence_2)}")
            output.append(f"Recognized motifs: {', '.join(motifs)}\n")

            if self.last_comparison_df.empty:
                output.append("No comparison data to display.")
            else:
                output.append(self.last_comparison_df.to_string(index=False))

            final_text = "\n".join(output)

            comparison_details = []
            for _, row in self.last_comparison_df.iterrows():
                comparison_details.append(
                    f"{row['motif']}: seq1={row['sequence_1_count']}, seq2={row['sequence_2_count']}"
                )

            history_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "operation": "comparison",
                "sequence_1_length": len(self.sequence),
                "sequence_2_length": len(self.sequence_2),
                "motifs": ", ".join(motifs),
                "segment_length": "",
                "details": "; ".join(comparison_details)
            }
            save_analysis_history(history_entry)

            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, final_text)

            self._show_results_window("Comparison Results", final_text)

        except Exception as e:
            messagebox.showerror("Error", f"Comparison failed: {e}")

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
            fig = create_motif_distribution_figure(self.last_statistics_df, self.last_selected_motif)
            self._show_figure_window("Distribution Plot", fig)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate plot: {e}")

    def show_positions_plot(self):
        if not self.last_results or not self.sequence:
            messagebox.showerror("Error", "No motif analysis results available.")
            return

        try:
            fig = create_motif_positions_figure(self.last_results, len(self.sequence))
            self._show_figure_window("Motif Positions", fig)
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

    def show_analysis_history(self):
        history_path = "results/analysis_history.csv"

        if not os.path.exists(history_path):
            messagebox.showinfo("History", "No analysis history available yet.")
            return

        try:
            history_df = pd.read_csv(history_path)
            history_text = history_df.to_string(index=False)
            self._show_results_window("Analysis History", history_text)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open history: {e}")