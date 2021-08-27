import tkinter
from tkinter import filedialog


def get_log(data):
    if data[0].get() == "username" and data[1].get() == "password":
        l_dict = {}
    else:
        l_dict = {"auth":{data[0].get():data[1].get()}}
    return l_dict


def result_dict(data):
    temp_dict = {}
    for number, (a, b) in enumerate(data):
        if a.get() == 'enter apikey' and b.get() == 'enter value':
            return temp_dict
        else:
            temp = {a.get(): b.get()}
        temp_dict.update(temp)
    return temp_dict


def extract_text():
    file_name = filedialog.asksaveasfilename(
        filetypes=(("TXT files", "*.txt"),
                   ("JSON files", "*.json"),
                   ("YAML files", "*.yaml"),
                   ("All files", "*.*")))
    f = open(file_name, 'w')
    #s = text.get(1.0, END)
    #f.write(s)
    f.close()
