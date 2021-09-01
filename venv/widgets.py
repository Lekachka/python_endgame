import json
import tkinter as tk
import tkinter.ttk
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox
import sqlite3
import requests

from endgame import Req, print_view, run_query, m_logger
from . import func
from .func import get_log


class EntryPlaceholder(tk.Entry):
    def __init__(self, master=None, placeholder=None):
        self.entry_var = tk.StringVar()
        super().__init__(master, textvariable=self.entry_var)

        if placeholder is not None:
            self.placeholder = placeholder
            self.placeholder_color = 'grey'
            self.default_fg_color = self['fg']
            self.placeholder_on = False
            self.put_placeholder()

            self.entry_var.trace("w", self.entry_change)

            # При всех перечисленных событиях, если placeholder отображается, ставить курсор на 0 позицию
            self.bind("<FocusIn>", self.reset_cursor)
            self.bind("<KeyRelease>", self.reset_cursor)
            self.bind("<ButtonRelease>", self.reset_cursor)

    def entry_change(self, *args):
        if not self.get():
            self.put_placeholder()
        elif self.placeholder_on:
            self.remove_placeholder()
            self.entry_change()  # На случай, если после удаления placeholder остается пустое поле

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color
        self.icursor(0)
        self.placeholder_on = True

    def remove_placeholder(self):
        # Если был вставлен какой-то символ в начало, удаляем не весь текст, а только placeholder:
        text = self.get()[:-len(self.placeholder)]
        self.delete('0', 'end')
        self['fg'] = self.default_fg_color
        self.insert(0, text)
        self.placeholder_on = False

    def reset_cursor(self, *args):
        if self.placeholder_on:
            self.icursor(0)


class Main_labelframe(tk.LabelFrame):
    """Add widget in Send request"""

    def __init__(self, parent, *args, **kwargs):
        tk.LabelFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.label = tk.LabelFrame(self.parent)

        self.frame_auth = Frame_auth(self, text="aut")
        self.frame_auth.pack(side=TOP, anchor=NW)

        self.frame_params = Frame_params(self, text="params")
        self.frame_params.pack(side=TOP, anchor=NW)

        self.frame_body = Frame_body(self, text="body")
        self.frame_body.pack(side=TOP, anchor=NW)

        self.frame_header = Frame_header(self, text="header")
        self.frame_header.pack(side=TOP, anchor=NW)


class Frame_url(tk.Frame):
    """pars URL"""
    res_dict = {}
    req_inst = Req(res_dict)

    def __init__(self, parent):

        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.value = StringVar

        self.comb_box = Combobox(self, textvariable=self.value, width=10)
        self.comb_box['values'] = ("GET", "POST", "PUT", "PATCH", "DELETE")
        self.comb_box.current(0)
        self.comb_box.pack(side=LEFT, anchor=N, ipady=2.5)

        self.entry_link = EntryPlaceholder(self, 'enter your link')
        self.entry_link.pack(side=LEFT, anchor=N, ipady=2.5, ipadx=70)

        self.but1 = tk.Button(self, text='Send', bg='#43b091', width=10, command=self.show_result)
        self.but1.pack(side=LEFT, anchor=N)
        self.but1.bind('<Button-1>', self.qw)

    def qw(self, event):

        if self.entry_link.get() == "enter your link":
            link_dict = {}
        else:
            link_dict = {'url': self.entry_link.get()}

        self.res_dict = {'method': self.comb_box.get()}
        params = func.result_dict(Frame_params.all)
        params_dict = {"params": params}
        body = func.result_dict(Frame_body.all)
        body_dict = {"body": body}
        header = func.result_dict(Frame_header.all)
        header_dict = {"headers": header}
        auth_tmp = get_log(Frame_auth.logs).get('auth', None)
        auth = {'auth': list(auth_tmp.keys()) + list(auth_tmp.values())} if auth_tmp else {'auth': []}
        log_dict = {'log': Log_level.res}
        responce_dict = {'responce': Responce_view.res}

        self.res_dict.update(link_dict)
        self.res_dict.update(auth)
        self.res_dict.update(params_dict)
        self.res_dict.update(body_dict)
        self.res_dict.update(header_dict)
        self.res_dict.update(log_dict)
        self.res_dict.update(responce_dict)
        self.req_inst = Req(self.res_dict)  # create Request class instance

    # Result window
    def show_result(self):

        def extract_text():
            try:
                file_name = filedialog.asksaveasfilename(
                    filetypes=(("TXT files", "*.txt"),
                               ("JSON files", "*.json"),
                               ("YAML files", "*.yaml"),
                               ("All files", "*.*")))
                f = open(file_name, 'w')
                s = text.get(1.0, END)
                f.write(s)
                f.close()
            except FileNotFoundError:
                pass

        def exit():
            root.destroy()

        root = Toplevel(self.parent)
        root.title("Result")
        text = Text(root, width=50, height=20, wrap=WORD, borderwidth=3, relief="sunken")
        """Run request"""
        full_resp: run_query = False
        try:
            m_logger.info(f'Send {self.req_inst.method} request to {self.req_inst.url}')
            full_resp, mess = run_query(self.res_dict, self.req_inst)
            if full_resp:
                text.insert(1.0, print_view(full_resp, Responce_view.res, True))
            else:
                text.insert(1.0, mess)
        except requests.exceptions.RequestException as e:
            m_logger.error(f'<{self.req_inst.method}> request Faild with error:           {e}')
            text.insert(1.0, f'<{self.req_inst.method}> request Faild.\n       {e}')
        except json.decoder.JSONDecodeError as e:  # Can not decode responce to json format
            if Responce_view.res == 'json':  # if JSON is used as 'view' argument show errors
                m_logger.error('json deconding error')
                text.insert(1.0, 'json deconding error, show txt format:')
            if full_resp:
                text.insert(1.0, full_resp.text)
        except Exception as e:
            text.insert(1.0, e)
        """"""
        b1 = Button(root, text="Закрыть", command=exit, borderwidth=2, width=10, relief='raised')
        b2 = Button(root, text="Сохранить", command=extract_text, width=10, borderwidth=2, relief='raised')

        text.pack(side=TOP, padx=30, pady=10)
        b1.pack(side=RIGHT, pady=10, padx=10)
        b2.pack(side=RIGHT, pady=10, padx=10)

        root.mainloop()


class Frame_auth(tk.LabelFrame):
    """authentication"""
    logs = []

    def __init__(self, parent, *args, **kwargs):
        tk.LabelFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.entry_log = EntryPlaceholder(self, "username")
        self.entry_pass = EntryPlaceholder(self, "password")

        self.entry_log.pack(side=LEFT)
        self.entry_pass.pack(side=LEFT)

        self.logs.append(self.entry_log)
        self.logs.append(self.entry_pass)


class Frame_params(tk.LabelFrame):
    """Params"""
    all = []

    def __init__(self, parent, *args, **kwargs):
        tk.LabelFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        addboxButton = Button(self.parent, text='add params', background='#43b091', width=10)
        addboxButton.bind('<Button-1>', self.addBox)

        addboxButton.pack(side=TOP, anchor=NE)

    def addBox(self, event):
        frame = Frame(self)
        frame.pack()

        ent1 = EntryPlaceholder(frame, 'enter apikey')
        ent2 = EntryPlaceholder(frame, 'enter value')

        ent1.grid(row=1, column=0)
        ent2.grid(row=1, column=1)

        self.all.append((ent1, ent2))


class Frame_body(tk.LabelFrame):
    """Body"""
    all = []

    def __init__(self, parent, *args, **kwargs):
        tk.LabelFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        addboxButton = Button(self.parent, text='add body', background='#43b091', width=10)
        addboxButton.pack(side=TOP, anchor=NE)
        addboxButton.bind('<Button-1>', self.addBox)

    def addBox(self, event):
        frame = Frame(self)
        frame.pack()

        ent1 = EntryPlaceholder(frame, 'enter apikey')
        ent2 = EntryPlaceholder(frame, 'enter value')

        ent1.grid(row=1, column=0)
        ent2.grid(row=1, column=1)

        self.all.append((ent1, ent2))


class Frame_header(tk.LabelFrame):
    """Header"""
    all = []

    def __init__(self, parent, *args, **kwargs):
        tk.LabelFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        addboxButton = Button(self.parent, text='add header', background='#43b091', width=10)
        addboxButton.pack(side=TOP, anchor=NE)
        addboxButton.bind('<Button-1>', self.addBox)

    def addBox(self, event):
        frame = Frame(self)
        frame.pack()

        ent1 = EntryPlaceholder(frame, 'enter apikey')
        ent1.grid(row=1, column=0)

        ent2 = EntryPlaceholder(frame, 'enter value')
        ent2.grid(row=1, column=1)

        self.all.append((ent1, ent2))


# Getting logs
def log(data):
    if data.get() == 0:
        Log_level.res = "DEBUG"
    elif data.get() == 1:
        Log_level.res = "INFO"
    elif data.get() == 2:
        Log_level.res = "WARNING"
    m_logger.setLevel(Log_level.res)


class Log_level(tk.Frame):
    """Logs Frame"""
    res = "DEBUG"

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        Label(self, text="Log level", width=15).pack(side=LEFT, anchor=W)

        var1 = IntVar()
        var1.set(0)

        debug_but = tk.Radiobutton(self, text="DEBUG", height=1, width=8, bg='#43b095', variable=var1,
                                   indicatoron=0, value=0, command=lambda: log(var1))

        info_but = tk.Radiobutton(self, text="INFO", height=1, width=8, bg='#43b095', variable=var1,
                                  indicatoron=0, value=1, command=lambda: log(var1))

        warning_but = tk.Radiobutton(self, text="WARNING", height=1, width=8, bg='#43b095', variable=var1,
                                     indicatoron=0, value=2, command=lambda: log(var1))

        debug_but.pack(side=LEFT, anchor=W, ipadx=10)
        info_but.pack(side=LEFT, anchor=W, ipadx=10)
        warning_but.pack(side=LEFT, anchor=W, ipadx=10)


# Getting responce
def responce(data):
    if data.get() == 0:
        Responce_view.res = "raw"
    elif data.get() == 1:
        Responce_view.res = "json"
    elif data.get() == 2:
        Responce_view.res = "yaml"


class Responce_view(tk.Frame):
    """Response frame"""

    res = "raw"

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        Label(self, text="Responce view", width=15).pack(side=LEFT)

        var2 = IntVar()
        var2.set(0)

        raw = tk.Radiobutton(self, text="RAW", height=1, width=8, bg='#43b095', variable=var2,
                             indicatoron=0, value=0, command=lambda: responce(var2))
        json = tk.Radiobutton(self, text="Pretty JSON", height=1, width=8, bg='#43b095', variable=var2,
                              indicatoron=0, value=1, command=lambda: responce(var2))
        yaml = tk.Radiobutton(self, text="YAML", height=1, width=8, bg='#43b095', variable=var2,
                              indicatoron=0, value=2, command=lambda: responce(var2))

        raw.pack(side=LEFT, anchor=W, ipadx=10)
        json.pack(side=LEFT, anchor=W, ipadx=10)
        yaml.pack(side=LEFT, anchor=W, ipadx=10)


class History(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        clear_histroy = tk.Button(self, text="Show History", bg='#43b095')
        clear_histroy.bind("<Button-1>", self.show_result)
        clear_histroy.pack()

    def show_result(self, event):

        def exit():
            root.destroy()

        def update():

            for i in tree.get_children():
                tree.delete(i)
            root.update()

            connect = sqlite3.connect('history.db')
            cur = connect.cursor()
            cur.execute('CREATE TABLE IF NOT EXISTS history (N integer primary key, Method text, URL text, Params text,'
                        ' Headers text, Request_body text, Authentification text, status int , response text);')
            cur.execute('select * from history;')
            rows = cur.fetchall()
            for row in rows:
                tree.insert("", tk.END, values=row)
            cur.close()
            connect.close()

        def clear():
            connect = sqlite3.connect('history.db')
            cur = connect.cursor()
            cur.execute('drop table history;')
            update()
            for i in tree.get_children():
                tree.delete(i)
            root.update()

        def check():
            answer = tkinter.messagebox.askyesno(
                title="Предупреждение",
                message="Вы уверены что хотите очистить историю?"
            )
            if answer:
                clear()

        root = Toplevel(self.parent)
        root.title("History")

        root.geometry(f'1200x700')
        root.resizable(False, False)
        style = tkinter.ttk.Style(root)
        style.configure('Treeview', rowheight=60)

        tree = tkinter.ttk.Treeview(root, selectmode="browse", height=10,
                                    column=("c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8", "c9"), show='headings')

        sby = tkinter.Scrollbar(root, orient=VERTICAL, width=20)
        tree.configure(yscrollcommand=sby.set)
        sby.configure(command=tree.yview)

        sbx = tkinter.Scrollbar(root, orient=HORIZONTAL)
        tree.configure(xscrollcommand=sbx.set)
        sbx.configure(command=tree.xview)

        tree.heading("#1", text="Number")
        tree.heading("#2", text="Method")
        tree.heading("#3", text="URL")
        tree.heading("#4", text="Params")
        tree.heading("#5", text="Header")
        tree.heading("#6", text="Request_body")
        tree.heading("#7", text="Authentification")
        tree.heading("#8", text="status")
        tree.heading("#9", text="responce")

        tree.column("#1", anchor=tk.CENTER, minwidth=30, width=30)
        tree.column("#2", anchor=tk.CENTER, minwidth=0, width=50)
        tree.column("#3", anchor=tk.CENTER, minwidth=0, width=200)
        tree.column("#4", anchor=tk.CENTER, minwidth=0, width=200)
        tree.column("#5", anchor=tk.CENTER, minwidth=0, width=200)
        tree.column("#6", anchor=tk.CENTER, minwidth=0, width=200)
        tree.column("#7", anchor=tk.CENTER, minwidth=0, width=200)
        tree.column("#8", anchor=tk.CENTER, minwidth=0, width=200)
        tree.column("#9", anchor=tk.CENTER, minwidth=0, width=200)

        b1 = Button(root, text="Закрыть", command=exit, borderwidth=2, width=10, relief='raised')
        b2 = Button(root, text="Очистить", command=check, width=10, borderwidth=2, relief='raised')
        b3 = Button(root, text="Обновить", command=update, width=10, borderwidth=2, relief='raised')

        sby.pack(fill=Y, side='right', anchor='n', pady=(15, 95))
        tree.pack()
        sbx.pack(fill=X)
        b1.pack(side=RIGHT, anchor=W, pady=10, padx=10)
        b2.pack(side=RIGHT, anchor=W, pady=10, padx=10)
        b3.pack(side=RIGHT, anchor=W, pady=10, padx=10)

        update()

        root.mainloop()
