# gui.py

import os
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import ttkbootstrap as tb

from pipeline_common import Pipeline, PipelineStep

from phoenixai.pipeline_analysis.pipeline_analysis_impl import analysis_actions
from phoenixai.pipeline_transformation.pipeline_transform_impl import transform_actions

from repository_manager import RepositoryManager
from navigation_manager import NavigationManager
from action_manager import ActionManager
from result_manager import ResultManager

class AnalyseGUI(tb.Window):
    def __init__(self):
        super().__init__(themename="flatly")  # Wählen Sie ein modernes Theme
        self.title("Analyse- und Transformations-Tool")
        self.geometry("1200x1000")  # Angepasst für mehr Platz links

        # Minimalgröße, damit das Layout nicht völlig bricht
        self.minsize(1200, 800)

        # Haupt-PanedWindow erstellen für linke und rechte Bereiche
        self.paned_window = tb.PanedWindow(self, orient=tk.HORIZONTAL, bootstyle="success")
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Linkes und rechtes Paneele erstellen
        self.left_frame = tb.Frame(self.paned_window, padding=10, bootstyle="light")
        self.right_frame = tb.Frame(self.paned_window, padding=10, bootstyle="light")

        # Paneele zum PanedWindow hinzufügen
        self.paned_window.add(self.left_frame, weight=1)
        self.paned_window.add(self.right_frame, weight=3)  # Rechte Seite erhält mehr Platz standardmäßig

        # Globale Variablen
        self.back_history = []
        self.forward_history = []
        self.current_directory = os.getcwd()
        self.selected_file = None

        # Ergebnisse sammeln
        self.results = []

        # Pipeline-TreeView vorbereiten (damit die Variable existiert)
        self.pipeline_tree = None

        # Pipeline erstellen mit Callback (vor `build_left_side()`, damit sie existiert)
        self.pipeline = Pipeline(None, step_callback=self.pipeline_step_completed)

        # Repository-Management wird durch RepositoryManager gehandhabt
        # Zunächst definieren wir die Variablen für ActionManager
        self.analysis_vars = {a_name: {"var": tk.BooleanVar(), "function": analysis_actions.get(a_name)} for a_name in analysis_actions.keys()}
        self.transform_vars = {t_name: {"var": tk.BooleanVar(), "function": transform_actions.get(t_name)} for t_name in transform_actions.keys()}

        columns = ("Script", "Ergebnis", "Status")
        self.results_tree = tb.Treeview(self.right_frame, columns=columns, show="headings", height=20, bootstyle="primary")
        self.results_tree.heading("Script", text="Script")
        self.results_tree.heading("Ergebnis", text="Ergebnis")
        self.results_tree.heading("Status", text="Status")
        self.results_tree.pack(fill="both", expand=True, padx=10, pady=10)

        # GUI-Elemente aufbauen
        self.build_left_side()
        self.build_right_side()

        # Nach dem Erstellen der TreeView setzen wir die Referenz in der Pipeline
        self.pipeline.treeview = self.pipeline_tree

        # Initiales Laden des aktuellen Verzeichnisses
        self.update_directory_list(
            directory=self.current_directory,
            add_to_history=False
        )

        # Statusleiste hinzufügen
        self.status_frame = tb.Frame(self, bootstyle="secondary")
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_label = tb.Label(self.status_frame, text="Bereit", anchor="w", font=("Helvetica", 10))
        self.status_label.pack(fill=tk.X, padx=10, pady=5)

        # Binden des Schließ-Events, um Repositories zu speichern
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Maus-Scrolling in der Dir-Listbox
        self.bind_all("<MouseWheel>", self.on_mouse_scroll)  # Windows und MacOS
        self.bind_all("<Button-4>", self.on_mouse_scroll)  # Linux
        self.bind_all("<Button-5>", self.on_mouse_scroll)  # Linux

    # ===================== Aufbau linker Bereich =====================
    def build_left_side(self):
        """
        Linker Bereich: Navigation, Aktionen, Pipeline-Anzeige, Repository Management
        """

        # Repository Management
        self.repo_manager = RepositoryManager(
            parent_frame=self.left_frame,
            set_status_callback=self.set_status,
            populate_repos_callback=self.on_repository_change
        )

        # Oberes Label: aktuelles Verzeichnis
        self.dir_label = tb.Label(
            self.left_frame,
            text=f"Aktuelles Verzeichnis: {self.current_directory}",
            anchor="w",
            font=("Helvetica", 12, "bold"),
            bootstyle="secondary"
        )
        self.dir_label.pack(fill="x", pady=(20,5), padx=10)

        # Frame für Navigation und Dateiliste
        nav_list_frame = tb.Frame(self.left_frame)
        nav_list_frame.pack(fill="both", expand=True, padx=10)

        # Navigation
        nav_frame = tb.Frame(nav_list_frame)
        nav_frame.pack(side="top", fill="x", pady=5)

        btn_up = tb.Button(nav_frame, text="⬆ Nach oben", command=self.navigate_up, bootstyle="outline-primary")
        btn_up.pack(side="left", padx=(0,10))

        btn_back = tb.Button(nav_frame, text="← Zurück", command=self.navigate_back, bootstyle="outline-primary")
        btn_back.pack(side="left", padx=(0,10))

        btn_fwd = tb.Button(nav_frame, text="→ Vorwärts", command=self.navigate_forward, bootstyle="outline-primary")
        btn_fwd.pack(side="left")

        # Liste
        list_frame = tb.Frame(nav_list_frame)
        list_frame.pack(side="top", fill="both", expand=True, pady=(5, 10))

        list_scroll = tb.Scrollbar(list_frame, orient="vertical")
        list_scroll.pack(side="right", fill="y")

        self.dir_listbox = tk.Listbox(list_frame, yscrollcommand=list_scroll.set, font=("Helvetica", 10))
        self.dir_listbox.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=5)

        list_scroll.config(command=self.dir_listbox.yview)

        self.dir_listbox.bind("<Double-Button-1>", self.on_list_double_click)

        # Initialisieren des NavigationManagers
        self.navigation_manager = NavigationManager(
            parent_frame=nav_list_frame,
            dir_label=self.dir_label,
            dir_listbox=self.dir_listbox,
            set_status_callback=self.set_status,
            update_directory_callback=self.update_directory_list
        )

        # Aktionen
        self.action_manager = ActionManager(
            parent_frame=self.left_frame,
            analysis_vars=self.analysis_vars,
            transform_vars=self.transform_vars,
            pipeline=self.pipeline,
            set_status_callback=self.set_status
        )

        # Pipeline
        pipeline_frame = tb.LabelFrame(self.left_frame, text="Pipeline Schritte", bootstyle="info")
        pipeline_frame.pack(fill="both", expand=False, pady=10, padx=10)

        self.pipeline_tree = tb.Treeview(
            pipeline_frame,
            columns=("Status", "Aktion", "Datei", "Duration"),
            show="headings",
            selectmode="browse",
            height=8
        )
        self.pipeline_tree.heading("Status", text="Status")
        self.pipeline_tree.heading("Aktion", text="Aktion")
        self.pipeline_tree.heading("Datei", text="Datei")
        self.pipeline_tree.heading("Duration", text="Duration")
        self.pipeline_tree.column("Status", width=100, anchor="center")
        self.pipeline_tree.column("Aktion", width=150, anchor="w")
        self.pipeline_tree.column("Datei", width=400, anchor="w")
        self.pipeline_tree.column("Duration", width=100, anchor="center")
        self.pipeline_tree.pack(side="left", fill="both", expand=True, padx=(0,5), pady=5)

        pipeline_scrollbar = tb.Scrollbar(pipeline_frame, orient="vertical", command=self.pipeline_tree.yview)
        self.pipeline_tree.configure(yscrollcommand=pipeline_scrollbar.set)
        pipeline_scrollbar.pack(side="right", fill="y")

        self.pipeline.treeview = self.pipeline_tree  # Pipeline bekommt ihr TreeView

        # Kontextmenü für die Pipeline
        self.pipeline_menu = tb.Menu(self, tearoff=0)
        self.pipeline_menu.add_command(
            label="Schritt entfernen",
            command=self.remove_pipeline_step
        )
        self.pipeline_tree.bind("<Button-3>", self.show_pipeline_menu_handler)

        run_btn = tb.Button(self.right_frame, text="Weiteren Schritt ausführen", command=self.run_next_step_button, bootstyle="success")
        run_btn.pack(pady=10, anchor="e", padx=10)

    # ===================== Aufbau rechter Bereich =====================
    def build_right_side(self):
        """
        Rechter Bereich:
        📊 Analyse-Ergebnisse & Empfehlungen
        """
        self.results_manager = ResultManager(
            parent_frame=self.right_frame,
            results_tree=self.results_tree,
            set_status_callback=self.set_status
        )

    # ===================== Repository Change Handler =====================
    def on_repository_change(self, new_directory):
        """Callback wenn ein Repository ausgewählt wird."""
        self.navigation_manager.update_directory_list(new_directory)

    # ===================== Navigation =====================
    def update_directory_list(self, directory, add_to_history=True):
        self.navigation_manager.update_directory_list(directory, add_to_history)

    def navigate_up(self):
        self.navigation_manager.navigate_up()

    def navigate_back(self):
        self.navigation_manager.navigate_back()

    def navigate_forward(self):
        self.navigation_manager.navigate_forward()

    # ===================== Pipeline / File Selection =====================
    def on_list_double_click(self, event):
        selection = self.dir_listbox.curselection()
        if not selection:
            return
        selected_item = self.dir_listbox.get(selection)
        path = os.path.join(self.navigation_manager.current_directory, selected_item).rstrip("/")
        if os.path.isdir(path):
            self.navigation_manager.update_directory_list(path)
        elif path.endswith(".py"):
            self.selected_file = path
            self.confirm_actions()

    def confirm_actions(self):
        """Bestätigt die Aktionen und fügt sie der Pipeline hinzu."""
        self.action_manager.confirm_actions(self.selected_file)

    def run_next_step_button(self):
        self.pipeline.run_next_step()

    def remove_pipeline_step(self):
        selected_item = self.pipeline_tree.selection()
        if not selected_item:
            return
        try:
            step_index = self.pipeline_tree.index(selected_item)  # Besser als int(selected_item[0]) - 1
            if 0 <= step_index < len(self.pipeline.steps):
                del self.pipeline.steps[step_index]
                self.pipeline.display_status()
                self.set_status(f"Schritt {step_index + 1} entfernt.")
        except Exception as e:
            tb.messagebox.show_error("Fehler", f"Ungültige Schritt-ID oder anderer Fehler: {e}")

    def show_pipeline_menu_handler(self, event):
        selected_item = self.pipeline_tree.identify_row(event.y)
        if selected_item:
            self.pipeline_tree.selection_set(selected_item)
            self.pipeline_menu.post(event.x_root, event.y_root)

    # ===================== Maus-Scroll =====================
    def on_mouse_scroll(self, event):
        """Lässt normales Scrollen zu, verhindert aber die Navigation durch das Verzeichnis."""
        widget = event.widget  # Das Widget, über dem die Maus ist

        # Nur scrollen, wenn es sich um eine Listbox, Treeview oder ein Scroll-Widget handelt
        if isinstance(widget, (tk.Listbox, tb.Treeview, ScrolledText)):
            if hasattr(event, 'delta'):  # Windows und MacOS
                widget.yview_scroll(-1 if event.delta > 0 else 1, "units")
            elif event.num == 4:  # Linux Scroll Up
                widget.yview_scroll(-1, "units")
            elif event.num == 5:  # Linux Scroll Down
                widget.yview_scroll(1, "units")

    # ===================== Pipeline Callback =====================
    def pipeline_step_completed(self, step: PipelineStep):
        """
        Callback-Funktion, die von der Pipeline nach jedem Schritt aufgerufen wird.
        Aktualisiert die Ergebnisse in der GUI.
        """
        if step.name in analysis_actions:
            # Beispiel: Name Checker generiert einen Report
            # Hier sollten Sie den tatsächlichen Report-Pfad erhalten, falls möglich
            fake_report_path = "name_checker_report.md"  # Dies sollte durch den tatsächlichen Report-Pfad ersetzt werden
            step_result = f"Report: {fake_report_path}"
        else:
            step_result = "OK"
        self.results_manager.update_results_tree(step.name, step_result, step.status)

    # ===================== Rechts: Analyse-Ergebnisse-Funktionen =====================
    # Diese Funktionen werden nun vom ResultManager gehandhabt

    # ===================== Statusleiste =====================
    def set_status(self, message):
        """Aktualisiert die Statusleiste mit der angegebenen Nachricht."""
        self.status_label.config(text=message)

    # ===================== Laden und Speichern der Repositories =====================
    # Diese Funktionen werden nun vom RepositoryManager gehandhabt

    def on_close(self):
        """Handler für das Schließen des Fensters."""
        self.repo_manager.save_repositories()
        self.destroy()

if __name__ == "__main__":
    # Starten der GUI
    app = AnalyseGUI()
    app.mainloop()
