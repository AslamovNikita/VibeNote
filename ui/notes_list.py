import tkinter as tk
from tkinter import ttk
from utils.config import BG_COLOR, CARD_DEFAULT_COLOR, BUTTON_ADD_COLOR


class NotesListView:
    def __init__(self, parent, notes, on_note_selected_callback=None):
        self.notes = notes
        self.on_note_selected = on_note_selected_callback
        self.parent = parent

        self.frame = ttk.Frame(parent, style="Brown.TFrame")
        self.frame.pack(fill="both", expand=True)

        self.build_ui()
        self.refresh_list()

        self.frame.bind("<Configure>", lambda e: self.refresh_list())

    def build_ui(self):
        # чёрный заголовок
        header = tk.Frame(self.frame, bg="#000000")
        header.pack(fill="x", pady=0)

        tk.Label(
            header,
            text="📝 Список всех заметок",
            bg="#000000",
            fg="white",
            font=("Arial", 16, "bold")
        ).pack(side="left", padx=20, pady=10)

        # контейнер списка тёмно песочный
        list_container = tk.Frame(self.frame, bg="#3E362E")
        list_container.pack(fill="both", expand=True, padx=5, pady=5)

        # холст и скролл
        self.canvas = tk.Canvas(list_container, bg="#3E362E", highlightthickness=0)
        scrollbar = tk.Scrollbar(list_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#3E362E")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.canvas.bind("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def refresh_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.scrollable_frame.update_idletasks()
        container_width = self.scrollable_frame.winfo_width()

        from utils.date_utils import get_time_left

        text_column_width = container_width - 400
        if text_column_width < 200:
            text_column_width = 200

        # заголовок таблицы  чёрный
        header_frame = tk.Frame(self.scrollable_frame, bg="#000000")
        header_frame.pack(fill="x", pady=(0, 5))

        tk.Label(header_frame, text="#", width=5, bg="#000000", fg="white", font=("Arial", 10, "bold")).pack(
            side="left", padx=5, pady=8)
        tk.Label(header_frame, text="Текст заметки", bg="#000000", fg="white", font=("Arial", 10, "bold"),
                 anchor="w").pack(side="left", padx=5, pady=8, fill="x", expand=True)
        tk.Label(header_frame, text="Дедлайн", width=15, bg="#000000", fg="white",
                 font=("Arial", 10, "bold")).pack(side="left", padx=5, pady=8)
        tk.Label(header_frame, text="Статус", width=12, bg="#000000", fg="white",
                 font=("Arial", 10, "bold")).pack(side="left", padx=5, pady=8)

        # строки таблицы  тёмно песочный фон
        for idx, note in enumerate(self.notes):
            row_bg = "#4A4036" if idx % 2 == 0 else "#3E362E"  # чередование оттенков

            row = tk.Frame(self.scrollable_frame, bg=row_bg, cursor="hand2")
            row.pack(fill="x", pady=1)

            tk.Label(row, text=str(idx + 1), width=5, bg=row_bg, fg="white", font=("Arial", 10)).pack(
                side="left", padx=5, pady=10)

            text = note.get("text", "")
            text_label = tk.Label(
                row,
                text=text,
                bg=row_bg,
                fg="white",
                font=("Arial", 10),
                anchor="nw",
                justify="left",
                wraplength=text_column_width
            )
            text_label.pack(side="left", padx=5, pady=10, fill="both", expand=True)

            deadline = note.get("deadline", "без срока")
            tk.Label(row, text=deadline, width=15, bg=row_bg, fg="#ccc", font=("Arial", 10), anchor="w").pack(
                side="left", padx=5, pady=10)

            time_left = get_time_left(deadline)
            if "просрочено" in time_left:
                status_color = "#e74c3c"
            elif "д" in time_left:
                status_color = "#f39c12"
            else:
                status_color = "#2ecc71"

            tk.Label(row, text=time_left, width=12, bg=row_bg, fg=status_color, font=("Arial", 10, "bold")).pack(
                side="left", padx=5, pady=10)

            def on_click(e, note_idx=idx):
                if self.on_note_selected:
                    self.on_note_selected(note_idx, self.notes[note_idx])

            row.bind("<Button-1>", on_click)
            for child in row.winfo_children():
                child.bind("<Button-1>", on_click)


def add_notes_list_tab(notebook, notes, on_note_selected_callback=None):
    notes_frame = ttk.Frame(notebook)
    notebook.add(notes_frame, text="📝 Список", padding=(5, 5, 5, 5))
    notes_view = NotesListView(notes_frame, notes, on_note_selected_callback)
    return notes_view