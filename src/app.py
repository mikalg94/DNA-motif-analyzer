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
    create_gc_content_figure,
    create_gc_comparison_figure,
    create_gc_motif_overlay_figure,
    export_report_to_pdf,
    export_results_to_csv,
    export_session_to_json,
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
    build_status_bar,
)
from src.io_utils import load_sequence_from_fasta, load_sequence_from_txt
from src.motif_analysis import (
    analyze_multiple_motifs,
    build_statistics_dataframe,
    calculate_at_content,
    calculate_average_motifs_per_segment,
    calculate_gc_content,
    calculate_motif_density_per_1000_nt,
    compare_sequences,
    count_unknown_bases,
    get_segment_with_max_motifs,
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
        build_status_bar(self)
        self._update_action_buttons_state()

    def _update_action_buttons_state(self):
        has_sequence_1 = bool(self.sequence)
        has_sequence_2 = bool(self.sequence_2)
        has_analysis_results = bool(self.last_results)
        has_statistics = self.last_statistics_df is not None
        has_comparison = self.last_comparison_df is not None
        has_any_export_data = has_statistics or has_comparison

        self.analyze_button.config(state="normal" if has_sequence_1 else "disabled")
        self.compare_button.config(
            state="normal" if has_sequence_1 and has_sequence_2 else "disabled"
        )
        self.export_json_button.config(
            state="normal" if has_any_export_data or has_analysis_results else "disabled"
        )
        self.export_csv_button.config(
            state="normal" if has_any_export_data else "disabled"
        )
        self.show_plot_button.config(
            state="normal" if has_analysis_results else "disabled"
        )
        self.show_multi_plot_button.config(
            state="normal" if has_analysis_results else "disabled"
        )
        self.show_positions_button.config(
            state="normal" if has_analysis_results else "disabled"
        )
        self.show_highlighted_sequence_button.config(
            state="normal" if has_analysis_results else "disabled"
        )
        self.show_interactive_button.config(
            state="normal" if has_analysis_results else "disabled"
        )
        self.save_plot_button.config(
            state="normal" if has_analysis_results else "disabled"
        )
        self.export_pdf_button.config(
            state="normal" if has_analysis_results else "disabled"
        )
        self.show_history_button.config(
            state="normal" if os.path.exists("results/analysis_history.csv") else "disabled"
        )

        self.show_gc_button.config(
            state="normal" if has_statistics else "disabled"
        )
        self.show_gc_comparison_button.config(
            state="normal" if has_sequence_1 and has_sequence_2 else "disabled"
        )
        self.show_gc_motif_overlay_button.config(
            state="normal" if has_analysis_results else "disabled"
        )

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

        self._update_action_buttons_state()
        self._set_ncbi_buttons_state("normal")
        self._set_status("Sequence downloaded successfully")

    def _handle_ncbi_error(self, error_message):
        self._set_ncbi_buttons_state("normal")
        self._update_action_buttons_state()
        self._set_status("NCBI download failed")
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
        self._set_status("Loading sequence from file...")
        selected_path = filedialog.askopenfilename(
            filetypes=[("Sequence files", "*.txt *.fasta *.fa"), ("All files", "*.*")]
        )

        if not selected_path:
            self._set_status("Ready")
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
            self._update_action_buttons_state()
            self._show_sequence_warning_if_needed(sequence)
            self._set_status("Sequence loaded successfully")
            messagebox.showinfo("Success", success_message)

        except Exception as e:
            if target == 1:
                self.sequence = ""
            else:
                self.sequence_2 = ""

            self._set_status("Failed to load sequence")
            self._update_action_buttons_state()
            messagebox.showerror("Error", f"Failed to load sequence: {e}")

    def fetch_from_ncbi(self, target):
        accession_entry = self.ncbi_entry if target == 1 else self.ncbi_entry_2
        accession_id = accession_entry.get().strip()
        email = self.email_entry.get().strip()

        if not accession_id or not email:
            self._set_status("NCBI download failed")
            messagebox.showerror("Error", "Please enter accession ID and email.")
            return

        self._set_status("Downloading sequence from NCBI...")
        self._set_ncbi_buttons_state("disabled")

        thread = threading.Thread(
            target=self._fetch_from_ncbi_worker,
            args=(target, accession_id, email),
            daemon=True
        )
        thread.start()

    def load_example_ncbi(self, target, accession_id, description):
        self._set_status("Downloading example sequence from NCBI...")
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

        mode = self.segment_mode_var.get()

        self.last_statistics_df = build_statistics_dataframe(
            self.sequence,
            motif,
            segment_length,
            mode=mode
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

    def show_gc_plot(self):
        if self.last_statistics_df is not None:
            try:
                fig = create_gc_content_figure(self.last_statistics_df)
                self._show_figure_window("GC Content Plot", fig)
                self._set_status("GC plot generated")
            except Exception as e:
                self._set_status("Failed to generate GC plot")
                messagebox.showerror("Error", f"Failed to generate GC plot: {e}")
        else:
            self._set_status("No analysis results available")
            messagebox.showerror("Error", "No analysis results available.")

    def show_gc_comparison_plot(self):
        if not self.sequence or not self.sequence_2:
            self._set_status("GC comparison failed")
            messagebox.showerror("Error", "Both sequences must be loaded.")
            return

        try:
            self._set_status("Generating GC comparison plot...")
            segment_length = self._get_segment_length()

            df1 = build_statistics_dataframe(
                self.sequence,
                self.last_selected_motif or "ATG",
                segment_length
            )

            df2 = build_statistics_dataframe(
                self.sequence_2,
                self.last_selected_motif or "ATG",
                segment_length
            )

            fig = create_gc_comparison_figure(df1, df2)
            self._show_figure_window("GC Comparison", fig)
            self._set_status("GC comparison plot generated")

        except Exception as e:
            self._set_status("Failed to generate GC comparison")
            messagebox.showerror("Error", f"Failed to generate GC comparison: {e}")

    def show_gc_motif_overlay(self):
        if not self.last_results or not self.sequence:
            self._set_status("No analysis results available")
            messagebox.showerror("Error", "No analysis results available.")
            return

        try:
            self._set_status("Generating GC and motif overlay plot...")
            self._prepare_selected_motif_statistics()

            fig = create_gc_motif_overlay_figure(
                self.last_statistics_df,
                self.last_results,
                len(self.sequence)
            )

            self._show_figure_window("GC + Motif Overlay", fig)
            self._set_status("GC and motif overlay plot generated")

        except Exception as e:
            self._set_status("Failed to generate overlay plot")
            messagebox.showerror("Error", f"Failed to generate overlay plot: {e}")

    def _build_extended_sequence_statistics(self, motif, segment_length):
        max_segment = get_segment_with_max_motifs(
            self.sequence,
            motif,
            segment_length
        )

        if max_segment is None:
            max_segment_text = "No segment data available"
        else:
            max_segment_text = (
                f"Segment {max_segment['segment_id']} "
                f"({max_segment['start']}-{max_segment['end']}), "
                f"count={max_segment['motif_count']}"
            )

        return {
            "gc_content": calculate_gc_content(self.sequence),
            "at_content": calculate_at_content(self.sequence),
            "unknown_bases": count_unknown_bases(self.sequence),
            "motif_density_per_1000_nt": calculate_motif_density_per_1000_nt(
                self.sequence,
                motif
            ),
            "average_motifs_per_segment": calculate_average_motifs_per_segment(
                self.sequence,
                motif,
                segment_length
            ),
            "max_segment_text": max_segment_text,
        }

    def _filter_and_sort_results(self, results):
        processed_results = results[:]

        if self.only_found_var.get():
            processed_results = [
                result for result in processed_results
                if result["count"] > 0
            ]

        sort_mode = self.sort_results_var.get()

        if sort_mode == "count_desc":
            processed_results.sort(key=lambda item: item["count"], reverse=True)
        elif sort_mode == "count_asc":
            processed_results.sort(key=lambda item: item["count"])

        top_n_text = self.top_n_entry.get().strip()
        if top_n_text:
            try:
                top_n = int(top_n_text)
                if top_n > 0:
                    processed_results = processed_results[:top_n]
            except ValueError:
                raise ValueError("Top N must be a positive integer.")

        return processed_results

    def _format_analysis_results(self, motifs, segment_length, results):
        selected_motif = self.last_selected_motif or motifs[0]
        extended_stats = self._build_extended_sequence_statistics(
            selected_motif,
            segment_length
        )

        output = [
            "ANALYSIS RESULTS\n",
            f"Sequence length: {len(self.sequence)}",
            f"GC content: {extended_stats['gc_content']}%",
            f"AT content: {extended_stats['at_content']}%",
            f"Unknown bases (N): {extended_stats['unknown_bases']}",
            f"Recognized motifs: {', '.join(motifs)}",
            f"Segment length: {segment_length}",
            f"Selected motif for detailed statistics: {selected_motif}",
            f"Motif density per 1000 nt: {extended_stats['motif_density_per_1000_nt']}",
            f"Average motifs per segment: {extended_stats['average_motifs_per_segment']}",
            f"Segment with highest count: {extended_stats['max_segment_text']}\n",
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

    def _clear_result_table(self):
        self.result_tree.delete(*self.result_tree.get_children())
        self.result_tree["columns"] = ()

    def _display_dataframe_in_table(self, df):
        self._clear_result_table()

        if df is None or df.empty:
            return

        columns = list(df.columns)
        self.result_tree["columns"] = columns

        for column in columns:
            self.result_tree.heading(column, text=column)
            self.result_tree.column(column, width=130, anchor="center")

        for _, row in df.iterrows():
            values = [str(value) for value in row.tolist()]
            self.result_tree.insert("", tk.END, values=values)

    def _display_results(self, window_title, content, dataframe=None):
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, content)

        self._display_dataframe_in_table(dataframe)
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
            self._set_status("Analysis failed")
            messagebox.showerror("Error", "Please load a sequence from file or NCBI.")
            return

        try:
            self._set_status("Running analysis...")
            motifs, segment_length = self._get_motifs_and_segment_length()
            self._validate_analysis_inputs(motifs, self.sequence)
            results = self._prepare_analysis_results(motifs, segment_length)
            display_results = self._filter_and_sort_results(results)
            final_text = self._format_analysis_results(motifs, segment_length, display_results)
            self._save_analysis_history(motifs, segment_length, results)
            self._display_results(
                "Analysis Results",
                final_text,
                dataframe=self.last_statistics_df
            )
            self._update_action_buttons_state()
            self._set_status("Analysis complete")
        except Exception as e:
            self._set_status("Analysis failed")
            messagebox.showerror("Error", str(e))

    def run_comparison(self):
        if not self.sequence:
            self._set_status("Comparison failed")
            messagebox.showerror("Error", "First sequence is not loaded.")
            return

        if not self.sequence_2:
            self._set_status("Comparison failed")
            messagebox.showerror("Error", "Second sequence is not loaded.")
            return

        try:
            self._set_status("Comparing sequences...")
            motifs, _ = self._get_motifs_and_segment_length()
            self._validate_analysis_inputs(motifs, self.sequence)
            self._validate_analysis_inputs(motifs, self.sequence_2)
            self._prepare_comparison_results(motifs)
            if self.only_found_var.get():
                self.last_comparison_df = self.last_comparison_df[
                    (self.last_comparison_df["sequence_1_count"] > 0) |
                    (self.last_comparison_df["sequence_2_count"] > 0)
                ]

            sort_mode = self.sort_results_var.get()
            if sort_mode == "count_desc":
                self.last_comparison_df = self.last_comparison_df.sort_values(
                    by=["sequence_1_count", "sequence_2_count"],
                    ascending=False
                )
            elif sort_mode == "count_asc":
                self.last_comparison_df = self.last_comparison_df.sort_values(
                    by=["sequence_1_count", "sequence_2_count"],
                    ascending=True
                )

            top_n_text = self.top_n_entry.get().strip()
            if top_n_text:
                try:
                    top_n = int(top_n_text)
                    if top_n > 0:
                        self.last_comparison_df = self.last_comparison_df.head(top_n)
                except ValueError:
                    raise ValueError("Top N must be a positive integer.")
            final_text = self._format_comparison_results(motifs)
            self._save_comparison_history(motifs)
            self._display_results(
                "Comparison Results",
                final_text,
                dataframe=self.last_comparison_df
            )
            self._update_action_buttons_state()
            self._set_status("Comparison complete")
        except Exception as e:
            self._set_status("Comparison failed")
            messagebox.showerror("Error", f"Comparison failed: {e}")

    def _build_session_data(self):
        session_data = {
            "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sequence_1_length": len(self.sequence) if self.sequence else 0,
            "sequence_2_length": len(self.sequence_2) if self.sequence_2 else 0,
            "file_path_1": self.file_path,
            "file_path_2": self.file_path_2,
            "selected_motif": self.last_selected_motif,
            "analysis_results": self.last_results,
            "statistics_dataframe": (
                self.last_statistics_df.to_dict(orient="records")
                if self.last_statistics_df is not None else []
            ),
            "comparison_results": (
                self.last_comparison_df.to_dict(orient="records")
                if self.last_comparison_df is not None else []
            ),
        }

        return session_data

    def export_json(self):
        if (
            not self.last_results and
            self.last_statistics_df is None and
            self.last_comparison_df is None
        ):
            self._set_status("JSON export failed")
            messagebox.showerror("Error", "No analysis session available for export.")
            return

        output_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )

        if not output_path:
            self._set_status("Ready")
            return

        try:
            self._set_status("Exporting JSON session...")
            session_data = self._build_session_data()
            export_session_to_json(session_data, output_path)
            self._set_status("JSON session exported")
            messagebox.showinfo("Success", f"JSON session exported to:\n{output_path}")
        except Exception as e:
            self._set_status("JSON export failed")
            messagebox.showerror("Error", f"Failed to export JSON: {e}")

    def export_csv(self):
        if self.last_statistics_df is None and self.last_comparison_df is None:
            self._set_status("CSV export failed")
            messagebox.showerror("Error", "No analysis results available for export.")
            return

        output_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )

        if not output_path:
            self._set_status("Ready")
            return

        try:
            self._set_status("Exporting CSV...")
            if self.last_comparison_df is not None:
                export_results_to_csv(self.last_comparison_df, output_path)
            else:
                export_results_to_csv(self.last_statistics_df, output_path)

            self._set_status("CSV exported")
            messagebox.showinfo("Success", f"CSV exported to:\n{output_path}")
        except Exception as e:
            self._set_status("CSV export failed")
            messagebox.showerror("Error", f"Failed to export CSV: {e}")

    def show_plot(self):
        try:
            self._set_status("Generating distribution plot...")
            self._prepare_selected_motif_statistics()
            fig = create_motif_distribution_figure(
                self.last_statistics_df,
                self.last_selected_motif
            )
            self._show_figure_window("Distribution Plot", fig)
            self._set_status("Distribution plot generated")
        except Exception as e:
            self._set_status("Failed to generate plot")
            messagebox.showerror("Error", f"Failed to generate plot: {e}")

    def show_multi_motif_plot(self):
        if not self.last_results:
            self._set_status("No motif analysis results available")
            messagebox.showerror("Error", "No motif analysis results available.")
            return

        try:
            self._set_status("Generating multi-motif summary plot...")
            fig = create_multiple_motifs_summary_figure(self.last_results)
            self._show_figure_window("Multi-Motif Summary", fig)
            self._set_status("Multi-motif summary plot generated")
        except Exception as e:
            self._set_status("Failed to generate multi-motif plot")
            messagebox.showerror("Error", f"Failed to generate multi-motif plot: {e}")

    def show_positions_plot(self):
        if not self.last_results or not self.sequence:
            self._set_status("No motif analysis results available")
            messagebox.showerror("Error", "No motif analysis results available.")
            return

        try:
            self._set_status("Generating motif positions plot...")
            fig = create_motif_positions_figure(self.last_results, len(self.sequence))
            self._show_figure_window("Motif Positions", fig)
            self._set_status("Motif positions plot generated")
        except Exception as e:
            self._set_status("Failed to generate motif position plot")
            messagebox.showerror("Error", f"Failed to generate motif position plot: {e}")

    def _get_motif_colors(self):
        palette = [
            "#fff59d",  # jasny żółty
            "#a5d6a7",  # jasny zielony
            "#90caf9",  # jasny niebieski
            "#ffab91",  # jasny pomarańczowy
            "#ce93d8",  # jasny fiolet
            "#80deea",  # turkus
            "#f48fb1",  # róż
            "#c5e1a5",  # oliwkowy
        ]

        return {
            result["motif"]: palette[index % len(palette)]
            for index, result in enumerate(self.last_results)
        }

    def _insert_sequence_with_line_breaks(self, text_widget, sequence, line_length=80):
        for i in range(0, len(sequence), line_length):
            chunk = sequence[i:i + line_length]
            text_widget.insert(tk.END, chunk + "\n")

    def _highlight_motif_occurrences(self, text_widget, sequence, line_length=80):
        motif_colors = self._get_motif_colors()

        for result in self.last_results:
            motif = result["motif"]
            positions = result["positions"]
            color = motif_colors[motif]

            tag_name = f"motif_{motif}"
            text_widget.tag_config(tag_name, background=color)

            motif_length = len(motif)

            for pos in positions:
                start_row = pos // line_length + 1
                start_col = pos % line_length
                remaining = motif_length
                current_pos = pos

                while remaining > 0:
                    row = current_pos // line_length + 1
                    col = current_pos % line_length
                    available_in_line = line_length - col
                    chars_in_this_line = min(remaining, available_in_line)

                    start_index = f"{row}.{col}"
                    end_index = f"{row}.{col + chars_in_this_line}"

                    text_widget.tag_add(tag_name, start_index, end_index)

                    current_pos += chars_in_this_line
                    remaining -= chars_in_this_line

    def show_highlighted_sequence(self):
        if not self.last_results or not self.sequence:
            self._set_status("No analysis results available")
            messagebox.showerror("Error", "No motif analysis results available.")
            return

        try:
            self._set_status("Generating highlighted sequence view...")

            sequence_window = tk.Toplevel(self.root)
            sequence_window.title("Highlighted DNA Sequence")
            sequence_window.geometry("1100x700")
            sequence_window.resizable(True, True)

            top_frame = tk.Frame(sequence_window)
            top_frame.pack(fill="x", padx=10, pady=10)

            info_label = tk.Label(
                top_frame,
                text=(
                    f"Sequence length: {len(self.sequence)} | "
                    f"Motifs: {', '.join([result['motif'] for result in self.last_results])}"
                ),
                font=("Arial", 10, "bold"),
                anchor="w",
                justify="left"
            )
            info_label.pack(fill="x")

            legend_frame = tk.Frame(sequence_window)
            legend_frame.pack(fill="x", padx=10, pady=(0, 10))

            motif_colors = self._get_motif_colors()
            for motif, color in motif_colors.items():
                legend_item = tk.Label(
                    legend_frame,
                    text=f" {motif} ",
                    bg=color,
                    relief="solid",
                    borderwidth=1,
                    padx=5,
                    pady=2
                )
                legend_item.pack(side="left", padx=5)

            text_frame = tk.Frame(sequence_window)
            text_frame.pack(fill="both", expand=True, padx=10, pady=10)

            scrollbar_y = tk.Scrollbar(text_frame, orient="vertical")
            scrollbar_y.pack(side="right", fill="y")

            scrollbar_x = tk.Scrollbar(text_frame, orient="horizontal")
            scrollbar_x.pack(side="bottom", fill="x")

            text_widget = tk.Text(
                text_frame,
                wrap="none",
                font=("Courier New", 11),
                yscrollcommand=scrollbar_y.set,
                xscrollcommand=scrollbar_x.set
            )
            text_widget.pack(side="left", fill="both", expand=True)

            scrollbar_y.config(command=text_widget.yview)
            scrollbar_x.config(command=text_widget.xview)

            self._insert_sequence_with_line_breaks(text_widget, self.sequence, line_length=80)
            self._highlight_motif_occurrences(text_widget, self.sequence, line_length=80)

            text_widget.config(state="disabled")

            self._set_status("Highlighted sequence view generated")

        except Exception as e:
            self._set_status("Failed to generate highlighted sequence view")
            messagebox.showerror("Error", f"Failed to generate highlighted sequence view: {e}")

    def show_interactive_positions_plot(self):
        if not self.last_results or not self.sequence:
            self._set_status("No motif analysis results available")
            messagebox.showerror("Error", "No motif analysis results available.")
            return

        try:
            self._set_status("Generating interactive motif plot...")
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

            self._set_status("Interactive motif plot generated")
        except Exception as e:
            self._set_status("Failed to generate interactive plot")
            messagebox.showerror("Error", f"Failed to generate interactive plot: {e}")

    def save_plot(self):
        output_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")]
        )

        if not output_path:
            self._set_status("Ready")
            return

        try:
            self._set_status("Saving plot as PNG...")
            self._prepare_selected_motif_statistics()
            plot_motif_distribution(
                self.last_statistics_df,
                self.last_selected_motif,
                output_path=output_path,
                show_plot=False
            )
            self._set_status("Plot saved as PNG")
            messagebox.showinfo("Success", f"Plot saved to:\n{output_path}")
        except Exception as e:
            self._set_status("Failed to save plot")
            messagebox.showerror("Error", f"Failed to save plot: {e}")

    def export_pdf(self):
        output_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )

        if not output_path:
            self._set_status("Ready")
            return

        try:
            self._set_status("Generating PDF...")
            self._prepare_selected_motif_statistics()
            export_report_to_pdf(
                self.last_statistics_df,
                self.last_selected_motif,
                len(self.sequence),
                output_path
            )
            self._set_status("PDF exported")
            messagebox.showinfo("Success", f"PDF report exported to:\n{output_path}")
        except Exception as e:
            self._set_status("PDF export failed")
            messagebox.showerror("Error", f"Failed to export PDF: {e}")

    def show_analysis_history(self):
        history_path = "results/analysis_history.csv"
        self._update_action_buttons_state()

        if not os.path.exists(history_path):
            self._set_status("No analysis history available")
            messagebox.showinfo("History", "No analysis history available yet.")
            return

        try:
            self._set_status("Opening analysis history...")
            history_df = pd.read_csv(history_path)
            history_text = history_df.to_string(index=False)
            self._display_results(
                "Analysis History",
                history_text,
                dataframe=history_df
            )
            self._set_status("Analysis history opened")
        except Exception as e:
            self._set_status("Failed to open analysis history")
            messagebox.showerror("Error", f"Failed to open history: {e}")

    def _set_status(self, text):
        self.status_var.set(text)
        self.root.update_idletasks()