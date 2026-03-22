import os
import tkinter as tk
import webbrowser
from tkinter import ttk


def create_progress_dialog(root, title="Please wait", message="Operation in progress..."):
    progress_window = tk.Toplevel(root)
    progress_window.title(title)
    progress_window.geometry("350x120")
    progress_window.resizable(False, False)
    progress_window.transient(root)
    progress_window.grab_set()

    label = ttk.Label(progress_window, text=message, anchor="center")
    label.pack(pady=(20, 10), padx=20)

    progress_bar = ttk.Progressbar(
        progress_window,
        mode="indeterminate",
        length=280
    )
    progress_bar.pack(pady=10, padx=20)
    progress_bar.start(10)

    progress_window.protocol("WM_DELETE_WINDOW", lambda: None)

    return progress_window, progress_bar


def close_progress_dialog(progress_window, progress_bar):
    if progress_bar is not None:
        try:
            progress_bar.stop()
        except Exception:
            pass

    if progress_window is not None:
        try:
            progress_window.grab_release()
        except Exception:
            pass
        progress_window.destroy()


def insert_sequence_with_line_breaks(text_widget, sequence, line_length=80):
    for i in range(0, len(sequence), line_length):
        chunk = sequence[i:i + line_length]
        text_widget.insert(tk.END, chunk + "\n")


def highlight_motif_occurrences(text_widget, results, motif_colors, line_length=80):
    for result in results:
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


def open_highlighted_sequence_window(root, sequence, sequence_label, results, motif_colors):
    sequence_window = tk.Toplevel(root)
    sequence_window.title(f"Highlighted DNA Sequence - {sequence_label}")
    sequence_window.geometry("1100x700")
    sequence_window.resizable(True, True)

    top_frame = tk.Frame(sequence_window)
    top_frame.pack(fill="x", padx=10, pady=10)

    info_label = tk.Label(
        top_frame,
        text=(
            f"{sequence_label} | "
            f"Sequence length: {len(sequence)} | "
            f"Motifs: {', '.join([result['motif'] for result in results])}"
        ),
        font=("Arial", 10, "bold"),
        anchor="w",
        justify="left"
    )
    info_label.pack(fill="x")

    legend_frame = tk.Frame(sequence_window)
    legend_frame.pack(fill="x", padx=10, pady=(0, 10))

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

    insert_sequence_with_line_breaks(text_widget, sequence, line_length=80)
    highlight_motif_occurrences(text_widget, results, motif_colors, line_length=80)

    text_widget.config(state="disabled")

    return sequence_window


def open_interactive_plot_info_window(root, output_html):
    absolute_html_path = os.path.abspath(output_html)
    file_url = f"file:///{absolute_html_path.replace(os.sep, '/')}"

    info_window = tk.Toplevel(root)
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

    return info_window