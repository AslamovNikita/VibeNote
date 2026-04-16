# вынос диалогов добавления и редактирования в отдельный модуль

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from utils.date_utils import auto_format_date_live, validate_deadline
from utils.config import BG_COLOR, BUTTON_ADD_COLOR

def open_add_note_dialog(parent, on_save_callback):

#открывает окно создания новой заметки
#on_save_callback(text, deadline) вызывается при успешном сохранении

    win = tk.Toplevel(parent)
    win.title("Новая заметка")
    win.geometry("420x320")
    win.configure(bg=BG_COLOR)

    tk.Label(win, text="Текст", bg=BG_COLOR, fg="white").pack()
    text_entry = tk.Text(win, height=6, font=("Arial", 12))
    text_entry.pack(fill="x", padx=10)

    tk.Label(win, text="Дата (цифры → автоформат)", bg=BG_COLOR, fg="white").pack()
    deadline_entry = tk.Entry(win, font=("Arial", 12))
    deadline_entry.pack(fill="x", padx=10)

    def on_key_release(event):
        formatted = auto_format_date_live(deadline_entry.get())
        deadline_entry.delete(0, tk.END)
        deadline_entry.insert(0, formatted)

    deadline_entry.bind("<KeyRelease>", on_key_release)

    def save():
        text = text_entry.get("1.0", "end").strip()
        deadline = deadline_entry.get().strip()

        if not text:
            return

        if not validate_deadline(deadline):
            messagebox.showerror("Ошибка", "Неверный формат даты")
            return

        on_save_callback(text, deadline)
        win.destroy()
    ttk.Button(win, text="Сохранить", style="Add.TButton", command=save).pack(pady=10)

def open_edit_text_dialog(parent, initial_text, on_confirm_callback):

    #Простое окно редактирования текста
    new_text = simpledialog.askstring("Редактировать", "Текст:",
                                      initialvalue=initial_text, parent=parent)
    if new_text is not None and new_text.strip():
        on_confirm_callback(new_text.strip())