import os
import threading
import webbrowser

import pandas as pd
import tkinter as tk
from tkinter import ttk

from src.export_utils import (
    create_gc_comparison_figure,
    create_gc_content_figure,
    create_gc_motif_overlay_figure,
    create_motif_distribution_figure,
    create_motif_positions_figure,
    create_multiple_motifs_summary_figure,
    interactive_motif_positions,
    save_analysis_history,
)
from src.gui_sections import (
    build_actions_frame,
    build_analysis_frame,
    build_files_frame,
    build_main_layout,
    build_ncbi_frame,
    build_results_frame,
    build_status_bar,
    build_title,
)
from src.io_utils import load_sequence_from_fasta, load_sequence_from_txt
from src.ncbi_utils import fetch_sequence_from_ncbi
from src.validation_utils import (
    get_sequence_warning,
    normalize_motifs,
    validate_motifs_against_sequence,
)

from src.report_utils import (
    build_session_data,
    format_analysis_results_for_sequence,
    format_comparison_results,
)

from src.history_utils import (
    build_analysis_history_entry,
    build_comparison_history_entry,
)

from src.analysis_service import (
    build_extended_sequence_statistics,
    build_motif_statistics,
    run_sequence_analysis,
    run_sequence_comparison,
)

from src.export_service import (
    export_analysis_or_comparison_csv,
    export_analysis_or_comparison_pdf,
    export_distribution_plot_png,
    export_positions_plot_png,
    export_session_json,
)

from src.gui_helpers import (
    ask_open_sequence_filename,
    ask_save_as_filename,
    get_default_empty_file_label,
    open_figure_window,
    show_error,
    show_info,
    show_warning,
)

from src.constants import ANALYSIS_HISTORY_PATH, INTERACTIVE_PLOT_PATH, RESULTS_DIR

from src.app_state import build_sequences_state

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("DNA Motif Analyzer")
        self.root.geometry("1000x900")
        self.root.resizable(True, True)

        self.sequences_state = build_sequences_state()

        self.file_path = None
        self.file_path_2 = None
        self.sequence = ""
        self.sequence_2 = ""

        self.last_results = []
        self.last_statistics_df = None
        self.last_selected_motif = None
        self.last_comparison_df = None

        self.last_analyzed_sequence = ""
        self.last_analyzed_sequence_label = ""

        self.current_theme = "light"

        self.progress_window = None
        self.progress_bar = None

        build_main_layout(self)
        build_title(self)
        build_files_frame(self)
        build_ncbi_frame(self)
        build_analysis_frame(self)
        build_actions_frame(self)
        build_results_frame(self)
        build_status_bar(self)

        self.result_tree.bind("<Configure>", self._resize_result_columns)
        self.result_notebook.bind("<<NotebookTabChanged>>", self._on_result_tab_changed)

        self._configure_styles()
        self._update_action_buttons_state()

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        if self.current_theme == "dark":
            bg = "#22252b"
            fg = "#f1f1f1"
            field_bg = "#2d3138"
            text_bg = "#1e2127"
            text_fg = "#f1f1f1"
        else:
            bg = "#f4f6f8"
            fg = "#1f1f1f"
            field_bg = "#ffffff"
            text_bg = "#ffffff"
            text_fg = "#1f1f1f"

        self.root.configure(bg=bg)

        style.configure(".", background=bg, foreground=fg)
        style.configure("TFrame", background=bg)
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure("TLabelFrame", background=bg, foreground=fg)
        style.configure("TLabelFrame.Label", background=bg, foreground=fg)
        style.configure("TButton", padding=6)
        style.configure("TEntry", fieldbackground=field_bg)
        style.configure("TCombobox", fieldbackground=field_bg)
        style.configure("Treeview", background=field_bg, fieldbackground=field_bg, foreground=fg)
        style.configure("Treeview.Heading", padding=6)
        style.configure("TNotebook", background=bg)
        style.configure("TNotebook.Tab", padding=(10, 5))

        try:
            self.result_text.configure(
                bg=text_bg,
                fg=text_fg,
                insertbackground=text_fg
            )
        except Exception:
            pass

        try:
            self.main_canvas.configure(bg=bg, highlightthickness=0)
        except Exception:
            pass

    def _resize_result_columns(self, event=None):
        columns = self.result_tree["columns"]
        if not columns:
            return

        self.root.update_idletasks()

        total_width = self.result_tree.winfo_width()
        if total_width <= 100:
            return

        usable_width = total_width - 4
        column_width = max(100, usable_width // len(columns))

        for column in columns:
            self.result_tree.column(
                column,
                width=column_width,
                minwidth=100,
                stretch=True
            )

    def _on_result_tab_changed(self, event=None):
        self.root.after(50, self._resize_result_columns)
        self.root.after(150, self._resize_result_columns)
        self.root.after(300, self._resize_result_columns)

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self._configure_styles()

        self.root.after(50, self._resize_result_columns)
        self.root.after(150, self._resize_result_columns)
        self.root.after(300, self._resize_result_columns)

        self._set_status("Ready")

    def _update_action_buttons_state(self):
        has_sequence_1 = bool(self.sequence)
        has_sequence_2 = bool(self.sequence_2)
        has_analysis_results = bool(self.last_results)
        has_statistics = self.last_statistics_df is not None
        has_comparison = self.last_comparison_df is not None
        has_any_export_data = has_statistics or has_comparison

        self.analyze_button.config(state="normal" if has_sequence_1 else "disabled")
        self.analyze_button_2.config(state="normal" if has_sequence_2 else "disabled")
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
        self.save_positions_plot_button.config(
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
            state="normal" if has_analysis_results or has_comparison else "disabled"
        )
        self.show_history_button.config(
            state="normal" if os.path.exists(ANALYSIS_HISTORY_PATH) else "disabled"
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
        slot = self._get_sequence_slot(target)
        slot.sequence = sequence
        slot.source_label = source_label

        if target == 1:
            self.sequence = sequence
        elif target == 2:
            self.sequence_2 = sequence
        else:
            raise ValueError("Target must be 1 or 2.")

        label_widget = self._get_sequence_label_widget_by_target(target)
        label_widget.config(text=source_label)

    def _get_sequence_by_target(self, target):
        slot = self._get_sequence_slot(target)
        return slot.sequence

    def _get_sequence_length_by_target(self, target):
        return len(self._get_sequence_by_target(target))

    def _get_ncbi_entry_by_target(self, target):
        if target == 1:
            return self.ncbi_entry
        if target == 2:
            return self.ncbi_entry_2
        raise ValueError("Target must be 1 or 2.")

    def _get_file_path_by_target(self, target):
        slot = self._get_sequence_slot(target)
        return slot.file_path

    def _set_file_path_by_target(self, target, path):
        slot = self._get_sequence_slot(target)
        slot.file_path = path

        if target == 1:
            self.file_path = path
        elif target == 2:
            self.file_path_2 = path
        else:
            raise ValueError("Target must be 1 or 2.")

    def _get_sequence_label_widget_by_target(self, target):
        if target == 1:
            return self.file_label
        if target == 2:
            return self.file_label_2
        raise ValueError("Target must be 1 or 2.")

    def _get_target_display_name(self, target):
        if target == 1:
            return "First sequence"
        if target == 2:
            return "Second sequence"
        raise ValueError("Target must be 1 or 2.")

    def _clear_sequence_slot(self, target):
        slot = self._get_sequence_slot(target)
        slot.sequence = ""
        slot.file_path = None
        slot.source_label = get_default_empty_file_label(target)

        if target == 1:
            self.sequence = ""
            self.file_path = None
        elif target == 2:
            self.sequence_2 = ""
            self.file_path_2 = None
        else:
            raise ValueError("Target must be 1 or 2.")

        label_widget = self._get_sequence_label_widget_by_target(target)
        label_widget.config(text=slot.source_label)

    def _clear_single_analysis_state(self):
        self.last_results = []
        self.last_statistics_df = None
        self.last_selected_motif = None
        self.last_analyzed_sequence = ""
        self.last_analyzed_sequence_label = ""
        self.selected_motif_combobox["values"] = []
        self.selected_motif_combobox.set("")

    def _clear_comparison_state(self):
        self.last_comparison_df = None

    def _show_sequence_warning_if_needed(self, sequence):
        warning_message = get_sequence_warning(sequence)
        if warning_message:
            show_warning("Sequence Warning", warning_message)

    def _validate_analysis_inputs(self, motifs, sequence):
        validate_motifs_against_sequence(motifs, sequence)

    def _set_ncbi_buttons_state(self, state):
        self.fetch_button.config(state=state)
        self.fetch_button_2.config(state=state)
        self.example_button.config(state=state)
        self.example_button_2.config(state=state)

    def _show_progress_dialog(self, title="Please wait", message="Operation in progress..."):
        if self.progress_window is not None:
            return

        self.progress_window = tk.Toplevel(self.root)
        self.progress_window.title(title)
        self.progress_window.geometry("350x120")
        self.progress_window.resizable(False, False)
        self.progress_window.transient(self.root)
        self.progress_window.grab_set()

        label = ttk.Label(self.progress_window, text=message, anchor="center")
        label.pack(pady=(20, 10), padx=20)

        self.progress_bar = ttk.Progressbar(
            self.progress_window,
            mode="indeterminate",
            length=280
        )
        self.progress_bar.pack(pady=10, padx=20)
        self.progress_bar.start(10)

        self.progress_window.protocol("WM_DELETE_WINDOW", lambda: None)

    def _close_progress_dialog(self):
        if self.progress_bar is not None:
            try:
                self.progress_bar.stop()
            except Exception:
                pass
            self.progress_bar = None

        if self.progress_window is not None:
            try:
                self.progress_window.grab_release()
            except Exception:
                pass
            self.progress_window.destroy()
            self.progress_window = None

    def _handle_ncbi_success(self, target, accession_id, sequence, description=None, is_example=False):
        self._close_progress_dialog()
        self._show_sequence_warning_if_needed(sequence)

        target_name = self._get_target_display_name(target)

        if is_example:
            self._set_sequence_data(target, sequence, f"Loaded example from NCBI: {accession_id}")
            show_info(
                "Success",
                f"Example sequence loaded successfully.\n"
                f"Description: {description}\n"
                f"Accession: {accession_id}\n"
                f"Length: {len(sequence)}"
            )
        else:
            self._set_sequence_data(target, sequence, f"Loaded from NCBI: {accession_id}")
            success_message = f"{target_name} downloaded from NCBI.\nLength: {len(sequence)}"
            show_info("Success", success_message)

        self._update_action_buttons_state()
        self._set_ncbi_buttons_state("normal")
        self._set_status("Sequence downloaded successfully")

    def _handle_ncbi_error(self, error_message):
        self._close_progress_dialog()
        self._set_ncbi_buttons_state("normal")
        self._update_action_buttons_state()
        self._set_status("NCBI download failed")
        show_error("Error", error_message)

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
        selected_path = ask_open_sequence_filename()

        if not selected_path:
            self._set_status("Ready")
            return

        try:
            sequence = self._load_sequence_from_path(selected_path)

            self._set_file_path_by_target(target, selected_path)
            target_name = self._get_target_display_name(target)
            success_message = f"{target_name} loaded successfully.\nLength: {len(sequence)}"

            self._set_sequence_data(target, sequence, selected_path)
            self._update_action_buttons_state()
            self._show_sequence_warning_if_needed(sequence)
            self._set_status("Sequence loaded successfully")
            show_info("Success", success_message)

        except Exception as e:
            self._clear_sequence_slot(target)
            self._set_status("Failed to load sequence")
            self._update_action_buttons_state()
            show_error("Error", f"Failed to load sequence: {e}")

    def fetch_from_ncbi(self, target):
        accession_entry = self._get_ncbi_entry_by_target(target)
        accession_id = accession_entry.get().strip()
        email = self.email_entry.get().strip()

        if not accession_id or not email:
            self._set_status("NCBI download failed")
            show_error("Error", "Please enter accession ID and email.")
            return

        self._set_status("Downloading sequence from NCBI...")
        self._set_ncbi_buttons_state("disabled")
        self._show_progress_dialog(
            title="Downloading from NCBI",
            message="Downloading sequence from NCBI. Please wait..."
        )

        thread = threading.Thread(
            target=self._fetch_from_ncbi_worker,
            args=(target, accession_id, email),
            daemon=True
        )
        thread.start()

    def load_example_ncbi(self, target, accession_id, description):
        self._set_status("Downloading example sequence from NCBI...")
        self._set_ncbi_buttons_state("disabled")
        self._show_progress_dialog(
            title="Downloading example",
            message="Downloading example sequence from NCBI. Please wait..."
        )

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
        if not self.last_analyzed_sequence:
            raise ValueError("Sequence is not loaded.")

        motif = self.selected_motif_var.get().strip()
        if not motif:
            raise ValueError("Please select a motif.")

        segment_length = self._get_segment_length()
        self.last_selected_motif = motif

        mode = self.segment_mode_var.get()

        self.last_statistics_df = build_motif_statistics(
            self.last_analyzed_sequence,
            motif,
            segment_length,
            mode=mode,
        )

    def _prepare_selected_motif_statistics(self):
        if not self.last_results or not self.last_analyzed_sequence:
            raise ValueError("No analysis results available.")

        self._refresh_statistics_for_selected_motif()

    def _show_figure_window(self, title, fig):
        open_figure_window(self.root, title, fig)

    def show_gc_plot(self):
        if self.last_statistics_df is not None:
            try:
                fig = create_gc_content_figure(self.last_statistics_df)
                self._show_figure_window("GC Content Plot", fig)
                self._set_status("GC plot generated")
            except Exception as e:
                self._set_status("Failed to generate GC plot")
                show_error("Error", f"Failed to generate GC plot: {e}")
        else:
            self._set_status("No analysis results available")
            show_error("Error", "No analysis results available.")

    def show_gc_comparison_plot(self):
        if not self.sequence or not self.sequence_2:
            self._set_status("GC comparison failed")
            show_error("Error", "Both sequences must be loaded.")
            return

        try:
            self._set_status("Generating GC comparison plot...")
            segment_length = self._get_segment_length()
            mode = self.segment_mode_var.get()

            df1 = build_motif_statistics(
                self.sequence,
                self.last_selected_motif or "ATG",
                segment_length,
                mode=mode,
            )

            df2 = build_motif_statistics(
                self.sequence_2,
                self.last_selected_motif or "ATG",
                segment_length,
                mode=mode,
            )

            fig = create_gc_comparison_figure(df1, df2)
            self._show_figure_window("GC Comparison", fig)
            self._set_status("GC comparison plot generated")

        except Exception as e:
            self._set_status("Failed to generate GC comparison")
            show_error("Error", f"Failed to generate GC comparison: {e}")

    def show_gc_motif_overlay(self):
        if not self.last_results or not self.last_analyzed_sequence:
            self._set_status("No analysis results available")
            show_error("Error", "No analysis results available.")
            return

        try:
            self._set_status("Generating GC and motif overlay plot...")
            self._prepare_selected_motif_statistics()

            fig = create_gc_motif_overlay_figure(
                self.last_statistics_df,
                self.last_results,
                len(self.last_analyzed_sequence)
            )

            self._show_figure_window("GC + Motif Overlay", fig)
            self._set_status("GC and motif overlay plot generated")

        except Exception as e:
            self._set_status("Failed to generate overlay plot")
            show_error("Error", f"Failed to generate overlay plot: {e}")

    def _build_extended_sequence_statistics_for_sequence(self, sequence, motif, segment_length, mode):
        return build_extended_sequence_statistics(
            sequence,
            motif,
            segment_length,
            mode=mode,
        )

    def _build_extended_sequence_statistics(self, motif, segment_length):
        return self._build_extended_sequence_statistics_for_sequence(
            self.last_analyzed_sequence,
            motif,
            segment_length,
            mode=self.segment_mode_var.get()
        )

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

    def _format_analysis_results_for_sequence(
        self,
        sequence,
        sequence_label,
        motifs,
        segment_length,
        results
    ):
        selected_motif = self.last_selected_motif or motifs[0]
        extended_stats = self._build_extended_sequence_statistics_for_sequence(
            sequence,
            selected_motif,
            segment_length,
            mode=self.segment_mode_var.get()
        )

        return format_analysis_results_for_sequence(
            sequence=sequence,
            sequence_label=sequence_label,
            motifs=motifs,
            segment_length=segment_length,
            results=results,
            selected_motif=selected_motif,
            statistics_df=self.last_statistics_df,
            extended_stats=extended_stats,
            segment_mode=self.segment_mode_var.get(),
        )

    def _format_comparison_results(self, motifs):
        return format_comparison_results(
            sequence_1=self.sequence,
            sequence_2=self.sequence_2,
            motifs=motifs,
            comparison_df=self.last_comparison_df,
        )


    def _save_comparison_history(self, motifs):
        history_entry = build_comparison_history_entry(
            sequence_1=self.sequence,
            sequence_2=self.sequence_2,
            motifs=motifs,
            comparison_df=self.last_comparison_df,
        )
        save_analysis_history(history_entry)

    def _save_analysis_history_for_sequence(
        self,
        sequence,
        sequence_label,
        motifs,
        segment_length,
        results
    ):
        history_entry = build_analysis_history_entry(
            sequence=sequence,
            sequence_label=sequence_label,
            motifs=motifs,
            segment_length=segment_length,
            results=results,
        )
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
            self.result_tree.column(
                column,
                width=120,
                minwidth=100,
                anchor="center",
                stretch=True
            )

        for _, row in df.iterrows():
            values = [str(value) for value in row.tolist()]
            self.result_tree.insert("", tk.END, values=values)

        self.root.after(50, self._resize_result_columns)
        self.root.after(150, self._resize_result_columns)
        self.root.after(300, self._resize_result_columns)

    def _display_results(self, content, dataframe=None):
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, content)
        self._display_dataframe_in_table(dataframe)

    def _prepare_comparison_results(self, motifs):
        self.last_comparison_df = run_sequence_comparison(
            self.sequence,
            self.sequence_2,
            motifs,
        )
        return self.last_comparison_df

    def _get_sequence_slot(self, target):
        try:
            return self.sequences_state[target]
        except KeyError as exc:
            raise ValueError("Target must be 1 or 2.") from exc

    def _run_analysis_for_sequence(self, sequence, sequence_label):
        if not sequence:
            self._set_status("Analysis failed")
            show_error("Error", f"{sequence_label} is not loaded.")
            return

        try:
            self._set_status(f"Running analysis for {sequence_label}...")
            motifs, segment_length = self._get_motifs_and_segment_length()
            self._validate_analysis_inputs(motifs, sequence)

            results = run_sequence_analysis(sequence, motifs)
            display_results = self._filter_and_sort_results(results)

            self._clear_comparison_state()

            self.last_results = results
            self.last_analyzed_sequence = sequence
            self.last_analyzed_sequence_label = sequence_label

            self.selected_motif_combobox["values"] = motifs
            self.selected_motif_combobox.set(motifs[0])

            self.last_selected_motif = motifs[0]
            self.last_statistics_df = build_motif_statistics(
                sequence,
                self.last_selected_motif,
                segment_length,
                mode=self.segment_mode_var.get(),
            )

            final_text = self._format_analysis_results_for_sequence(
                sequence,
                sequence_label,
                motifs,
                segment_length,
                display_results
            )

            self._save_analysis_history_for_sequence(
                sequence,
                sequence_label,
                motifs,
                segment_length,
                results
            )

            self._display_results(
                final_text,
                dataframe=self.last_statistics_df
            )

            self._update_action_buttons_state()
            self._set_status(f"Analysis complete for {sequence_label}")

        except Exception as e:
            self._set_status("Analysis failed")
            show_error("Error", str(e))

    def run_analysis_for_target(self, target):
        sequence = self._get_sequence_by_target(target)
        sequence_label = f"Sequence {target}"
        self._run_analysis_for_sequence(sequence, sequence_label)

    def run_analysis_sequence_1(self):
        self.run_analysis_for_target(1)

    def run_analysis_sequence_2(self):
        self.run_analysis_for_target(2)

    def run_analysis(self):
        self.run_analysis_sequence_1()

    def run_comparison(self):
        if not self.sequence:
            self._set_status("Comparison failed")
            show_error("Error", "First sequence is not loaded.")
            return

        if not self.sequence_2:
            self._set_status("Comparison failed")
            show_error("Error", "Second sequence is not loaded.")
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

            self._clear_single_analysis_state()

            final_text = self._format_comparison_results(motifs)
            self._save_comparison_history(motifs)
            self._display_results(
                final_text,
                dataframe=self.last_comparison_df
            )
            self._update_action_buttons_state()
            self._set_status("Comparison complete")

        except Exception as e:
            self._set_status("Comparison failed")
            show_error("Error", f"Comparison failed: {e}")

    def _build_session_data(self):
        return build_session_data(
            sequence_1=self.sequence,
            sequence_2=self.sequence_2,
            file_path_1=self.file_path,
            file_path_2=self.file_path_2,
            last_analyzed_sequence_label=self.last_analyzed_sequence_label,
            selected_motif=self.last_selected_motif,
            analysis_results=self.last_results,
            statistics_df=self.last_statistics_df,
            comparison_df=self.last_comparison_df,
        )

    def export_json(self):
        if (
            not self.last_results and
            self.last_statistics_df is None and
            self.last_comparison_df is None
        ):
            self._set_status("JSON export failed")
            show_error("Error", "No analysis session available for export.")
            return

        output_path = ask_save_as_filename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
        )

        if not output_path:
            self._set_status("Ready")
            return

        try:
            self._set_status("Exporting JSON session...")
            session_data = self._build_session_data()
            export_session_json(session_data, output_path)
            self._set_status("JSON session exported")
            show_info("Success", f"JSON session exported to:\n{output_path}")
        except Exception as e:
            self._set_status("JSON export failed")
            show_error("Error", f"Failed to export JSON: {e}")

    def export_csv(self):
        if self.last_statistics_df is None and self.last_comparison_df is None:
            self._set_status("CSV export failed")
            show_error("Error", "No analysis results available for export.")
            return

        output_path = ask_save_as_filename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )

        if not output_path:
            self._set_status("Ready")
            return

        try:
            self._set_status("Exporting CSV...")
            export_analysis_or_comparison_csv(
                statistics_df=self.last_statistics_df,
                comparison_df=self.last_comparison_df,
                output_path=output_path,
            )
            self._set_status("CSV exported")
            show_info("Success", f"CSV exported to:\n{output_path}")
        except Exception as e:
            self._set_status("CSV export failed")
            show_error("Error", f"Failed to export CSV: {e}")

    def show_plot(self):
        try:
            self._set_status("Generating distribution plot...")
            self._prepare_selected_motif_statistics()
            fig = create_motif_distribution_figure(
                self.last_statistics_df,
                self.last_selected_motif
            )
            self._show_figure_window(
                f"{self.last_analyzed_sequence_label} Distribution Plot",
                fig
            )
            self._set_status("Distribution plot generated")
        except Exception as e:
            self._set_status("Failed to generate plot")
            show_error("Error", f"Failed to generate plot: {e}")

    def show_multi_motif_plot(self):
        if not self.last_results:
            self._set_status("No motif analysis results available")
            show_error("Error", "No motif analysis results available.")
            return

        try:
            self._set_status("Generating multi-motif summary plot...")
            fig = create_multiple_motifs_summary_figure(self.last_results)
            self._show_figure_window("Multi-Motif Summary", fig)
            self._set_status("Multi-motif summary plot generated")
        except Exception as e:
            self._set_status("Failed to generate multi-motif plot")
            show_error("Error", f"Failed to generate multi-motif plot: {e}")

    def show_positions_plot(self):
        if not self.last_results or not self.last_analyzed_sequence:
            self._set_status("No motif analysis results available")
            show_error("Error", "No motif analysis results available.")
            return

        try:
            self._set_status("Generating motif positions plot...")
            fig = create_motif_positions_figure(self.last_results, len(self.last_analyzed_sequence))
            self._show_figure_window(
                f"{self.last_analyzed_sequence_label} Motif Positions",
                fig
            )
            self._set_status("Motif positions plot generated")
        except Exception as e:
            self._set_status("Failed to generate motif position plot")
            show_error("Error", f"Failed to generate motif position plot: {e}")

    def save_positions_plot(self):
        if not self.last_results or not self.last_analyzed_sequence:
            self._set_status("No motif analysis results available")
            show_error("Error", "No motif analysis results available.")
            return

        output_path = ask_save_as_filename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")]
        )

        if not output_path:
            self._set_status("Ready")
            return

        try:
            self._set_status("Saving motif positions plot as PNG...")
            export_positions_plot_png(
                results=self.last_results,
                sequence_length=len(self.last_analyzed_sequence),
                output_path=output_path,
            )
            self._set_status("Motif positions plot saved as PNG")
            show_info("Success", f"Plot saved to:\n{output_path}")
        except Exception as e:
            self._set_status("Failed to save positions plot")
            show_error("Error", f"Failed to save positions plot: {e}")

    def _get_motif_colors(self):
        palette = [
            "#fff59d",
            "#a5d6a7",
            "#90caf9",
            "#ffab91",
            "#ce93d8",
            "#80deea",
            "#f48fb1",
            "#c5e1a5",
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
        if not self.last_results or not self.last_analyzed_sequence:
            self._set_status("No analysis results available")
            show_error("Error", "No motif analysis results available.")
            return

        try:
            self._set_status("Generating highlighted sequence view...")

            sequence_window = tk.Toplevel(self.root)
            sequence_window.title(f"Highlighted DNA Sequence - {self.last_analyzed_sequence_label}")
            sequence_window.geometry("1100x700")
            sequence_window.resizable(True, True)

            top_frame = tk.Frame(sequence_window)
            top_frame.pack(fill="x", padx=10, pady=10)

            info_label = tk.Label(
                top_frame,
                text=(
                    f"{self.last_analyzed_sequence_label} | "
                    f"Sequence length: {len(self.last_analyzed_sequence)} | "
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

            self._insert_sequence_with_line_breaks(text_widget, self.last_analyzed_sequence, line_length=80)
            self._highlight_motif_occurrences(text_widget, self.last_analyzed_sequence, line_length=80)

            text_widget.config(state="disabled")
            self._set_status("Highlighted sequence view generated")

        except Exception as e:
            self._set_status("Failed to generate highlighted sequence view")
            show_error("Error", f"Failed to generate highlighted sequence view: {e}")

    def show_interactive_positions_plot(self):
        if not self.last_results or not self.last_analyzed_sequence:
            self._set_status("No motif analysis results available")
            show_error("Error", "No motif analysis results available.")
            return

        try:
            self._set_status("Generating interactive motif plot...")
            os.makedirs(RESULTS_DIR, exist_ok=True)

            output_html = interactive_motif_positions(
                self.last_results,
                len(self.last_analyzed_sequence)
            )

            absolute_html_path = os.path.abspath(output_html)
            file_url = f"file:///{absolute_html_path.replace(os.sep, '/')}"

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
                text=f"Saved file:\n{absolute_html_path}",
                wraplength=550,
                justify="center"
            )
            label2.pack(pady=10)

            open_button = tk.Button(
                info_window,
                text="Open in browser",
                command=lambda: webbrowser.open(file_url),
                width=20
            )
            open_button.pack(pady=10)

            self._set_status("Interactive motif plot generated")

        except Exception as e:
            self._set_status("Failed to generate interactive plot")
            show_error("Error", f"Failed to generate interactive plot: {e}")

    def save_plot(self):
        output_path = ask_save_as_filename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")]
        )

        if not output_path:
            self._set_status("Ready")
            return

        try:
            self._set_status("Saving plot as PNG...")
            self._prepare_selected_motif_statistics()
            export_distribution_plot_png(
                statistics_df=self.last_statistics_df,
                selected_motif=self.last_selected_motif,
                output_path=output_path,
            )
            self._set_status("Plot saved as PNG")
            show_info("Success", f"Plot saved to:\n{output_path}")
        except Exception as e:
            self._set_status("Failed to save plot")
            show_error("Error", f"Failed to save plot: {e}")

    def export_pdf(self):
        if self.last_comparison_df is None and (
            not self.last_results or self.last_statistics_df is None
        ):
            self._set_status("PDF export failed")
            show_error("Error", "No analysis or comparison results available.")
            return

        output_path = ask_save_as_filename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )

        if not output_path:
            self._set_status("Ready")
            return

        try:
            self._set_status("Generating PDF...")

            if self.last_comparison_df is None:
                self._prepare_selected_motif_statistics()

            export_analysis_or_comparison_pdf(
                comparison_df=self.last_comparison_df,
                analysis_results=self.last_results,
                statistics_df=self.last_statistics_df,
                selected_motif=self.last_selected_motif,
                analyzed_sequence_length=len(self.last_analyzed_sequence),
                output_path=output_path,
            )

            self._set_status("PDF exported")
            show_info("Success", f"PDF report exported to:\n{output_path}")
        except Exception as e:
            self._set_status("PDF export failed")
            show_error("Error", f"Failed to export PDF: {e}")

    def show_analysis_history(self):
        history_path = ANALYSIS_HISTORY_PATH
        self._update_action_buttons_state()

        if not os.path.exists(history_path):
            self._set_status("No analysis history available")
            show_info("History", "No analysis history available yet.")
            return

        try:
            self._set_status("Opening analysis history...")
            history_df = pd.read_csv(history_path)
            history_text = history_df.to_string(index=False)
            self._display_results(
                history_text,
                dataframe=history_df
            )
            self._set_status("Analysis history opened")
        except Exception as e:
            self._set_status("Failed to open analysis history")
            show_error("Error", f"Failed to open history: {e}")

    def _set_status(self, text):
        self.status_var.set(text)
        self.root.update_idletasks()