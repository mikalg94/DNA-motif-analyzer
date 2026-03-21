import os
import threading
import webbrowser
from datetime import datetime

import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from src.export_utils import (
    create_motif_distribution_figure,
    create_motif_positions_figure,
    create_multiple_motifs_summary_figure,
    export_report_to_pdf,
    export_results_to_csv,
    interactive_motif_positions,
    plot_motif_distribution,
    save_analysis_history,
)
from src.gui_sections import (
    build_actions_frame,
    build_analysis_frame,
    build_files_frame,
    build_main_layout,
    build_ncbi_frame,
    build_results_frame,
    build_title,
)
from src.io_utils import load_sequence_from_fasta, load_sequence_from_txt
from src.motif_analysis import (
    analyze_multiple_motifs,
    build_statistics_dataframe,
    compare_sequences,
    calculate_gc_content,
)
from src.ncbi_utils import fetch_sequence_from_ncbi
from src.validation_utils import (
    get_sequence_warning,
    normalize_motifs,
    validate_motifs_against_sequence,
)


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

        build_main_layout(self)
        build_title(self)
        build_files_frame(self)
        build_ncbi_frame(self)
        build_analysis_frame(self)
        build_actions_frame(self)
        build_results_frame(self)

    @staticmethod
    def _load_sequence_from_path(path):
        lowered = path.lower()

        if lowered.endswith(".txt"):
            return load_sequence_from_txt(path)
        if lowered.endswith(".fasta") or lowered.endswith(".fa"):
            return load_sequence_from_fasta(path)

        raise ValueError("Unsupported file format. Please choose TXT, FASTA, or FA.")

    def _set_sequence_data(self, target, sequence, source_label):
        if target == 1:
            self.sequence = sequence
            self.file_label.config(text=source_label)
        else:
            self.sequence_2 = sequence
            self.file_label_2.config(text=source_label)

    def _show_sequence_warning_if_needed(self, sequence):
        warning_message = get_sequence_warning(sequence)
        if warning_message:
            messagebox.showwarning("Sequence Warning", warning_message)

    def _validate_analysis_inputs(self, motifs, sequence):
        validate_motifs_against_sequence(motifs, sequence)

    def _set_ncbi_buttons_state(self, state):
        self.fetch_button.config(state=state)
        self.fetch_button_2.config(state=state)
        self.example_button.config(state=state)
        self.example_button_2.config(state=state)

    def _handle_ncbi_success(self, target, accession_id, sequence, description=None, is_example=False):
        self._show_sequence_warning_if_needed(sequence)

        if is_example:
            self._set_sequence_data(target, sequence, f"Loaded example from NCBI: {accession_id}")
            messagebox.showinfo(
                "Success",
                f"Example sequence loaded successfully.\n"
                f"Description: {description}\n"
                f"Accession: {accession_id}\n"
                f"Length: {len(sequence)}"
            )
        else:
            self._set_sequence_data(target, sequence, f"Loaded from NCBI: {accession_id}")

            if target == 1:
                success_message = f"First sequence downloaded from NCBI.\nLength: {len(sequence)}"
            else:
                success_message = f"Second sequence downloaded from NCBI.\nLength: {len(sequence)}"

            messagebox.showinfo("Success", success_message)

        self._set_ncbi_buttons_state("normal")

    def _handle_ncbi_error(self, error_message):
        self._set_ncbi_buttons_state("normal")
        messagebox.showerror("Error", error_message)

    def _fetch_from_ncbi_worker(self, target, accession_id, email):
        try:
            sequence = fetch_sequence_from_ncbi(accession_id, email)
            self.root.after(
                0,
                lambda: self._handle_ncbi_success(target, accession_id, sequence)
            )
        except Exception as e:
            self.root.after(
                0,
                lambda: self._handle_ncbi_error(f"Failed to download sequence: {e}")
            )

    def _load_example_ncbi_worker(self, target, accession_id, description):
        try:
            email = "test@test.com"
            sequence = fetch_sequence_from_ncbi(accession_id, email)
            self.root.after(
                0,
                lambda: self._handle_ncbi_success(
                    target,
                    accession_id,
                    sequence,
                    description=description,
                    is_example=True
                )
            )
        except Exception as e:
            self.root.after(
                0,
                lambda: self._handle_ncbi_error(f"Failed to load example: {e}")
            )

    def choose_file(self, target):
        selected_path = filedialog.askopenfilename(
            filetypes=[("Sequence files", "*.txt *.fasta *.fa"), ("All files", "*.*")]
        )

        if not selected_path:
            return

        try:
            sequence = self._load_sequence_from_path(selected_path)

            if target == 1:
                self.file_path = selected_path
                success_message = f"First sequence loaded successfully.\nLength: {len(sequence)}"
            else:
                self.file_path_2 = selected_path
                success_message = f"Second sequence loaded successfully.\nLength: {len(sequence)}"

            self._set_sequence_data(target, sequence, selected_path)
            self._show_sequence_warning_if_needed(sequence)
            messagebox.showinfo("Success", success_message)

        except Exception as e:
            if target == 1:
                self.sequence = ""
            else:
                self.sequence_2 = ""

            messagebox.showerror("Error", f"Failed to load sequence: {e}")

    def fetch_from_ncbi(self, target):
        accession_entry = self.ncbi_entry if target == 1 else self.ncbi_entry_2
        accession_id = accession_entry.get().strip()
        email = self.email_entry.get().strip()

        if not accession_id or not email:
            messagebox.showerror("Error", "Please enter accession ID and email.")
            return

        self._set_ncbi_buttons_state("disabled")

        thread = threading.Thread(
            target=self._fetch_from_ncbi_worker,
            args=(target, accession_id, email),
            daemon=True
        )
        thread.start()

    def load_example_ncbi(self, target, accession_id, description):
        self._set_ncbi_buttons_state("disabled")

        thread = threading.Thread(
            target=self._load_example_ncbi_worker,
            args=(target, accession_id, description),
            daemon=True
        )
        thread.start()

    def _get_segment_length(self):
        segment_text = self.segment_entry.get().strip()

        if not segment_text:
            raise ValueError("Segment length cannot be empty.")

        try:
            segment_length = int(segment_text)
        except ValueError:
            raise ValueError("Segment length must be an integer.")

        if segment_length <= 0:
            raise ValueError("Segment length must be a positive integer.")

        return segment_length

    def _get_motifs_and_segment_length(self):
        motifs_text = self.motif_entry.get().strip()

        if not motifs_text:
            raise ValueError("Please enter at least one motif.")

        motifs = normalize_motifs(motifs_text.split(","))

        if not motifs:
            raise ValueError("Please enter at least one valid motif.")

        segment_length = self._get_segment_length()
        return motifs, segment_length

    def _refresh_statistics_for_selected_motif(self):
        if not self.sequence:
            raise ValueError("Sequence is not loaded.")

        motif = self.selected_motif_var.get().strip()
        if not motif:
            raise ValueError("Please select a motif.")

        segment_length = self._get_segment_length()

        self.last_selected_motif = motif
        self.last_statistics_df = build_statistics_dataframe(
            self.sequence,
            motif,
            segment_length
        )

    def _prepare_selected_motif_statistics(self):
        if not self.last_results or not self.sequence:
            raise ValueError("No analysis results available.")

        self._refresh_statistics_for_selected_motif()

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

    def _format_analysis_results(self, motifs, segment_length, results):
        output = [
            "ANALYSIS RESULTS\n",
            f"Sequence length: {len(self.sequence)}",
            f"GC content: {calculate_gc_content(self.sequence)}%",
            f"Recognized motifs: {', '.join(motifs)}",
            f"Segment length: {segment_length}\n",
        ]

        for result in results:
            output.append(
                f"Motif: {result['motif']} | "
                f"Count: {result['count']} | "
                f"Positions: {result['positions']}"
            )

        output.append("\nSegment statistics for selected motif:\n")
        output.append(self.last_statistics_df.to_string(index=False))

        return "\n".join(output)

    def _format_comparison_results(self, motifs):
        output = [
            "COMPARISON RESULTS\n",
            f"Sequence 1 length: {len(self.sequence)}",
            f"Sequence 2 length: {len(self.sequence_2)}",
            f"Recognized motifs: {', '.join(motifs)}\n",
        ]

        if self.last_comparison_df.empty:
            output.append("No comparison data to display.")
        else:
            output.append(self.last_comparison_df.to_string(index=False))

        return "\n".join(output)

    def _save_analysis_history(self, motifs, segment_length, results):
        history_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operation": "analysis",
            "sequence_1_length": len(self.sequence),
            "sequence_2_length": "",
            "motifs": ", ".join(motifs),
            "segment_length": segment_length,
            "details": "; ".join(
                [f"{result['motif']}={result['count']}" for result in results]
            )
        }
        save_analysis_history(history_entry)

    def _save_comparison_history(self, motifs):
        comparison_details = []
        for _, row in self.last_comparison_df.iterrows():
            comparison_details.append(
                f"{row['motif']}: seq1={row['sequence_1_count']}, "
                f"seq2={row['sequence_2_count']}"
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

    def _display_results(self, window_title, content):
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, content)
        self._show_results_window(window_title, content)

    def _prepare_analysis_results(self, motifs, segment_length):
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

        return results

    def _prepare_comparison_results(self, motifs):
        self.last_comparison_df = compare_sequences(
            self.sequence,
            self.sequence_2,
            motifs
        )
        return self.last_comparison_df

    def run_analysis(self):
        if not self.sequence:
            messagebox.showerror("Error", "Please load a sequence from file or NCBI.")
            return

        try:
            motifs, segment_length = self._get_motifs_and_segment_length()
            self._validate_analysis_inputs(motifs, self.sequence)
            results = self._prepare_analysis_results(motifs, segment_length)
            final_text = self._format_analysis_results(motifs, segment_length, results)
            self._save_analysis_history(motifs, segment_length, results)
            self._display_results("Analysis Results", final_text)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def run_comparison(self):
        if not self.sequence:
            messagebox.showerror("Error", "First sequence is not loaded.")
            return

        if not self.sequence_2:
            messagebox.showerror("Error", "Second sequence is not loaded.")
            return

        try:
            motifs, _ = self._get_motifs_and_segment_length()
            self._validate_analysis_inputs(motifs, self.sequence)
            self._validate_analysis_inputs(motifs, self.sequence_2)
            self._prepare_comparison_results(motifs)
            final_text = self._format_comparison_results(motifs)
            self._save_comparison_history(motifs)
            self._display_results("Comparison Results", final_text)
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
        try:
            self._prepare_selected_motif_statistics()
            fig = create_motif_distribution_figure(
                self.last_statistics_df,
                self.last_selected_motif
            )
            self._show_figure_window("Distribution Plot", fig)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate plot: {e}")

    def show_multi_motif_plot(self):
        if not self.last_results:
            messagebox.showerror("Error", "No motif analysis results available.")
            return

        try:
            fig = create_multiple_motifs_summary_figure(self.last_results)
            self._show_figure_window("Multi-Motif Summary", fig)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate multi-motif plot: {e}")

    def show_positions_plot(self):
        if not self.last_results or not self.sequence:
            messagebox.showerror("Error", "No motif analysis results available.")
            return

        try:
            fig = create_motif_positions_figure(self.last_results, len(self.sequence))
            self._show_figure_window("Motif Positions", fig)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate motif position plot: {e}")

    def show_interactive_positions_plot(self):
        if not self.last_results or not self.sequence:
            messagebox.showerror("Error", "No motif analysis results available.")
            return

        try:
            os.makedirs("results", exist_ok=True)
            output_html = interactive_motif_positions(
                self.last_results,
                len(self.sequence)
            )

            info_window = tk.Toplevel(self.root)
            info_window.title("Interactive Motif Plot")
            info_window.geometry("600x220")
            info_window.resizable(False, False)

            label1 = tk.Label(
                info_window,
                text="Interactive motif plot has been created successfully.",
                font=("Arial", 11, "bold")
            )
            label1.pack(pady=10)

            label2 = tk.Label(
                info_window,
                text=f"Saved file:\n{output_html}",
                wraplength=550,
                justify="center"
            )
            label2.pack(pady=10)

            open_button = tk.Button(
                info_window,
                text="Open in browser",
                command=lambda: webbrowser.open(output_html),
                width=20
            )
            open_button.pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate interactive plot: {e}")

    def save_plot(self):
        output_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")]
        )

        if not output_path:
            return

        try:
            self._prepare_selected_motif_statistics()
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
        output_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )

        if not output_path:
            return

        try:
            self._prepare_selected_motif_statistics()
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