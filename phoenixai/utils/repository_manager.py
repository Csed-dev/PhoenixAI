import os
import shutil
import pathlib
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
        self.selection = None
        self.selected_repo = None

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

        # Container für die Buttons erstellen
        button_frame = tb.Frame(repo_frame)
        button_frame.pack(padx=0, pady=0, anchor="w")  # Pack bleibt für das Frame erhalten

        # Button zum Hinzufügen eines bestehenden Repos
        add_existing_repo_button = tb.Button(button_frame, text="Bestehendes Repository hinzufügen",
                                             command=self.add_existing_repository, bootstyle="primary")
        add_existing_repo_button.grid(row=0, column=0, padx=5, pady=5)

        # Button zum Hinzufügen eines bestehenden Projekts (rechts daneben)
        add_existing_project_button = tb.Button(button_frame, text="Bestehendes Projekt hinzufügen",
                                                command=self.add_existing_project, bootstyle="primary")
        add_existing_project_button.grid(row=0, column=1, padx=5, pady=5)

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

        # Container für die Buttons erstellen
        button_frame = tb.Frame(repo_frame)
        button_frame.pack(padx=0, pady=0, anchor="e")  # Pack bleibt für das Frame erhalten

        # Button zum Entfernen des ausgewählten Repos
        remove_repo_button = tb.Button(
            button_frame,
            text="Repository entfernen",
            command=self.remove_repository,
            bootstyle="danger-outline")
        #remove_repo_button.pack(padx=5, pady=5, anchor="w")
        remove_repo_button.grid(row=0, column=0, padx=5, pady=5)

        run_analyzing_pipeline_btn = tb.Button(
            button_frame,
            text="Starte Analyse Pipeline",
            command=self.run_analyze_repo,
            bootstyle="success")
        run_analyzing_pipeline_btn.grid(row=0, column=1, padx=10, pady=10)

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

    def add_existing_project(self):
        """Hinzufügen eines bestehenden lokalen Python Projekts."""
        selected_dir = filedialog.askdirectory(title="Bestehendes Projekt auswählen")
        if not selected_dir:
            return

        project_name = os.path.basename(os.path.normpath(selected_dir))

        for repo in self.repositories:
            if repo['path'] == selected_dir:
                messagebox.showwarning("Warnung", "Dieses Projekt wurde bereits hinzugefügt.")
                return

        # Repo zur Liste hinzufügen
        self.repositories.append({
            'name': project_name,
            'path': selected_dir
        })

        # Hier Speichern ERZWINGEN
        self.save_repositories()

        self.populate_repos_listbox()
        self.set_status(f"Projekt '{project_name}' erfolgreich hinzugefügt.")

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
        """Entfernt das ausgewählte Repository aus der Liste."""
        self.selection = self.repos_listbox.curselection()
        if not self.selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie ein Repository zum Entfernen aus.")
            return
        index = self.selection[0]
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
        self.selection = self.repos_listbox.curselection()
        if not self.selection:
            self.selected_repo = None
            return
        index = self.selection[0]
        self.selected_repo = self.repositories[index]
        self.populate_repos(self.selected_repo['path'])  # Aktualisiere das aktuelle Verzeichnis in der GUI

    def run_analyze_repo(self):
        if not self.selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie ein Repository zum Analysieren aus.")
            return

        self.add_dockerfile_and_startup_to_project(self.selected_repo['path'])

        # Change directory to the destination path
        original_dir = os.getcwd()
        os.chdir(str(self.selected_repo['path']))

        try:
            # Build the Docker image
            print("Building Docker image...")
            print("original_dir:" + str(original_dir))
            print("current_dir:" + str(pathlib.Path().resolve()))
            subprocess.run(["docker", "build", "--no-cache", "-t", self.selected_repo['name'], "."], check=True)

            # Run the Docker container with the correct volume mapping
            print("Running Docker container...")

            # Get the absolute path in a cross-platform way
            current_dir = str(pathlib.Path().resolve())

            # Run the Docker container
            subprocess.run([
                "docker", "run", "--rm",
                "-v", f"{current_dir}:/app",
                self.selected_repo['name']
            ], check=True)

            print("Docker container executed successfully")

        except subprocess.CalledProcessError as e:
            print(f"Error executing Docker command: {e}")
            messagebox.showwarning("Error", "Error executing Docker command: {e}")
        except Exception as e:
            print(f"Error: {e}")
            messagebox.showwarning("Error", f"Error: {e}")
        finally:
            # Change back to the original directory
            os.chdir(original_dir)


    @staticmethod
    def add_dockerfile_and_startup_to_project(destination_path):
        # Get the current absolute path
        current_path = pathlib.Path().resolve()

        # Navigate to the project root by finding 'phoenixai' directory
        project_root = current_path
        while project_root.name != 'phoenixai' and project_root.parent != project_root:
            project_root = project_root.parent

        # If we couldn't find 'phoenixai' directory, raise an error
        if project_root.name != 'phoenixai':
            raise FileNotFoundError("Could not locate the 'phoenixai' directory in the path hierarchy")

        # Path to the docker files
        docker_files_dir = project_root / "docker_standard" / "python3_procedure"
        # TODO: Process for python2_procedure (which currently does not exist) needs to be implemented in the future

        # Files to copy
        dockerfile = docker_files_dir / "Dockerfile"
        startup_script = docker_files_dir / "startup.py"

        # Ensure destination directory exists
        destination_path = pathlib.Path(destination_path)
        destination_path.mkdir(parents=True, exist_ok=True)

        # Copy the files only if they don't already exist
        dest_dockerfile = destination_path / "Dockerfile"
        dest_startup = destination_path / "startup.py"

        if not dest_dockerfile.exists():
            shutil.copyfile(dockerfile, dest_dockerfile)

        if not dest_startup.exists():
            shutil.copyfile(startup_script, dest_startup)