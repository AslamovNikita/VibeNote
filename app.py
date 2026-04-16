# сборка главного окна
# связывание всех компонентов, меню и логика сохранения

import tkinter as tk
from tkinter import ttk, colorchooser
from models.note_manager import NoteManager
from ui.canvas_manager import CanvasManager
from ui.dialogs import open_add_note_dialog, open_edit_text_dialog
from utils.config import BG_COLOR, CARD_DEFAULT_COLOR, BUTTON_ADD_COLOR, WINDOW_SIZE

class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📝 Доска заметок")
        self.root.geometry(WINDOW_SIZE)
        self.root.configure(bg=BG_COLOR)

# менеджер данных
        self.note_manager = NoteManager()

# настройка стилей
        self._setup_styles()

# шапка
        self._build_header()

# холст с карточками
        self.canvas_manager = CanvasManager(
            self.root,
            bg_color=BG_COLOR,
            on_drag_end_callback=self.save_positions_and_notes
        )

# контекстное меню
        self.selected_index = None
        self._build_context_menu()

# первая отрисовка
        self.refresh()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Add.TButton", background=BUTTON_ADD_COLOR, foreground="white")

    def _build_header(self):
        header = tk.Frame(self.root, bg=BG_COLOR)
        header.pack(fill="x")
        tk.Label(header, text="📒 Доска заметок", bg=BG_COLOR, fg="white",
                 font=("Arial", 18, "bold")).pack(pady=10)
        ttk.Button(header, text="➕ Добавить", style="Add.TButton",
                   command=self.add_note_ui).pack(pady=5)

    def _build_context_menu(self):
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="🎨 Цвет", command=self.change_color)
        self.menu.add_command(label="✏️ Редактировать", command=self.edit_note)
        self.menu.add_command(label="❌ Удалить", command=self.delete_note)

#UI взаимодействия
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

#схранение позиций
    def save_positions_and_notes(self):
        self.canvas_manager.save_positions(self.note_manager.notes)
        self.note_manager.save()

    def on_close(self):
        self.save_positions_and_notes()
        self.root.destroy()