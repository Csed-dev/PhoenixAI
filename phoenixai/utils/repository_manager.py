import os
import json
import subprocess
import shutil
from tkinter import END, filedialog, messagebox
import tkinter as tk
import ttkbootstrap as tb

class RepositoryManager:
    def __init__(self, parent_frame, set_status_callback, populate_repos_callback):
        self.parent_frame = parent_frame
        self.set_status = set_status_callback
        self.populate_repos = populate_repos_callback
        self.repositories = []
        self.repos_file = "repos.json"

        self.build_repository_section()

    def build_repository_section(self):
        """Erstellt den Repository Management Abschnitt der GUI."""
        repo_frame = tb.LabelFrame(self.parent_frame, text="Repository Management", bootstyle="info")
        repo_frame.pack(fill="x", pady=10, padx=10)

        # Eingabefeld für GitHub Repo URL
        url_label = tb.Label(repo_frame, text="GitHub Repository URL:", bootstyle="secondary")
        url_label.pack(anchor="w", padx=5, pady=(10, 0))
        self.repo_url_entry = tb.Entry(repo_frame, width=50, bootstyle="secondary")
        self.repo_url_entry.pack(fill="x", padx=5, pady=5)

        # Button zum Klonen des Repos
        clone_button = tb.Button(repo_frame, text="Repository klonen", command=self.clone_repository, bootstyle="primary")
        clone_button.pack(padx=5, pady=5, anchor="w")

        # Button zum Hinzufügen eines bestehenden Repos
        add_existing_repo_button = tb.Button(repo_frame, text="Bestehendes Repository hinzufügen", command=self.add_existing_repository, bootstyle="primary")
        add_existing_repo_button.pack(padx=5, pady=5, anchor="w")

        # Listbox zur Anzeige der geklonten Repositories
        repos_list_label = tb.Label(repo_frame, text="Geklonte Repositories:", bootstyle="secondary")
        repos_list_label.pack(anchor="w", padx=5, pady=(15, 5))
        list_frame = tb.Frame(repo_frame)
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.repos_listbox = tk.Listbox(list_frame, height=5, font=("Helvetica", 10))
        self.repos_listbox.pack(side="left", fill="both", expand=True, padx=(0,5), pady=5)
        repos_scroll = tb.Scrollbar(list_frame, orient="vertical", command=self.repos_listbox.yview)
        repos_scroll.pack(side="right", fill="y")
        self.repos_listbox.config(yscrollcommand=repos_scroll.set)
        self.repos_listbox.bind("<<ListboxSelect>>", self.on_repo_select)

        # Button zum Entfernen des ausgewählten Repos
        remove_repo_button = tb.Button(repo_frame, text="Repository entfernen", command=self.remove_repository, bootstyle="danger-outline")
        remove_repo_button.pack(padx=5, pady=5, anchor="w")

        # Laden der Repositories in die Listbox
        self.load_repositories()
        self.populate_repos_listbox()

    def load_repositories(self):
        """Lädt die Repository-Liste aus der JSON-Datei und stellt sicher, dass sie gültig ist."""
        if os.path.exists(self.repos_file):
            try:
                with open(self.repos_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if not content:
                        self.repositories = []  # Leere Datei -> Initialisiere leere Liste
                    else:
                        self.repositories = json.loads(content)  # JSON einlesen
            except json.JSONDecodeError:
                messagebox.showerror("Fehler",
                                         f"Die Datei {self.repos_file} enthält kein gültiges JSON. Sie wird zurückgesetzt.")
                self.repositories = []
                self.save_repositories()  # Korrupte Datei direkt überschreiben
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Laden der Repositories:\n{e}")
                self.repositories = []
        else:
            self.repositories = []

    def save_repositories(self):
        """Speichert die Repository-Liste in die JSON-Datei."""
        try:
            with open(self.repos_file, "w", encoding="utf-8") as f:
                json.dump(self.repositories, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern der Repositories:\n{e}")

    def populate_repos_listbox(self):
        """Füllt die Listbox mit den geladenen Repositories."""
        self.repos_listbox.delete(0, END)
        for repo in self.repositories:
            self.repos_listbox.insert(END, repo['name'])

    def clone_repository(self):
        """Klonen eines neuen GitHub-Repositories und es zur Liste hinzufügen."""
        url = self.repo_url_entry.get().strip()
        if not url:
            messagebox.showwarning("Warnung", "Bitte geben Sie eine GitHub Repository URL ein.")
            return

        # Zielverzeichnis auswählen
        default_dir = os.path.expanduser("~/Documents/GitHub_Repos")
        dest_dir = filedialog.askdirectory(initialdir=default_dir, title="Zielverzeichnis auswählen")
        if not dest_dir:
            return

        repo_name = url.rstrip('/').split('/')[-1]
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]

        repo_path = os.path.join(dest_dir, repo_name)
        if os.path.exists(repo_path):
            messagebox.showerror("Fehler", f"Das Verzeichnis '{repo_path}' existiert bereits.")
            return

        # Klonen des Repositories
        try:
            self.set_status(f"Klonen des Repositories '{repo_name}' wird gestartet...")
            subprocess.check_call(['git', 'clone', url, repo_path])
            self.set_status(f"Repository '{repo_name}' erfolgreich geklont.")

            # Hinzufügen zur Repository-Liste
            self.repositories.append({
                'name': repo_name,
                'path': repo_path
            })
            self.save_repositories()  # Speichern nach erfolgreichem Klonen
            self.populate_repos_listbox()
            self.repo_url_entry.delete(0, END)

        except subprocess.CalledProcessError as e:
            messagebox.showerror("Fehler", f"Fehler beim Klonen des Repositories:\n{e}")
            self.set_status(f"Fehler beim Klonen des Repositories '{repo_name}'.")
        except FileNotFoundError:
            messagebox.showerror("Fehler", "Git ist nicht installiert oder nicht im PATH gefunden.")
            self.set_status("Git ist nicht installiert oder nicht im PATH gefunden.")

    def add_existing_repository(self):
        """Hinzufügen eines bestehenden lokalen Git-Repositories."""
        selected_dir = filedialog.askdirectory(title="Bestehendes Repository auswählen")
        if not selected_dir:
            return

        git_dir = os.path.join(selected_dir, ".git")
        if not os.path.isdir(git_dir):
            messagebox.showerror("Fehler",
                                 "Das ausgewählte Verzeichnis ist kein gültiges Git-Repository ('.git' Ordner fehlt).")
            return

        repo_name = os.path.basename(os.path.normpath(selected_dir))

        for repo in self.repositories:
            if repo['path'] == selected_dir:
                messagebox.showwarning("Warnung", "Dieses Repository wurde bereits hinzugefügt.")
                return

        # Repo zur Liste hinzufügen
        self.repositories.append({
            'name': repo_name,
            'path': selected_dir
        })

        # Hier Speichern ERZWINGEN
        self.save_repositories()

        self.populate_repos_listbox()
        self.set_status(f"Repository '{repo_name}' erfolgreich hinzugefügt.")

    def remove_repository(self):
        """Entfernt das ausgewählte Repository aus der Liste und löscht die lokale Kopie."""
        selection = self.repos_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie ein Repository zum Entfernen aus.")
            return
        index = selection[0]
        repo = self.repositories.pop(index)

        # Lösche die lokale Kopie des Repositories, falls vorhanden
        if os.path.exists(repo['path']):
            try:
                shutil.rmtree(repo['path'])
                self.set_status(f"Lokale Kopie des Repositories '{repo['name']}' gelöscht.")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Löschen der lokalen Kopie:\n{e}")

        self.populate_repos_listbox()
        self.save_repositories()
        self.set_status(f"Repository '{repo['name']}' entfernt.")
        self.populate_repos()  # Aktualisiere die Repository-Auswahl in der GUI

    def on_repo_select(self, event):
        """Handler für die Auswahl eines Repositories aus der Listbox."""
        selection = self.repos_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        repo = self.repositories[index]
        self.populate_repos(repo['path'])  # Aktualisiere das aktuelle Verzeichnis in der GUI
