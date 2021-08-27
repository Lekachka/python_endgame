import tkinter as tk
from tkinter import *
from tkinter import ttk,messagebox
from tkinter.ttk import Combobox
from . import func


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

class Tabs(tk.Frame):
    """Create tabs"""

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        tab = ttk.Notebook(self.parent)
        tab.pack(pady=10, expand=True)

        self.frame1 = ttk.Frame(tab, width=300, height=300)
        tab.add(self.frame1, text="Send request")

        self.frame2 = ttk.Frame(tab, width=300, height=300)
        tab.add(self.frame2, text="History")


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

        self.but1 = tk.Button(self, text='Send', bg='#43b091',width=10,command=self.show_result)
        self.but1.pack(side=LEFT,anchor=N)
        self.but1.bind('<Button-1>', self.qw)

    def qw(self,event):

        if self.entry_link.get() == "enter your link":
            link_dict = {}
        else:
            link_dict = {'url': self.entry_link.get()}

        self.res_dict = {'method' : self.comb_box.get()}
        params = func.result_dict(Frame_params.all)
        params_dict = {"params": params}
        body = func.result_dict(Frame_body.all)
        body_dict = {"body" : body}
        header = func.result_dict(Frame_header.all)
        header_dict = {"header": header}
        auth = func.get_log(Frame_auth.logs)
        log_dict = {'log': Log_level.res}
        responce_dict = {'responce': Responce_view.res}

        self.res_dict.update(link_dict)
        self.res_dict.update(auth)
        self.res_dict.update(params_dict)
        self.res_dict.update(body_dict)
        self.res_dict.update(header_dict)
        self.res_dict.update(log_dict)
        self.res_dict.update(responce_dict)

    #Result window
    def show_result(self):

        def exit():
            root.destroy()

        root = Toplevel(self.parent)
        root.title("Result")
        text = Text(root,width=50, height=20,wrap=WORD,borderwidth=3,relief="sunken")
        text.insert(1.0, self.res_dict)

        b1 = Button(root, text="Закрыть", command=exit, borderwidth=2, width=10, relief='raised')
        # b1.bind('<Button-1>')
        b2 = Button(root,text="Сохранить", command=func.extract_text,width=10,borderwidth=2,relief='raised')

        text.pack(side=TOP, padx=30, pady=10)
        b1.pack(side=RIGHT, pady=10, padx=10)
        b2.pack(side=RIGHT,pady=10,padx=10)

        root.mainloop()


class Frame_auth(tk.LabelFrame):
    """authentication"""
    logs = []
    def __init__(self, parent, *args, **kwargs):
        tk.LabelFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.entry_log = EntryPlaceholder(self,"username")
        self.entry_pass = EntryPlaceholder(self, "password")

        self.entry_log.pack(side=LEFT)
        self.entry_pass.pack(side=LEFT)

        self.logs.append(self.entry_log)
        self.logs.append(self.entry_pass)


class Frame_params(tk.LabelFrame):
    """Params"""
    all = []
    def __init__(self,parent,*args,**kwargs):
        tk.LabelFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        addboxButton = Button(self.parent, text='add params',background='#43b091',width=10)
        addboxButton.bind('<Button-1>',self.addBox)

        addboxButton.pack(side=TOP, anchor=NE)

    def addBox(self,event):
        frame = Frame(self)
        frame.pack()

        ent1 = EntryPlaceholder(frame,'enter apikey')
        ent2 = EntryPlaceholder(frame,'enter value')

        ent1.grid(row=1, column=0)
        ent2.grid(row=1, column=1)

        self.all.append((ent1, ent2))

class Frame_body(tk.LabelFrame):
    """Body"""
    all = []

    def __init__(self, parent, *args, **kwargs):
        tk.LabelFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent


        addboxButton = Button(self.parent, text='add body',background='#43b091',width=10)
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

        addboxButton = Button(self.parent, text='add header',background='#43b091',width=10)
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

#Getting logs
def log(data):

    if data.get() == 0:
        Log_level.res = "DEBUG"
        # print(Log_level.res)
    elif data.get() == 1:
        Log_level.res = "INFO"
        # print(Log_level.res)
    elif data.get() == 2:
        Log_level.res = "WARNING"
        # print(Log_level.res)

class Log_level(tk.Frame):
    """Logs Frame"""
    res = "DEBUG"

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent=parent

        Label(self, text="Log level",width=15).pack(side=LEFT,anchor=W)

        var1 = IntVar()
        var1.set(0)

        debug_but = tk.Radiobutton(self, text="DEBUG", height=1, width=8, bg='#43b095', variable=var1,
                                        indicatoron=0, value=0,command = lambda : log(var1))

        info_but = tk.Radiobutton(self, text="INFO", height=1, width=8, bg='#43b095', variable=var1,
                                         indicatoron=0, value=1,command = lambda : log(var1))

        warning_but = tk.Radiobutton(self, text="WARNING", height=1, width=8, bg='#43b095', variable=var1,
                                            indicatoron=0, value=2,command = lambda : log(var1))


        debug_but.pack(side=LEFT, anchor=W, ipadx=10)
        info_but.pack(side=LEFT, anchor=W, ipadx=10)
        warning_but.pack(side=LEFT, anchor=W, ipadx=10)

#Getting responce
def responce(data):
    if data.get() == 0:
        Responce_view.res = "RAW"
    elif data.get() == 1:
        Responce_view.res = "Pretty JSON"
    elif data.get() == 2:
        Responce_view.res = "YAML"
    # elif data.get() == 3:
    #     Response_view.res = "Treeview"
    # elif data.get() == 4:
    #     Response_view.res = "Table"


class Responce_view(tk.Frame):
    """Response frame"""

    res = "RAM"

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent=parent

        Label(self,text="Responce view", width=15).pack(side=LEFT)

        var2 = IntVar()
        var2.set(0)

        raw = tk.Radiobutton(self, text="RAW", height=1, width=8, bg='#43b095', variable=var2, indicatoron=0, value=0,command = lambda : responce(var2))
        json = tk.Radiobutton(self, text="Pretty JSON", height=1, width=8,bg='#43b095', variable=var2, indicatoron=0, value=1,command = lambda : responce(var2))
        yaml = tk.Radiobutton(self, text="YAML", height=1, width=8, bg='#43b095', variable=var2, indicatoron=0, value=2,command = lambda : responce(var2))

        raw.pack(side=LEFT, anchor=W, ipadx=10)
        json.pack(side=LEFT, anchor=W, ipadx=10)
        yaml.pack(side=LEFT, anchor=W,ipadx=10)
        # debug_treeview = tk.Radiobutton(self, text="Treeview", height=1, width=7, bg='#43b095', variable=var2, indicatoron=0, value=3,command = lambda : response(var2))
        # debug_treeview.pack(side=LEFT,anchor=W)
        # debug_table = tk.Radiobutton(self, text="Table", height=1, width=6, bg='#43b095', variable=var2, indicatoron=0, value=4,command = lambda : response(var2))
        # debug_table.pack(side=LEFT, anchor=W)

class History(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent=parent
        clear_histroy = tk.Button(self,text="Clear history")
        clear_histroy.pack(side=LEFT,padx=10,pady=10)


    def addBox(self):
        frame = Frame(self)
        frame.pack()

        ent1 = EntryPlaceholder(frame, 'enter apikey')
        ent2 = EntryPlaceholder(frame, 'enter value')

        ent1.grid(row=1, column=0)
        ent2.grid(row=1, column=1)

# class documentMaker():
#     def test():
#         return "hello people"
