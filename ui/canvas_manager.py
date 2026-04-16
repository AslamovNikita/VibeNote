#инкапсуляция работы с холстом, отрисовка карточек

import tkinter as tk
from utils.date_utils import get_time_left
from utils.config import CARD_WIDTH, CARD_MAX_HEIGHT_GUESS

class CanvasManager:
    def __init__(self, parent, bg_color, on_drag_end_callback):
        self.canvas = tk.Canvas(parent, bg=bg_color, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.drag_data = None
        self.on_drag_end_callback = on_drag_end_callback  #вызывается после перетаскивания

    def clear(self):
        self.canvas.delete("all")

    def create_card(self, note, index, start_drag_callback, do_drag_callback, stop_drag_callback, open_menu_callback):

        #cоздаёт карточку и размещает её на холсте
        #возвращает ID canvas window

        text = note["text"]
        color = note["color"]
        # рассчитывается высота карточки по тексту
        temp_label = tk.Label(self.canvas, text=text, font=("Arial", 14, "bold"),
                              wraplength=CARD_WIDTH - 20, justify="left")
        temp_label.update_idletasks()
        text_height = temp_label.winfo_reqheight()
        temp_label.destroy()

        card_height = text_height + 70

        card_frame = tk.Frame(self.canvas, bg=color, width=CARD_WIDTH, height=card_height)
        card_frame.pack_propagate(False)

        tk.Label(card_frame, text=text, bg=color, fg="white",
                 font=("Arial", 14, "bold"), wraplength=CARD_WIDTH - 20,
                 justify="left").pack(anchor="w")

        deadline_str = get_time_left(note.get("deadline"))
        tk.Label(card_frame, text="⏳ " + deadline_str, bg=color, fg="#ccc",
                 font=("Arial", 11)).pack(anchor="w")
# привязка событий
        card_frame.bind("<Button-1>", start_drag_callback)
        card_frame.bind("<B1-Motion>", do_drag_callback)
        card_frame.bind("<ButtonRelease-1>", stop_drag_callback)
        card_frame.bind("<Button-3>", lambda e, i=index: open_menu_callback(e, i))

# размещаем на холсте
        cid = self.canvas.create_window(
            note.get("x", 50), note.get("y", 50),
            window=card_frame, anchor="nw"
        )

        # сохраняем ID в самом фрейме для удобства
        card_frame._canvas_id = cid
        return cid

    def start_drag(self, event):
        self.drag_data = {
            "item": event.widget._canvas_id,
            "x": event.x_root,
            "y": event.y_root
        }

    def do_drag(self, event):
        if not self.drag_data:
            return

        item = self.drag_data["item"]
        dx = event.x_root - self.drag_data["x"]
        dy = event.y_root - self.drag_data["y"]

        x0, y0 = self.canvas.coords(item)
        new_x = x0 + dx
        new_y = y0 + dy

        # ограничение по границам холста
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        new_x = max(0, min(new_x, w - CARD_WIDTH))
        new_y = max(0, min(new_y, h - CARD_MAX_HEIGHT_GUESS))

        self.canvas.coords(item, new_x, new_y)

        self.drag_data["x"] = event.x_root
        self.drag_data["y"] = event.y_root

    def stop_drag(self, event):
        self.drag_data = None
        self.on_drag_end_callback()

    def save_positions(self, notes):
       #сохраняет координаты каждой карточки в списке заметок
        items = self.canvas.find_all()
        for i, note in enumerate(notes):
            if i < len(items):
                x, y = self.canvas.coords(items[i])
                note["x"] = x
                note["y"] = y