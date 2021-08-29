import tkinter as tk
from venv.widgets import *

class MainApplication(tk.Frame):
    tabs = None

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        tk.Label(self.parent, text='Rest Api request').pack(side="top", anchor='nw')

        # self.tabs = Tabs(self)
        # self.tabs.pack(side='top', anchor="nw")

        self.frame_url = Frame_url(self)
        self.frame_url.pack(side=TOP, pady=10, anchor=NW)

        self.history = History(self)
        self.history.pack(side=TOP,anchor = NE)

        self.label_frame1 = Main_labelframe(self, text='Shape your request')
        self.label_frame1.pack(ipadx=20,padx=55, anchor=NW, side=TOP)

        self.log_level = Log_level(self)
        self.log_level.pack(side=TOP, anchor=W, pady=10)

        self.responce_view = Responce_view(self)
        self.responce_view.pack(side=TOP, anchor=W,pady=10)
