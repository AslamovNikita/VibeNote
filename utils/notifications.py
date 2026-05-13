import threading
from datetime import datetime
import time
import tkinter as tk
from utils.config import BG_COLOR, CARD_DEFAULT_COLOR, BUTTON_ADD_COLOR, TEXT_COLOR


class NotificationManager:
    def __init__(self, notes_manager, root):
        self.notes_manager = notes_manager
        self.root = root
        self.running = False
        self.thread = None
        self.notified_notes = set()

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._check_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _check_loop(self):
        while self.running:
            self._check_deadlines()
            time.sleep(3600)

    def _check_deadlines(self):
        now = datetime.now()

        for idx, note in enumerate(self.notes_manager.notes):
            deadline_str = note.get("deadline", "")
            if not deadline_str:
                continue

            try:
                deadline = datetime.strptime(deadline_str, "%d.%m.%Y %H:%M")
                note_id = f"{idx}_{deadline_str}"

                if note_id in self.notified_notes:
                    continue

                days_left = (deadline - now).days

                if deadline < now:
                    self._show_notification("⛔ Дедлайн просрочен", f"Заметка: {note['text'][:50]}")
                    self.notified_notes.add(note_id)
                elif days_left == 1:
                    self._show_notification("⚠️ Дедлайн завтра!", f"Заметка: {note['text'][:50]}")
                    self.notified_notes.add(note_id)
                elif days_left == 3:
                    self._show_notification("📅 Скоро дедлайн", f"Заметка: {note['text'][:50]}\nОсталось 3 дня")
                    self.notified_notes.add(note_id)
                elif days_left == 7:
                    self._show_notification("📅 Дедлайн через неделю", f"Заметка: {note['text'][:50]}\nОсталось 7 дней")
                    self.notified_notes.add(note_id)
            except:
                pass

    def _show_notification(self, title, message):
        def show():
            win = tk.Toplevel(self.root)
            win.overrideredirect(True)
            win.attributes("-topmost", True)
            win.configure(bg=BG_COLOR)

            win.update_idletasks()
            x = win.winfo_screenwidth() - 400
            y = win.winfo_screenheight() - 150
            win.geometry(f"380x130+{x}+{y}")

            color = "#e74c3c" if "просрочено" in title or "завтра" in title else "#f39c12" if "Скоро" in title or "неделю" in title else BUTTON_ADD_COLOR

            tk.Frame(win, bg=color, height=4).pack(fill="x")

            frame = tk.Frame(win, bg=BG_COLOR)
            frame.pack(fill="both", expand=True, padx=15, pady=10)

            tk.Label(frame, text=title, bg=BG_COLOR, fg=color, font=("Arial", 12, "bold")).pack(anchor="w")
            tk.Label(frame, text=message, bg=BG_COLOR, fg=TEXT_COLOR, font=("Arial", 10), wraplength=350,
                     justify="left").pack(anchor="w", pady=(5, 10))

            btn = tk.Button(frame, text="OK", bg=BUTTON_ADD_COLOR, fg="white", relief="flat", command=win.destroy, bd=0,
                            padx=10, pady=3)
            btn.pack()

            win.after(5000, win.destroy)

        self.root.after(0, show)

    def reset_notified(self):
        self.notified_notes.clear()


def check_deadlines_now(notes_manager):
    now = datetime.now()
    for note in notes_manager.notes:
        deadline_str = note.get("deadline", "")
        if not deadline_str:
            continue
        try:
            deadline = datetime.strptime(deadline_str, "%d.%m.%Y %H:%M")
            if deadline < now:
                print(f"⛔ Просрочено: {note['text'][:50]}")
            elif (deadline - now).days == 1:
                print(f"⚠️ Завтра дедлайн: {note['text'][:50]}")
        except:
            pass