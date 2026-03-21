import tkinter as tk
from tkinter import ttk


def build_main_layout(app):
    app.main_canvas = tk.Canvas(app.root)
    app.main_scrollbar = ttk.Scrollbar(
        app.root,
        orient="vertical",
        command=app.main_canvas.yview
    )

    app.scrollable_frame = ttk.Frame(app.main_canvas)

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

    app.content_frame = ttk.Frame(app.scrollable_frame)
    app.content_frame.pack(fill="both", expand=True, padx=15, pady=5)

    app.left_column = ttk.Frame(app.content_frame)
    app.left_column.pack(side="left", fill="both", expand=True, padx=(0, 8))

    app.right_column = ttk.Frame(app.content_frame)
    app.right_column.pack(side="left", fill="both", expand=True, padx=(8, 0))


def build_title(app):
    app.title_label = ttk.Label(
        app.scrollable_frame,
        text="DNA Motif Analyzer",
        font=("Arial", 18, "bold")
    )
    app.title_label.pack(pady=10)


def build_files_frame(app):
    app.files_frame = ttk.LabelFrame(
        app.left_column,
        text="Sequence files",
        padding=10
    )
    app.files_frame.pack(fill="x", padx=0, pady=5)

    app.file_button = ttk.Button(
        app.files_frame,
        text="Choose first sequence file",
        command=lambda: app.choose_file(1),
        width=28
    )
    app.file_button.pack(pady=3)

    app.file_label = ttk.Label(app.files_frame, text="No first file selected")
    app.file_label.pack(pady=3, fill="x")

    app.file_button_2 = ttk.Button(
        app.files_frame,
        text="Choose second sequence file",
        command=lambda: app.choose_file(2),
        width=28
    )
    app.file_button_2.pack(pady=3)

    app.file_label_2 = ttk.Label(app.files_frame, text="No second file selected")
    app.file_label_2.pack(pady=3, fill="x")


def build_ncbi_frame(app):
    app.ncbi_frame = ttk.LabelFrame(
        app.left_column,
        text="NCBI download",
        padding=10
    )
    app.ncbi_frame.pack(fill="x", padx=0, pady=5)

    app.ncbi_label = ttk.Label(app.ncbi_frame, text="First NCBI accession ID:")
    app.ncbi_label.pack(pady=3, anchor="w")

    app.ncbi_entry = ttk.Entry(app.ncbi_frame, width=35)
    app.ncbi_entry.pack(pady=3, fill="x")

    app.ncbi_label_2 = ttk.Label(app.ncbi_frame, text="Second NCBI accession ID:")
    app.ncbi_label_2.pack(pady=3, anchor="w")

    app.ncbi_entry_2 = ttk.Entry(app.ncbi_frame, width=35)
    app.ncbi_entry_2.pack(pady=3, fill="x")

    app.email_label = ttk.Label(app.ncbi_frame, text="Email for NCBI:")
    app.email_label.pack(pady=3, anchor="w")

    app.email_entry = ttk.Entry(app.ncbi_frame, width=35)
    app.email_entry.pack(pady=3, fill="x")

    app.fetch_button = ttk.Button(
        app.ncbi_frame,
        text="Fetch first from NCBI",
        command=lambda: app.fetch_from_ncbi(1),
        width=28
    )
    app.fetch_button.pack(pady=3)

    app.fetch_button_2 = ttk.Button(
        app.ncbi_frame,
        text="Fetch second from NCBI",
        command=lambda: app.fetch_from_ncbi(2),
        width=28
    )
    app.fetch_button_2.pack(pady=3)

    app.example_button = ttk.Button(
        app.ncbi_frame,
        text="Load Example (Human Hemoglobin)",
        command=lambda: app.load_example_ncbi(
            target=1,
            accession_id="NM_000518",
            description="Human Hemoglobin"
        ),
        width=34
    )
    app.example_button.pack(pady=3)

    app.example_button_2 = ttk.Button(
        app.ncbi_frame,
        text="Load Example (Mitochondrial DNA)",
        command=lambda: app.load_example_ncbi(
            target=2,
            accession_id="NC_012920",
            description="Mitochondrial DNA"
        ),
        width=34
    )
    app.example_button_2.pack(pady=3)


def build_analysis_frame(app):
    app.analysis_frame = ttk.LabelFrame(
        app.right_column,
        text="Analysis settings",
        padding=10
    )
    app.analysis_frame.pack(fill="x", padx=0, pady=5)

    app.motif_label = ttk.Label(
        app.analysis_frame,
        text="Enter motifs separated by commas:"
    )
    app.motif_label.pack(pady=3, anchor="w")

    app.motif_entry = ttk.Entry(app.analysis_frame, width=45)
    app.motif_entry.insert(0, "ATG, TATA, CGCG")
    app.motif_entry.pack(pady=3, fill="x")

    app.selected_motif_label = ttk.Label(
        app.analysis_frame,
        text="Select motif for plot/PDF:"
    )
    app.selected_motif_label.pack(pady=3, anchor="w")

    app.selected_motif_var = tk.StringVar()
    app.selected_motif_combobox = ttk.Combobox(
        app.analysis_frame,
        textvariable=app.selected_motif_var,
        state="readonly",
        width=25
    )
    app.selected_motif_combobox.pack(pady=3, fill="x")

    app.segment_label = ttk.Label(app.analysis_frame, text="Segment length:")
    app.segment_label.pack(pady=3, anchor="w")

    app.segment_entry = tk.Spinbox(
        app.analysis_frame,
        from_=1,
        to=10000,
        width=10
    )
    app.segment_entry.delete(0, "end")
    app.segment_entry.insert(0, "10")
    app.segment_entry.pack(pady=3, anchor="w")

    app.sort_results_var = tk.StringVar(value="original")

    app.sort_label = ttk.Label(app.analysis_frame, text="Sort results:")
    app.sort_label.pack(pady=3, anchor="w")

    app.sort_combobox = ttk.Combobox(
        app.analysis_frame,
        textvariable=app.sort_results_var,
        values=["original", "count_desc", "count_asc"],
        state="readonly",
        width=17
    )
    app.sort_combobox.pack(pady=3, fill="x")

    app.only_found_var = tk.BooleanVar(value=False)
    app.only_found_checkbox = ttk.Checkbutton(
        app.analysis_frame,
        text="Show only found motifs",
        variable=app.only_found_var
    )
    app.only_found_checkbox.pack(pady=3, anchor="w")

    app.top_n_label = ttk.Label(app.analysis_frame, text="Top N motifs (optional):")
    app.top_n_label.pack(pady=3, anchor="w")

    app.top_n_entry = ttk.Entry(app.analysis_frame, width=10)
    app.top_n_entry.pack(pady=3, anchor="w")


def build_actions_frame(app):
    app.actions_frame = ttk.LabelFrame(
        app.right_column,
        text="Actions",
        padding=10
    )
    app.actions_frame.pack(fill="x", padx=0, pady=5)

    app.analysis_actions_frame = ttk.LabelFrame(
        app.actions_frame,
        text="Analysis",
        padding=10
    )
    app.analysis_actions_frame.pack(fill="x", padx=5, pady=5)

    app.visualization_actions_frame = ttk.LabelFrame(
        app.actions_frame,
        text="Visualization",
        padding=10
    )
    app.visualization_actions_frame.pack(fill="x", padx=5, pady=5)

    app.export_actions_frame = ttk.LabelFrame(
        app.actions_frame,
        text="Export",
        padding=10
    )
    app.export_actions_frame.pack(fill="x", padx=5, pady=5)

    app.other_actions_frame = ttk.LabelFrame(
        app.actions_frame,
        text="Other",
        padding=10
    )
    app.other_actions_frame.pack(fill="x", padx=5, pady=5)

    app.analyze_button = ttk.Button(
        app.analysis_actions_frame,
        text="Analyze",
        command=app.run_analysis,
        width=28
    )
    app.analyze_button.pack(pady=3)

    app.compare_button = ttk.Button(
        app.analysis_actions_frame,
        text="Compare Sequences",
        command=app.run_comparison,
        width=28
    )
    app.compare_button.pack(pady=3)

    app.show_plot_button = ttk.Button(
        app.visualization_actions_frame,
        text="Show Distribution Plot",
        command=app.show_plot,
        width=28
    )
    app.show_plot_button.pack(pady=3)

    app.show_multi_plot_button = ttk.Button(
        app.visualization_actions_frame,
        text="Show Multi-Motif Summary",
        command=app.show_multi_motif_plot,
        width=28
    )
    app.show_multi_plot_button.pack(pady=3)

    app.show_positions_button = ttk.Button(
        app.visualization_actions_frame,
        text="Show Motif Positions",
        command=app.show_positions_plot,
        width=28
    )
    app.show_positions_button.pack(pady=3)

    app.show_highlighted_sequence_button = ttk.Button(
        app.visualization_actions_frame,
        text="Show Highlighted Sequence",
        command=app.show_highlighted_sequence,
        width=28
    )
    app.show_highlighted_sequence_button.pack(pady=3)

    app.show_interactive_button = ttk.Button(
        app.visualization_actions_frame,
        text="Open Interactive Motif Plot",
        command=app.show_interactive_positions_plot,
        width=28
    )
    app.show_interactive_button.pack(pady=3)

    app.show_gc_button = ttk.Button(
        app.visualization_actions_frame,
        text="Show GC Content Plot",
        command=app.show_gc_plot,
        width=28
    )
    app.show_gc_button.pack(pady=3)

    app.show_gc_comparison_button = ttk.Button(
        app.visualization_actions_frame,
        text="Compare GC Content",
        command=app.show_gc_comparison_plot,
        width=28
    )
    app.show_gc_comparison_button.pack(pady=3)

    app.show_gc_motif_overlay_button = ttk.Button(
        app.visualization_actions_frame,
        text="GC + Motif Overlay",
        command=app.show_gc_motif_overlay,
        width=28
    )
    app.show_gc_motif_overlay_button.pack(pady=3)

    app.export_csv_button = ttk.Button(
        app.export_actions_frame,
        text="Export CSV",
        command=app.export_csv,
        width=28
    )
    app.export_csv_button.pack(pady=3)

    app.export_json_button = ttk.Button(
        app.export_actions_frame,
        text="Export JSON",
        command=app.export_json,
        width=28
    )
    app.export_json_button.pack(pady=3)

    app.save_plot_button = ttk.Button(
        app.export_actions_frame,
        text="Save Plot as PNG",
        command=app.save_plot,
        width=28
    )
    app.save_plot_button.pack(pady=3)

    app.export_pdf_button = ttk.Button(
        app.export_actions_frame,
        text="Export PDF",
        command=app.export_pdf,
        width=28
    )
    app.export_pdf_button.pack(pady=3)

    app.show_history_button = ttk.Button(
        app.other_actions_frame,
        text="Show Analysis History",
        command=app.show_analysis_history,
        width=28
    )
    app.show_history_button.pack(pady=3)


def build_results_frame(app):
    app.result_container = ttk.LabelFrame(
        app.scrollable_frame,
        text="Results",
        padding=10
    )
    app.result_container.pack(fill="both", expand=True, padx=15, pady=10)

    app.result_frame = ttk.Frame(app.result_container)
    app.result_frame.pack(fill="both", expand=True)

    app.result_scrollbar = ttk.Scrollbar(app.result_frame)
    app.result_scrollbar.pack(side="right", fill="y")

    app.result_text = tk.Text(
        app.result_frame,
        height=12,
        width=110,
        yscrollcommand=app.result_scrollbar.set
    )
    app.result_text.pack(side="left", fill="both", expand=True)

    app.result_scrollbar.config(command=app.result_text.yview)


def build_status_bar(app):
    app.status_var = tk.StringVar()
    app.status_var.set("Ready")

    app.status_bar = ttk.Label(
        app.root,
        textvariable=app.status_var,
        anchor="w",
        padding=(8, 4)
    )
    app.status_bar.pack(side="bottom", fill="x")