# точка входа в приложение

import tkinter as tk
from app import NotesApp

if __name__ == "__main__":
    root = tk.Tk()
    app = NotesApp(root)
    root.mainloop()