import tkinter as tk
from venv.mainapp import MainApplication

root = tk.Tk()
root.title("END GAME")

MainApplication(root).pack(side="top", fill="both", expand=True)
