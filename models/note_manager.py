# отделение логики хранения от UI

import json
import os
from utils.config import FILE_NAME

class NoteManager:
    def __init__(self):
        self.notes = []
        self.load()

    def load(self):
        if os.path.exists(FILE_NAME):
            with open(FILE_NAME, "r", encoding="utf-8") as f:
                self.notes = json.load(f)

    def save(self):
        with open(FILE_NAME, "w", encoding="utf-8") as f:
            json.dump(self.notes, f, ensure_ascii=False, indent=2)

    def add(self, text, deadline, color, x, y):
        self.notes.append({
            "text": text,
            "deadline": deadline,
            "color": color,
            "x": x,
            "y": y
        })

    def update_position(self, index, x, y):
        if 0 <= index < len(self.notes):
            self.notes[index]["x"] = x
            self.notes[index]["y"] = y

    def update_color(self, index, color):
        if 0 <= index < len(self.notes):
            self.notes[index]["color"] = color

    def update_text(self, index, new_text):
        if 0 <= index < len(self.notes):
            self.notes[index]["text"] = new_text

    def delete(self, index):
        if 0 <= index < len(self.notes):
            del self.notes[index]