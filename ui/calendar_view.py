import tkinter as tk
from tkinter import ttk
from datetime import datetime
import calendar

from utils.config import BG_COLOR, TEXT_COLOR, CARD_DEFAULT_COLOR
from utils.date_utils import validate_deadline


class CalendarView:
    def __init__(self, parent, notes, on_note_selected_callback=None):
        self.notes = notes
        self.on_note_selected = on_note_selected_callback

        now = datetime.now()
        self.current_year = now.year
        self.current_month = now.month

        self.frame = ttk.Frame(parent)
        self.frame.pack(fill="both", expand=True)

        self.build_ui()
        self.draw_calendar()
        self.refresh_notes_list()

    def build_ui(self):
        top = tk.Frame(self.frame, bg=BG_COLOR)
        top.pack(fill="x", pady=10)

        tk.Button(
            top,
            text="◀",
            command=self.prev_month,
            width=5,
            bg=CARD_DEFAULT_COLOR,
            fg="white",
            relief="flat"
        ).pack(side="left", padx=10)

        self.month_label = tk.Label(
            top,
            text="",
            bg=BG_COLOR,
            fg="white",
            font=("Arial", 16, "bold")
        )
        self.month_label.pack(side="left", expand=True)

        tk.Button(
            top,
            text="▶",
            command=self.next_month,
            width=5,
            bg=CARD_DEFAULT_COLOR,
            fg="white",
            relief="flat"
        ).pack(side="right", padx=10)

        self.calendar_frame = tk.Frame(self.frame, bg=BG_COLOR)
        self.calendar_frame.pack(fill="both", expand=True, padx=10, pady=5)

        notes_label = tk.Label(
            self.frame,
            text="📌 Заметки на выбранный день:",
            bg=BG_COLOR,
            fg="white",
            font=("Arial", 11, "bold"),
            anchor="w"
        )
        notes_label.pack(fill="x", padx=10, pady=(10, 5))

        self.notes_box = tk.Text(
            self.frame,
            height=12,
            bg=CARD_DEFAULT_COLOR,
            fg="white",
            font=("Arial", 11),
            wrap="word",
            relief="flat",
            padx=10,
            pady=10
        )
        self.notes_box.pack(fill="both", padx=10, pady=(0, 10))

        scrollbar = tk.Scrollbar(self.notes_box)
        scrollbar.pack(side="right", fill="y")
        self.notes_box.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.notes_box.yview)

    def draw_calendar(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        months_ru = {
            1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
            5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
            9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
        }
        month_name = months_ru[self.current_month]
        self.month_label.config(text=f"{month_name} {self.current_year}")

        days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

        for col, day in enumerate(days):
            tk.Label(
                self.calendar_frame,
                text=day,
                bg=BG_COLOR,
                fg="#aaa",
                font=("Arial", 10, "bold"),
                width=10,
                height=2
            ).grid(row=0, column=col, sticky="nsew")

        cal = calendar.Calendar(firstweekday=0)
        weeks = cal.monthdayscalendar(self.current_year, self.current_month)

        for row, week in enumerate(weeks, start=1):
            for col, day in enumerate(week):
                if day == 0:
                    continue

                date_string = f"{day:02d}.{self.current_month:02d}.{self.current_year}"
                notes_count = self.get_notes_count(date_string)

                if notes_count > 0:
                    bg_color = "#3a6ea5"
                    text_color = "white"
                else:
                    bg_color = CARD_DEFAULT_COLOR
                    text_color = "#ccc"

                text = str(day)
                if notes_count > 0:
                    text += f"\n📝 {notes_count}"

                btn = tk.Button(
                    self.calendar_frame,
                    text=text,
                    width=10,
                    height=3,
                    bg=bg_color,
                    fg=text_color,
                    font=("Arial", 10),
                    relief="flat",
                    command=lambda d=date_string: self.show_notes(d)
                )

                btn.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")

        for i in range(7):
            self.calendar_frame.grid_columnconfigure(i, weight=1)

    def get_notes_count(self, date_string):
        count = 0
        for note in self.notes:
            deadline = note.get("deadline", "")
            if deadline and deadline.startswith(date_string):
                count += 1
        return count

    def show_notes(self, date_string):
        self.notes_box.delete("1.0", tk.END)
        self.current_date = date_string

        found = False
        note_index = 0

        for note in self.notes:
            deadline = note.get("deadline", "")
            if deadline and deadline.startswith(date_string):
                found = True

                self.notes_box.insert(tk.END, f"📌 ", "bullet")
                self.notes_box.insert(tk.END, f"{note['text']}\n", f"note_{note_index}")
                self.notes_box.insert(tk.END, f"   ⏰ {deadline}\n\n", "meta")

                self.notes_box.tag_config(f"note_{note_index}", foreground="#81c784", underline=1)
                self.notes_box.tag_bind(f"note_{note_index}", "<Button-1>", 
                                        lambda e, idx=note_index: self.select_note(idx))
                self.notes_box.tag_bind(f"note_{note_index}", "<Enter>", 
                                        lambda e: self.notes_box.config(cursor="hand2"))
                self.notes_box.tag_bind(f"note_{note_index}", "<Leave>", 
                                        lambda e: self.notes_box.config(cursor=""))

                note_index += 1

        self.notes_box.tag_config("bullet", foreground="#4CAF50")
        self.notes_box.tag_config("meta", foreground="#888", font=("Arial", 10))

        if not found:
            self.notes_box.insert(tk.END, "✨ Нет заметок на этот день", "empty")
            self.notes_box.tag_config("empty", foreground="#aaa", font=("Arial", 11, "italic"))

    def select_note(self, note_index):
        if self.on_note_selected and note_index < len(self.notes):
            target_deadline = self.current_date if hasattr(self, 'current_date') else ""
            matching_notes = []
            for idx, note in enumerate(self.notes):
                if note.get("deadline", "").startswith(target_deadline):
                    matching_notes.append((idx, note))

            if note_index < len(matching_notes):
                original_idx, note = matching_notes[note_index]
                self.on_note_selected(original_idx, note)

    def refresh_notes_list(self):
        if hasattr(self, 'current_date'):
            self.show_notes(self.current_date)

    def prev_month(self):
        self.current_month -= 1
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        self.draw_calendar()

    def next_month(self):
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        self.draw_calendar()


def add_calendar_tab(notebook, notes, on_note_selected_callback=None):
    calendar_frame = ttk.Frame(notebook)
    notebook.add(calendar_frame, text="📅 Календарь")
    calendar_view = CalendarView(calendar_frame, notes, on_note_selected_callback)
    return calendar_view