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

    def _create_textured_button(self, parent, text, command, width=None):
        import os, sys
        from PIL import Image, ImageTk

        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        btn_bg_path = os.path.join(base_dir, "button_bg.png")
        w = width if width else 120
        h = 40

        if os.path.exists(btn_bg_path):
            from PIL import Image
            bg_color = (120, 50, 30)
            colored_bg = Image.new("RGB", (w, h), bg_color)
            texture = Image.open(btn_bg_path).convert("RGBA")
            texture = texture.resize((w, h), Image.LANCZOS)
            colored_bg = colored_bg.convert("RGBA")
            colored_bg.paste(texture, (0, 0), texture)
            btn_photo = ImageTk.PhotoImage(colored_bg)
            btn = tk.Canvas(
                parent,
                width=w,
                height=h,
                bg=BG_COLOR,
                bd=0,
                highlightthickness=0
            )
            btn.create_image(w // 2, h // 2, image=btn_photo)
            btn.create_text(w // 2, h // 2, text=text, fill="white",
                            font=("Arial", 11, "bold"))
            btn.bind("<Button-1>", lambda e: command())
            btn._photo = btn_photo
        else:
            btn = tk.Button(
                parent,
                text=text,
                bg=CARD_DEFAULT_COLOR,
                fg="white",
                font=("Arial", 11, "bold"),
                relief="flat",
                command=command,
                bd=0,
                highlightthickness=0,
                padx=15, pady=5
            )
        return btn

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Add.TButton", background=BUTTON_ADD_COLOR, foreground="white")
        # стиль вкладок
        style.configure("TNotebook", background="#3E1A12", borderwidth=0)
        style.configure("TNotebook.Tab",
                        background="#000000",
                        foreground="white",
                        padding=[15, 8],
                        font=("Arial", 11),
                        borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", "#78281F")],
                  foreground=[("selected", "white")])
        style.configure("Brown.TFrame", background="#3E1A12", borderwidth=3)

    def _build_header(self):

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        board_frame = ttk.Frame(self.notebook, style="Brown.TFrame")
        self.notebook.add(board_frame, text="📋 Доска заметок")


        board_header = tk.Frame(board_frame, bg="#000000")
        board_header.pack(fill="x", pady=10)

        tk.Label(
            board_header,
            text="📋 Доска заметок",
            bg="#000000",
            fg="white",
            font=("Arial", 18, "bold")
        ).pack(side="left", padx=20)

        add_btn = self._create_textured_button(
            board_header,
            text="➕ Добавить",
            command=self.add_note_ui,
            width=140
        )
        add_btn.pack(side="right", padx=20)

        self.canvas_manager = CanvasManager(
            board_frame,
            bg_color=BG_COLOR,
            on_drag_end_callback=self.save_positions_and_notes
        )
        self.canvas_manager.canvas.config(
            highlightthickness=3,
            highlightbackground="#3E1A12" #коричневая рамка
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