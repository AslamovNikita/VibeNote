#инкапсуляция работы с холстом, отрисовка карточек

import tkinter as tk
from utils.date_utils import get_time_left
from utils.config import CARD_WIDTH, CARD_MAX_HEIGHT_GUESS
from PIL import Image, ImageTk

class CanvasManager:
    def __init__(self, parent, bg_color, on_drag_end_callback):
        self.canvas = tk.Canvas(parent, bg=bg_color, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.drag_data = None
        self.on_drag_end_callback = on_drag_end_callback  #вызывается после перетаскивания
        self.resize_data = None
        self.bg_item = None
        self.bg_image = None
        self.bg_raw = None

        self.canvas.update()
        self._load_background()
        self.canvas.bind("<Configure>", self._resize_background)

    def clear(self):
        for item in self.canvas.find_all():
            if item != self.bg_item:
                self.canvas.delete(item)

    def create_card(self, note, index, start_drag_callback, do_drag_callback, stop_drag_callback, open_menu_callback):

        #cоздаёт карточку и размещает её на холсте
        #возвращает ID canvas window

        text = note["text"]
        color = note["color"]
        card_width = note.get("width", CARD_WIDTH)
        card_height = note.get("height", 200)
        # рассчитывается высота карточки по тексту
        temp_label = tk.Label(self.canvas, text=text, font=("Arial", 14, "bold"),
                              wraplength=CARD_WIDTH - 20, justify="left")
        temp_label.update_idletasks()
        text_height = temp_label.winfo_reqheight()
        temp_label.destroy()

        card_height = text_height + 70

        card_frame = tk.Frame(self.canvas, bg=color, width=card_width, height=card_height)
        card_frame.pack_propagate(False)

        tk.Label(card_frame, text=text, bg=color, fg="white",
                 font=("Arial", 14, "bold"), wraplength=card_width - 30,
                 justify="left").pack(anchor="w")

        deadline_str = get_time_left(note.get("deadline"))
        tk.Label(card_frame, text="⏳ " + deadline_str, bg=color, fg="#ccc",
                 font=("Arial", 11)).pack(anchor="w")
# привязка событий
        resize_handle = tk.Label(card_frame, text="◢", bg=color, fg="white",
                                 font=("Arial", 12), cursor="sizing")
        resize_handle.place(relx=1.0, rely=1.0, anchor="se", x=-5, y=-5)

        resize_handle.bind("<Button-1>", lambda e, f=card_frame, i=index: self.start_resize(e, f, i))
        resize_handle.bind("<B1-Motion>", self.do_resize)
        resize_handle.bind("<ButtonRelease-1>", self.stop_resize)
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
        items = self.canvas.find_all()
        item_index = 0
        for i, note in enumerate(notes):
            # Пропускаем элементы без опции "window" (например, фон)
            while item_index < len(items):
                try:
                    self.canvas.itemcget(items[item_index], "window")
                    break  # нашли элемент с window
                except:
                    item_index += 1  # пропускаем

            if item_index < len(items):
                item_id = items[item_index]
                x, y = self.canvas.coords(item_id)
                note["x"] = x
                note["y"] = y

                # получаем виджет карточки
                try:
                    widget = self.canvas.nametowidget(self.canvas.itemcget(item_id, "window"))
                    note["width"] = widget.winfo_width()
                    note["height"] = widget.winfo_height()
                except:
                    pass
                item_index += 1
    def _load_background(self):
        try:
            width = self.canvas.winfo_width() or 900
            height = self.canvas.winfo_height() or 650
            self.bg_raw = Image.open("background.jpg")
            self.bg_raw = self.bg_raw.resize((width, height))
            self.bg_image = ImageTk.PhotoImage(self.bg_raw)
            self.bg_item = self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        except Exception as e:
            print(f"Фон не загружен: {e}")

    def _resize_background(self, event):
        if event.width > 10 and event.height > 10 and self.bg_raw:
            try:
                resized = self.bg_raw.resize((event.width, event.height))
                self.bg_image = ImageTk.PhotoImage(resized)
                if self.bg_item:
                    self.canvas.itemconfig(self.bg_item, image=self.bg_image)
            except:
                pass

    def start_resize(self, event, card_frame, note_index):
        self.resize_data = {
            "frame": card_frame,
            "index": note_index,
            "start_x": event.x_root,
            "start_y": event.y_root,
            "start_width": card_frame.winfo_width(),
            "start_height": card_frame.winfo_height()
        }

    def do_resize(self, event):
        if not self.resize_data:
            return
        dx = event.x_root - self.resize_data["start_x"]
        dy = event.y_root - self.resize_data["start_y"]
        new_width = max(150, self.resize_data["start_width"] + dx)
        new_height = max(100, self.resize_data["start_height"] + dy)
        self.resize_data["frame"].config(width=new_width, height=new_height)
        for child in self.resize_data["frame"].winfo_children():
            if isinstance(child, tk.Label) and hasattr(child, 'cget') and 'wraplength' in child.keys():
                try:
                    child.config(wraplength=new_width - 30)
                except:
                    pass

    def stop_resize(self, event):
        if self.resize_data:
            self.on_drag_end_callback()
        self.resize_data = None