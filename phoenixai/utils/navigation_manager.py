# navigation_manager.py

import os
import tkinter as tk
import ttkbootstrap as tb

class NavigationManager:
    def __init__(self, parent_frame, dir_label, dir_listbox, set_status_callback, update_directory_callback):
        self.parent_frame = parent_frame
        self.dir_label = dir_label
        self.dir_listbox = dir_listbox
        self.set_status = set_status_callback
        self.update_directory = update_directory_callback

        self.back_history = []
        self.forward_history = []
        self.current_directory = os.getcwd()

    def navigate_up(self):
        parent_directory = os.path.dirname(self.current_directory)
        if parent_directory != self.current_directory:
            self.update_directory(parent_directory)
        else:
            self.set_status("Sie befinden sich bereits im Wurzelverzeichnis.")

    def navigate_back(self):
        if self.back_history:
            self.forward_history.append(self.current_directory)
            previous_directory = self.back_history.pop()
            self.update_directory(previous_directory, add_to_history=False)
        else:
            self.set_status("Keine vorherigen Verzeichnisse.")

    def navigate_forward(self):
        if self.forward_history:
            self.back_history.append(self.current_directory)
            next_directory = self.forward_history.pop()
            self.update_directory(next_directory, add_to_history=False)
        else:
            self.set_status("Keine weiteren Verzeichnisse.")

    def update_directory_list(self, directory, add_to_history=True):
        if add_to_history:
            self.back_history.append(self.current_directory)
        if add_to_history and self.current_directory != directory:
            self.forward_history.clear()

        self.current_directory = directory
        self.dir_listbox.delete(0, tk.END)

        items = self.list_directory_contents(directory)
        for item in items:
            self.dir_listbox.insert(tk.END, item)

        self.dir_label.config(text=f"Aktuelles Verzeichnis: {directory}")

    def list_directory_contents(self, directory):
        """Listet alle Dateien und Ordner im Verzeichnis auf."""
        contents = []
        try:
            for item in os.listdir(directory):
                full_path = os.path.join(directory, item)
                if os.path.isdir(full_path):
                    contents.append(f"{item}/")
                elif item.endswith(".py"):
                    contents.append(item)
        except PermissionError:
            tb.messagebox.show_error("Fehler", f"Zugriff verweigert auf Verzeichnis: {directory}")
        return contents
