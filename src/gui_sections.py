import tkinter as tk
from tkinter import ttk


def build_main_layout(app):
    app.main_canvas = tk.Canvas(app.root)
    app.main_scrollbar = tk.Scrollbar(
        app.root,
        orient="vertical",
        command=app.main_canvas.yview
    )

    app.scrollable_frame = tk.Frame(app.main_canvas)

    app.scrollable_frame.bind(
        "<Configure>",
        lambda e: app.main_canvas.configure(
            scrollregion=app.main_canvas.bbox("all")
        ),
    )

    app.main_canvas.create_window((0, 0), window=app.scrollable_frame, anchor="nw")
    app.main_canvas.configure(yscrollcommand=app.main_scrollbar.set)

    app.main_canvas.pack(side="left", fill="both", expand=True)
    app.main_scrollbar.pack(side="right", fill="y")

    app.root.grid_rowconfigure(0, weight=1)
    app.root.grid_columnconfigure(0, weight=1)


def build_title(app):
    app.title_label = tk.Label(
        app.scrollable_frame,
        text="DNA Motif Analyzer",
        font=("Arial", 18, "bold")
    )
    app.title_label.pack(pady=10)


def build_files_frame(app):
    app.files_frame = tk.LabelFrame(
        app.scrollable_frame,
        text="Sequence files",
        padx=10,
        pady=10
    )
    app.files_frame.pack(fill="x", padx=15, pady=5)

    app.file_button = tk.Button(
        app.files_frame,
        text="Choose first sequence file",
        command=lambda: app.choose_file(1),
        width=25
    )
    app.file_button.pack(pady=3)

    app.file_label = tk.Label(app.files_frame, text="No first file selected")
    app.file_label.pack(pady=3)

    app.file_button_2 = tk.Button(
        app.files_frame,
        text="Choose second sequence file",
        command=lambda: app.choose_file(2),
        width=25
    )
    app.file_button_2.pack(pady=3)

    app.file_label_2 = tk.Label(app.files_frame, text="No second file selected")
    app.file_label_2.pack(pady=3)


def build_ncbi_frame(app):
    app.ncbi_frame = tk.LabelFrame(
        app.scrollable_frame,
        text="NCBI download",
        padx=10,
        pady=10
    )
    app.ncbi_frame.pack(fill="x", padx=15, pady=5)

    app.ncbi_label = tk.Label(app.ncbi_frame, text="First NCBI accession ID:")
    app.ncbi_label.pack(pady=3)

    app.ncbi_entry = tk.Entry(app.ncbi_frame, width=35)
    app.ncbi_entry.pack(pady=3)

    app.ncbi_label_2 = tk.Label(app.ncbi_frame, text="Second NCBI accession ID:")
    app.ncbi_label_2.pack(pady=3)

    app.ncbi_entry_2 = tk.Entry(app.ncbi_frame, width=35)
    app.ncbi_entry_2.pack(pady=3)

    app.email_label = tk.Label(app.ncbi_frame, text="Email for NCBI:")
    app.email_label.pack(pady=3)

    app.email_entry = tk.Entry(app.ncbi_frame, width=35)
    app.email_entry.pack(pady=3)

    app.fetch_button = tk.Button(
        app.ncbi_frame,
        text="Fetch first from NCBI",
        command=lambda: app.fetch_from_ncbi(1),
        width=25
    )
    app.fetch_button.pack(pady=3)

    app.fetch_button_2 = tk.Button(
        app.ncbi_frame,
        text="Fetch second from NCBI",
        command=lambda: app.fetch_from_ncbi(2),
        width=25
    )
    app.fetch_button_2.pack(pady=3)

    app.example_button = tk.Button(
        app.ncbi_frame,
        text="Load Example (Human Hemoglobin)",
        command=lambda: app.load_example_ncbi(
            target=1,
            accession_id="NM_000518",
            description="Human Hemoglobin"
        ),
        width=30
    )
    app.example_button.pack(pady=3)

    app.example_button_2 = tk.Button(
        app.ncbi_frame,
        text="Load Example (Mitochondrial DNA)",
        command=lambda: app.load_example_ncbi(
            target=2,
            accession_id="NC_012920",
            description="Mitochondrial DNA"
        ),
        width=30
    )
    app.example_button_2.pack(pady=3)


def build_analysis_frame(app):
    app.analysis_frame = tk.LabelFrame(
        app.scrollable_frame,
        text="Analysis settings",
        padx=10,
        pady=10
    )
    app.analysis_frame.pack(fill="x", padx=15, pady=5)

    app.motif_label = tk.Label(
        app.analysis_frame,
        text="Enter motifs separated by commas:"
    )
    app.motif_label.pack(pady=3)

    app.motif_entry = tk.Entry(app.analysis_frame, width=45)
    app.motif_entry.pack(pady=3)

    app.selected_motif_label = tk.Label(
        app.analysis_frame,
        text="Select motif for plot/PDF:"
    )
    app.selected_motif_label.pack(pady=3)

    app.selected_motif_var = tk.StringVar()
    app.selected_motif_combobox = ttk.Combobox(
        app.analysis_frame,
        textvariable=app.selected_motif_var,
        state="readonly",
        width=25
    )
    app.selected_motif_combobox.pack(pady=3)

    app.segment_label = tk.Label(app.analysis_frame, text="Segment length:")
    app.segment_label.pack(pady=3)

    app.segment_entry = tk.Entry(app.analysis_frame, width=10)
    app.segment_entry.insert(0, "10")
    app.segment_entry.pack(pady=3)


def build_actions_frame(app):
    app.actions_frame = tk.LabelFrame(
        app.scrollable_frame,
        text="Actions",
        padx=10,
        pady=10
    )
    app.actions_frame.pack(fill="x", padx=15, pady=5)

    app.analyze_button = tk.Button(
        app.actions_frame,
        text="Analyze",
        command=app.run_analysis,
        width=25
    )
    app.analyze_button.pack(pady=3)

    app.compare_button = tk.Button(
        app.actions_frame,
        text="Compare Sequences",
        command=app.run_comparison,
        width=25
    )
    app.compare_button.pack(pady=3)

    app.export_csv_button = tk.Button(
        app.actions_frame,
        text="Export CSV",
        command=app.export_csv,
        width=25
    )
    app.export_csv_button.pack(pady=3)

    app.show_plot_button = tk.Button(
        app.actions_frame,
        text="Show Distribution Plot",
        command=app.show_plot,
        width=25
    )
    app.show_plot_button.pack(pady=3)

    app.show_multi_plot_button = tk.Button(
        app.actions_frame,
        text="Show Multi-Motif Summary",
        command=app.show_multi_motif_plot,
        width=25
    )
    app.show_multi_plot_button.pack(pady=3)

    app.show_positions_button = tk.Button(
        app.actions_frame,
        text="Show Motif Positions",
        command=app.show_positions_plot,
        width=25
    )
    app.show_positions_button.pack(pady=3)

    app.show_interactive_button = tk.Button(
        app.actions_frame,
        text="Open Interactive Motif Plot",
        command=app.show_interactive_positions_plot,
        width=25
    )
    app.show_interactive_button.pack(pady=3)

    app.save_plot_button = tk.Button(
        app.actions_frame,
        text="Save Plot as PNG",
        command=app.save_plot,
        width=25
    )
    app.save_plot_button.pack(pady=3)

    app.export_pdf_button = tk.Button(
        app.actions_frame,
        text="Export PDF",
        command=app.export_pdf,
        width=25
    )
    app.export_pdf_button.pack(pady=3)

    app.show_history_button = tk.Button(
        app.actions_frame,
        text="Show Analysis History",
        command=app.show_analysis_history,
        width=25
    )
    app.show_history_button.pack(pady=3)


def build_results_frame(app):
    app.result_frame = tk.Frame(app.scrollable_frame)
    app.result_frame.pack(fill="both", expand=True, padx=15, pady=10)

    app.result_scrollbar = tk.Scrollbar(app.result_frame)
    app.result_scrollbar.pack(side="right", fill="y")

    app.result_text = tk.Text(
        app.result_frame,
        height=8,
        width=110,
        yscrollcommand=app.result_scrollbar.set
    )
    app.result_text.pack(side="left", fill="both", expand=True)

    app.result_scrollbar.config(command=app.result_text.yview)