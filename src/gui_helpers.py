import tkinter as tk
from tkinter import filedialog, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


def show_info(title, message):
    show_info(title, message)


def show_error(title, message):
    show_error(title, message)


def show_warning(title, message):
    messagebox.showwarning(title, message)


def ask_save_as_filename(defaultextension, filetypes):
    return ask_save_as_filename(
        defaultextension=defaultextension,
        filetypes=filetypes,
    )


def open_figure_window(root, title, fig):
    plot_window = tk.Toplevel(root)
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

    return plot_window

def ask_open_sequence_filename():
    return filedialog.askopenfilename(
        filetypes=[("Sequence files", "*.txt *.fasta *.fa"), ("All files", "*.*")]
    )


def get_default_empty_file_label(target):
    if target == 1:
        return "No first file selected"
    if target == 2:
        return "No second file selected"
    raise ValueError("Target must be 1 or 2.")