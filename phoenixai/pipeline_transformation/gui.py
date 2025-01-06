# gui_common.py
import os
import tkinter as tk
from tkinter import END, messagebox

back_history = []
forward_history = []
current_directory = os.getcwd()

def list_directory_contents(directory):
    contents = []
    for item in os.listdir(directory):
        full_path = os.path.join(directory, item)
        if os.path.isdir(full_path):
            contents.append(f"{item}/")
        elif item.endswith(".py"):
            contents.append(item)
    return contents

def update_directory_list(directory, dir_listbox, dir_label, pipeline, add_to_history=True):
    global current_directory, back_history, forward_history

    if add_to_history:
        back_history.append(current_directory)

    # Nur löschen, wenn der Benutzer nicht über Vorwärts navigiert
    if add_to_history and current_directory != directory:
        forward_history.clear()

    current_directory = directory
    dir_listbox.delete(0, END)
    contents = list_directory_contents(directory)
    for item in contents:
        dir_listbox.insert(END, item)
    dir_label.config(text=f"Aktuelles Verzeichnis: {directory}")
    pipeline.reset()

def navigate_up(dir_listbox, dir_label, pipeline):
    global current_directory
    parent_directory = os.path.dirname(current_directory)
    if parent_directory != current_directory:
        update_directory_list(parent_directory, dir_listbox, dir_label, pipeline)
    else:
        messagebox.showinfo("Info", "Sie befinden sich bereits im Wurzelverzeichnis.")

def navigate_back(dir_listbox, dir_label, pipeline):
    global back_history, current_directory, forward_history
    if back_history:
        forward_history.append(current_directory)
        previous_directory = back_history.pop()
        update_directory_list(previous_directory, dir_listbox, dir_label, pipeline, add_to_history=False)
    else:
        messagebox.showinfo("Info", "Keine vorherigen Verzeichnisse in der Historie.")

def navigate_forward(dir_listbox, dir_label, pipeline):
    global forward_history, current_directory, back_history
    if forward_history:
        back_history.append(current_directory)
        next_directory = forward_history.pop()
        update_directory_list(next_directory, dir_listbox, dir_label, pipeline, add_to_history=False)
    else:
        messagebox.showinfo("Info", "Keine weiteren Verzeichnisse in der Historie.")
