import tkinter as tk
from tkinter import ttk, colorchooser
from models.note_manager import NoteManager
from ui.canvas_manager import CanvasManager
from ui.dialogs import open_add_note_dialog, open_edit_text_dialog
from utils.config import BG_COLOR, CARD_DEFAULT_COLOR, BUTTON_ADD_COLOR, WINDOW_SIZE
from ui.calendar_view import add_calendar_tab
from ui.notes_list import add_notes_list_tab
from utils.notifications import NotificationManager, check_deadlines_now

class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📝 Доска заметок")
        self.root.geometry(WINDOW_SIZE)
        self.root.configure(bg=BG_COLOR)

        self.note_manager = NoteManager()
        self.selected_index = None
        self._setup_styles()
        self._build_header()
        self._build_context_menu()

        self.refresh()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.notification_manager = NotificationManager(self.note_manager, self.root)
        self.notification_manager.start()
        check_deadlines_now(self.note_manager)

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Add.TButton", background=BUTTON_ADD_COLOR, foreground="white")

        style.configure("TNotebook", background=BG_COLOR, borderwidth=0)
        style.configure("TNotebook.Tab", background=CARD_DEFAULT_COLOR, foreground="white", padding=[15, 8])
        style.map("TNotebook.Tab", background=[("selected", BUTTON_ADD_COLOR)])

        style.configure("TFrame", background=BG_COLOR)

    def _build_header(self):

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        board_frame = ttk.Frame(self.notebook)
        self.notebook.add(board_frame, text="📋 Доска заметок")


        board_header = tk.Frame(board_frame, bg=BG_COLOR)
        board_header.pack(fill="x", pady=10)

        tk.Label(
            board_header,
            text="📋 Доска заметок",
            bg=BG_COLOR,
            fg="white",
            font=("Arial", 18, "bold")
        ).pack(side="left", padx=20)

        ttk.Button(
            board_header,
            text="➕ Добавить",
            style="Add.TButton",
            command=self.add_note_ui
        ).pack(side="right", padx=20)

        self.canvas_manager = CanvasManager(
            board_frame,
            bg_color=BG_COLOR,
            on_drag_end_callback=self.save_positions_and_notes
        )
        self.canvas_manager.canvas.pack(fill="both", expand=True, padx=10, pady=5)

        self.notes_list_view = add_notes_list_tab(
            self.notebook,
            self.note_manager.notes,
            on_note_selected_callback=self.scroll_to_note
        )

        self.calendar_view = add_calendar_tab(
            self.notebook,
            self.note_manager.notes,
            on_note_selected_callback=self.scroll_to_note
        )

    def _build_context_menu(self):
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="🎨 Цвет", command=self.change_color)
        self.menu.add_command(label="✏️ Редактировать", command=self.edit_note)
        self.menu.add_command(label="❌ Удалить", command=self.delete_note)

    def scroll_to_note(self, note_index, note):
        self.notebook.select(0)

    def add_note_ui(self):
        def on_save(text, deadline):
            self.note_manager.add(
                text=text,
                deadline=deadline,
                color=CARD_DEFAULT_COLOR,
                x=80, y=80
            )
            self.refresh()
        open_add_note_dialog(self.root, on_save)

    def refresh(self):
        self.canvas_manager.clear()
        for i, note in enumerate(self.note_manager.notes):
            self.canvas_manager.create_card(
                note, i,
                start_drag_callback=self.canvas_manager.start_drag,
                do_drag_callback=self.canvas_manager.do_drag,
                stop_drag_callback=self.canvas_manager.stop_drag,
                open_menu_callback=self.open_menu
            )
        if hasattr(self, 'calendar_view'):
            self.calendar_view.refresh_notes_list()
        if hasattr(self, 'notes_list_view'):
            self.notes_list_view.refresh_list()
        if hasattr(self, 'notification_manager'):
            self.notification_manager.reset_notified()

    def open_menu(self, event, index):
        self.selected_index = index
        self.menu.tk_popup(event.x_root, event.y_root)

    def change_color(self):
        if self.selected_index is None:
            return
        color = colorchooser.askcolor()[1]
        if color:
            self.note_manager.update_color(self.selected_index, color)
            self.refresh()

    def edit_note(self):
        if self.selected_index is None:
            return
        note = self.note_manager.notes[self.selected_index]
        open_edit_text_dialog(
            self.root,
            note["text"],
            lambda new_text: self._apply_text_edit(new_text)
        )

    def _apply_text_edit(self, new_text):
        self.note_manager.update_text(self.selected_index, new_text)
        self.refresh()

    def delete_note(self):
        if self.selected_index is None:
            return
        self.note_manager.delete(self.selected_index)
        self.refresh()

    def save_positions_and_notes(self):
        self.canvas_manager.save_positions(self.note_manager.notes)
        self.note_manager.save()

    def on_close(self):
        self.save_positions_and_notes()
        self.notification_manager.stop()
        self.root.destroy()