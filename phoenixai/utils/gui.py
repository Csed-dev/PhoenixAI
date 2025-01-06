# gui.py

import os
import json
import time
import tkinter as tk
from tkinter import ttk, messagebox, END, filedialog
from tkinter.scrolledtext import ScrolledText

# Importieren der Pipeline-Klassen aus pipeline_common.py
from pipeline_common import Pipeline, PipelineStep

# Importieren der Aktionen aus den entsprechenden Modulen
from phoenixai.pipeline_analysis.pipeline_analysis_impl import analysis_actions
from phoenixai.pipeline_transformation.pipeline_transform_impl import action_functions as transform_actions

class AnalyseGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Analyse- und Transformations-Tool")
        self.geometry("1200x800")

        # Minimalgröße, damit das Layout nicht völlig bricht
        self.minsize(1500, 600)

        # Haupt-PanedWindow erstellen für linke und rechte Bereiche
        self.paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Linkes und rechtes Paneele erstellen
        self.left_frame = ttk.Frame(self.paned_window, padding=5)
        self.right_frame = ttk.Frame(self.paned_window, padding=5)

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

    # ===================== Aufbau linker Bereich =====================
    def build_left_side(self):
        """
        Linker Bereich: Navigation, Aktionen, Pipeline-Anzeige
        """

        # Oberes Label: aktuelles Verzeichnis
        self.dir_label = ttk.Label(
            self.left_frame,
            text=f"Aktuelles Verzeichnis: {self.current_directory}",
            anchor="w",
            font=("Helvetica", 12, "bold")
        )
        self.dir_label.pack(fill="x", pady=(10,5))

        # Frame für Navigation und Dateiliste
        nav_list_frame = ttk.Frame(self.left_frame)
        nav_list_frame.pack(fill="both", expand=True)

        # Navigation
        nav_frame = ttk.Frame(nav_list_frame)
        nav_frame.pack(side="top", fill="x", pady=5)

        btn_up = ttk.Button(nav_frame, text="⬆ Nach oben", command=self.navigate_up)
        btn_up.pack(side="left", padx=(0,10))

        btn_back = ttk.Button(nav_frame, text="← Zurück", command=self.navigate_back)
        btn_back.pack(side="left", padx=(0,10))

        btn_fwd = ttk.Button(nav_frame, text="→ Vorwärts", command=self.navigate_forward)
        btn_fwd.pack(side="left")

        # Liste
        list_frame = ttk.Frame(nav_list_frame)
        list_frame.pack(side="top", fill="both", expand=True, pady=(5,10))

        list_scroll = ttk.Scrollbar(list_frame, orient="vertical")
        list_scroll.pack(side="right", fill="y")

        self.dir_listbox = tk.Listbox(list_frame, yscrollcommand=list_scroll.set, font=("Courier", 10))
        self.dir_listbox.pack(side="left", fill="both", expand=True)
        list_scroll.config(command=self.dir_listbox.yview)

        self.dir_listbox.bind("<Double-Button-1>", self.on_list_double_click)

        # Aktionen
        actions_frame = ttk.LabelFrame(self.left_frame, text="Aktionen auswählen")
        actions_frame.pack(fill="x", pady=5)

        # Analyse
        analysis_frame = ttk.LabelFrame(actions_frame, text="Analyse")
        analysis_frame.pack(side="top", fill="x", padx=5, pady=5)

        self.analysis_vars = {}
        for a_name in analysis_actions.keys():
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(analysis_frame, text=a_name, variable=var)
            cb.pack(side="left", padx=5, pady=2)
            self.analysis_vars[a_name] = var

        # Transformation
        transformation_frame = ttk.LabelFrame(actions_frame, text="Transformation")
        transformation_frame.pack(side="top", fill="x", padx=5, pady=5)

        self.transform_vars = {}
        for t_name in transform_actions.keys():
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(transformation_frame, text=t_name, variable=var)
            cb.pack(side="left", padx=5, pady=2)
            self.transform_vars[t_name] = var

        # Pipeline
        pipeline_frame = ttk.LabelFrame(self.left_frame, text="Pipeline Schritte")
        pipeline_frame.pack(fill="both", expand=False, pady=5)

        self.pipeline_tree = ttk.Treeview(
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
        self.pipeline_tree.column("Status", width=80, anchor="center")
        self.pipeline_tree.column("Aktion", width=80, anchor="w")
        self.pipeline_tree.column("Datei", width=300, anchor="w")
        self.pipeline_tree.column("Duration", width=80, anchor="center")
        self.pipeline_tree.pack(side="left", fill="both", expand=True)

        pipeline_scrollbar = ttk.Scrollbar(pipeline_frame, orient="vertical", command=self.pipeline_tree.yview)
        self.pipeline_tree.configure(yscrollcommand=pipeline_scrollbar.set)
        pipeline_scrollbar.pack(side="right", fill="y")

        self.pipeline.treeview = self.pipeline_tree  # Pipeline bekommt ihr TreeView

        self.pipeline_menu = tk.Menu(self, tearoff=0)
        self.pipeline_menu.add_command(
            label="Schritt entfernen",
            command=self.remove_pipeline_step
        )
        self.pipeline_tree.bind("<Button-3>", self.show_pipeline_menu_handler)

        run_btn = ttk.Button(self.left_frame, text="Weiteren Schritt ausführen", command=self.run_next_step_button)
        run_btn.pack(pady=5, anchor="e")

        # Maus-Scrolling in der Dir-Listbox
        self.bind_all("<Button-4>", self.on_mouse_button)
        self.bind_all("<Button-5>", self.on_mouse_button)

    # ===================== Aufbau rechter Bereich =====================
    def build_right_side(self):
        """
        Rechter Bereich:
        📊 Analyse-Ergebnisse & Empfehlungen
        """
        ergebnisse_label = ttk.Label(
            self.right_frame,
            text="📊 Analyse-Ergebnisse & Empfehlungen",
            font=("Helvetica", 12, "bold")
        )
        ergebnisse_label.pack(anchor="w", pady=(0,5))

        # Treeview für Ergebnisse
        columns = ("Script", "Ergebnis", "Status")
        self.results_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=20)
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=150, anchor="center")
        self.results_tree.pack(fill="both", expand=True, pady=5)

        # Buttons für Details, Vergleich, Export
        ergebnisse_buttons = ttk.Frame(self.right_frame)
        ergebnisse_buttons.pack(fill="x", pady=5)

        details_button = ttk.Button(ergebnisse_buttons, text="Details anzeigen", command=self.show_details)
        details_button.pack(side="left", fill="x", expand=True, padx=2)

        compare_button = ttk.Button(ergebnisse_buttons, text="Vergleichsansicht", command=self.compare_results)
        compare_button.pack(side="left", fill="x", expand=True, padx=2)

        export_button = ttk.Button(ergebnisse_buttons, text="Exportieren", command=self.export_results)
        export_button.pack(side="left", fill="x", expand=True, padx=2)

    # ===================== Navigation =====================
    def update_directory_list(self, directory, add_to_history=True):
        if add_to_history:
            self.back_history.append(self.current_directory)
        if add_to_history and self.current_directory != directory:
            self.forward_history.clear()

        self.current_directory = directory
        self.dir_listbox.delete(0, END)

        items = self.list_directory_contents(directory)
        for item in items:
            self.dir_listbox.insert(END, item)

        self.dir_label.config(text=f"Aktuelles Verzeichnis: {directory}")
        self.pipeline.reset()

    def list_directory_contents(self, directory):
        """Listet alle Dateien und Ordner im Verzeichnis auf."""
        contents = []
        for item in os.listdir(directory):
            full_path = os.path.join(directory, item)
            if os.path.isdir(full_path):
                contents.append(f"{item}/")
            elif item.endswith(".py"):
                contents.append(item)
        return contents

    def navigate_up(self):
        parent_directory = os.path.dirname(self.current_directory)
        if parent_directory != self.current_directory:
            self.update_directory_list(parent_directory)
        else:
            messagebox.showinfo("Info", "Sie befinden sich bereits im Wurzelverzeichnis.")

    def navigate_back(self):
        if self.back_history:
            self.forward_history.append(self.current_directory)
            previous_directory = self.back_history.pop()
            self.update_directory_list(previous_directory, add_to_history=False)
        else:
            messagebox.showinfo("Info", "Keine vorherigen Verzeichnisse.")

    def navigate_forward(self):
        if self.forward_history:
            self.back_history.append(self.current_directory)
            next_directory = self.forward_history.pop()
            self.update_directory_list(next_directory, add_to_history=False)
        else:
            messagebox.showinfo("Info", "Keine weiteren Verzeichnisse.")

    # ===================== Pipeline / File Selection =====================
    def on_list_double_click(self, event):
        selection = self.dir_listbox.curselection()
        if not selection:
            return
        selected_item = self.dir_listbox.get(selection)
        path = os.path.join(self.current_directory, selected_item).rstrip("/")
        if os.path.isdir(path):
            self.update_directory_list(path)
        elif path.endswith(".py"):
            self.selected_file = path
            self.confirm_actions()

    def confirm_actions(self):
        chosen_analysis = [name for name, var in self.analysis_vars.items() if var.get()]
        chosen_transform = [name for name, var in self.transform_vars.items() if var.get()]
        if (not chosen_analysis) and (not chosen_transform):
            messagebox.showwarning("Warnung", "Bitte wähle mindestens eine Aktion (Analyse oder Transform).")
            return
        if not self.selected_file:
            messagebox.showwarning("Warnung", "Bitte wähle eine .py Datei aus.")
            return

        for a in chosen_analysis:
            func = analysis_actions.get(a)
            if func:
                self.pipeline.add_step(a, func, self.selected_file)

        for t in chosen_transform:
            func = transform_actions.get(t)
            if func:
                self.pipeline.add_step(t, func, self.selected_file)

    def run_next_step_button(self):
        self.pipeline.run_next_step()

    def remove_pipeline_step(self):
        selected_item = self.pipeline_tree.selection()
        if not selected_item:
            return
        try:
            step_index = int(selected_item[0]) - 1
            if 0 <= step_index < len(self.pipeline.steps):
                del self.pipeline.steps[step_index]
                self.pipeline.display_status()
        except ValueError:
            messagebox.showerror("Fehler", "Ungültige Schritt-ID.")

    def show_pipeline_menu_handler(self, event):
        selected_item = self.pipeline_tree.identify_row(event.y)
        if selected_item:
            self.pipeline_tree.selection_set(selected_item)
            self.pipeline_menu.post(event.x_root, event.y_root)

    # ===================== Maus-Scroll =====================
    def on_mouse_button(self, event):
        # Linux-Scroll-Events
        if event.num == 4:  # scrolled up
            self.navigate_back()
        elif event.num == 5:  # scrolled down
            self.navigate_forward()

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
        self.update_results_tree(step.name, step_result, step.status)

    # ===================== Rechts: Analyse-Ergebnisse-Funktionen =====================
    def show_details(self):
        selected_item = self.results_tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Bitte wählen Sie ein Ergebnis aus.")
            return
        item = self.results_tree.item(selected_item)
        script, result, status = item["values"]

        # Spezieller Fall: "Name Checker"
        if script == "Name Checker" and "Report:" in result:
            report_path = result.split(": ")[1]
            try:
                with open(report_path, "r", encoding="utf-8") as f:
                    report_content = f.read()
                detail_window = tk.Toplevel(self)
                detail_window.title(f"Details zu {script}")
                detail_window.geometry("800x600")

                detail_label = ttk.Label(detail_window, text=f"Details zu {script}", font=("Helvetica", 12, "bold"))
                detail_label.pack(anchor="w", pady=10, padx=10)

                detail_text = ScrolledText(detail_window, state="normal")
                detail_text.pack(fill="both", expand=True, padx=10, pady=5)
                detail_text.insert(tk.END, report_content)
                detail_text.config(state="disabled")
            except FileNotFoundError:
                messagebox.showerror("Fehler", f"Report-Datei nicht gefunden: {report_path}")
        else:
            # Standard-Details
            detail_window = tk.Toplevel(self)
            detail_window.title(f"Details zu {script}")
            detail_window.geometry("400x300")

            detail_label = ttk.Label(detail_window, text=f"Details zu {script}", font=("Helvetica", 12, "bold"))
            detail_label.pack(anchor="w", pady=10, padx=10)

            detail_text = ScrolledText(detail_window, state="normal")
            detail_text.pack(fill="both", expand=True, padx=10, pady=5)
            detail_text.insert(
                tk.END,
                f"Ergebnis: {result}\nStatus: {status}\n\nWeitere Details können hier angezeigt werden."
            )
            detail_text.config(state="disabled")

    def compare_results(self):
        # Placeholder
        messagebox.showinfo("Info", "Vergleichsansicht ist noch nicht implementiert.")

    def export_results(self):
        if not self.results:
            messagebox.showinfo("Info", "Keine Ergebnisse zum Exportieren.")
            return
        export_window = tk.Toplevel(self)
        export_window.title("Exportieren")
        export_window.geometry("300x200")

        export_label = ttk.Label(export_window, text="Wählen Sie ein Exportformat:", font=("Helvetica", 12, "bold"))
        export_label.pack(pady=10)

        json_button = ttk.Button(export_window, text="Als JSON exportieren", command=lambda: self.export_as("json"))
        json_button.pack(fill="x", padx=20, pady=5)

        csv_button = ttk.Button(export_window, text="Als CSV exportieren", command=lambda: self.export_as("csv"))
        csv_button.pack(fill="x", padx=20, pady=5)

        md_button = ttk.Button(export_window, text="Als Markdown exportieren", command=lambda: self.export_as("md"))
        md_button.pack(fill="x", padx=20, pady=5)

    def export_as(self, format):
        file_path = filedialog.asksaveasfilename(
            defaultextension=f".{format}",
            filetypes=[(f"{format.upper()} Dateien", f"*.{format}")]
        )
        if not file_path:
            return
        try:
            if format == "json":
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(self.results, f, ensure_ascii=False, indent=4)
            elif format == "csv":
                import csv
                with open(file_path, "w", newline='', encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=["Script", "Ergebnis", "Status"])
                    writer.writeheader()
                    writer.writerows(self.results)
            elif format == "md":
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("| Skript | Ergebnis | Status |\n")
                    f.write("|---|---|---|\n")
                    for res in self.results:
                        f.write(f"| {res['Script']} | {res['Ergebnis']} | {res['Status']} |\n")
            messagebox.showinfo("Erfolg", f"Ergebnisse erfolgreich als {format.upper()} exportiert.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Beim Exportieren ist ein Fehler aufgetreten:\n{e}")

    def update_results_tree(self, script: str, result: str, status: str):
        """
        Fügt einen Eintrag in der Ergebnis-TreeView hinzu
        und speichert ihn in self.results (als Liste von Dicts).
        """
        self.results_tree.insert("", tk.END, values=(script, result, status))
        self.results.append({"Script": script, "Ergebnis": result, "Status": status})


if __name__ == "__main__":
    # Starten der GUI
    app = AnalyseGUI()
    app.mainloop()
