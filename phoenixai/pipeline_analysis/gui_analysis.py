import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import threading
import json
import os

from name_checker import NameChecker

class AnalysisApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Analyse- und Empfehlungssystem")
        self.geometry("825x800")
        self.resizable(False, False)

        # Setze Theme analog zum Transformations-Tool
        style = ttk.Style(self)
        available_themes = style.theme_names()
        if "vista" in available_themes:
            style.theme_use("vista")
        else:
            style.theme_use("default")

        # Initialisiere Variablen
        self.selected_files = []
        self.pipeline_scripts = [
            {"name": "Skript 1", "enabled": tk.BooleanVar(value=True)},
            {"name": "Skript 2", "enabled": tk.BooleanVar(value=True)},
            {"name": "Name Checker", "enabled": tk.BooleanVar(value=True)},
            {"name": "Skript 4", "enabled": tk.BooleanVar(value=True)},
        ]
        self.current_step = 0
        self.results = []
        self.log_messages = []
        self.is_running = False

        # Hauptcontainer
        self.main_frame = ttk.Frame(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.create_widgets()

    def create_widgets(self):
        """
        Erzeugt die GUI-Elemente in einer vertikalen Anordnung,
        ähnlich dem Transformations-Tool.
        """
        # ============ Dateiauswahl (1. Bereich) ============
        self.dateiauswahl_frame = ttk.LabelFrame(
            self.main_frame, text="Dateien & Ordner auswählen", padding=(10, 10)
        )
        self.dateiauswahl_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10,5))

        drop_area = tk.Label(
            self.dateiauswahl_frame,
            text="Drag & Drop Dateien hier",
            relief="ridge",
            borderwidth=2,
            width=60,
            height=3,
        )
        drop_area.grid(row=0, column=0, columnspan=2, pady=5, sticky="ew")
        drop_area.bind("<Button-1>", self.browse_files)

        browse_button = ttk.Button(
            self.dateiauswahl_frame, text="Durchsuchen", command=self.browse_files
        )
        browse_button.grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")

        self.files_listbox = tk.Listbox(self.dateiauswahl_frame, height=8)
        self.files_listbox.grid(row=2, column=0, columnspan=2, sticky="ew")

        # ============ Pipeline Manager (2. Bereich) ============
        self.pipeline_frame = ttk.LabelFrame(
            self.main_frame, text="Pipeline-Manager", padding=(10, 10)
        )
        self.pipeline_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(5,5))

        # Checkbuttons für Skripte
        row_idx = 0
        for script in self.pipeline_scripts:
            cb = ttk.Checkbutton(
                self.pipeline_frame, text=script["name"], variable=script["enabled"]
            )
            cb.grid(row=row_idx, column=0, sticky="w")
            row_idx += 1

        # Buttons zum Verschieben
        reorder_frame = ttk.Frame(self.pipeline_frame)
        reorder_frame.grid(row=row_idx, column=0, sticky="ew", pady=5)

        move_up_button = ttk.Button(
            reorder_frame, text="🡅 Nach oben", command=lambda: self.move_script(-1)
        )
        move_up_button.pack(side="left", expand=True, fill="x", padx=2)

        move_down_button = ttk.Button(
            reorder_frame, text="🡇 Nach unten", command=lambda: self.move_script(1)
        )
        move_down_button.pack(side="left", expand=True, fill="x", padx=2)

        # ============ Analyse-Steuerung & Log (3. Bereich) ============
        self.steuerung_frame = ttk.LabelFrame(
            self.main_frame, text="Analyse-Steuerung & Live-Status", padding=(10, 10)
        )
        self.steuerung_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5,5))

        run_step_button = ttk.Button(
            self.steuerung_frame, text="Analyse starten", command=self.start_analysis
        )
        run_step_button.grid(row=0, column=0, sticky="ew", pady=5)

        self.log_label = ttk.Label(self.steuerung_frame, text="Live-Log der Analyse:")
        self.log_label.grid(row=1, column=0, sticky="w")

        self.log_text = ScrolledText(self.steuerung_frame, height=10, state="disabled")
        self.log_text.grid(row=2, column=0, sticky="ew")

        # Fortschrittsanzeige
        self.progress_label = ttk.Label(self.steuerung_frame, text="Fortschritt:")
        self.progress_label.grid(row=3, column=0, sticky="w", pady=(5,0))

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.steuerung_frame, variable=self.progress_var, maximum=100
        )
        self.progress_bar.grid(row=4, column=0, sticky="ew", pady=5)

        self.progress_percent = ttk.Label(self.steuerung_frame, text="0%")
        self.progress_percent.grid(row=5, column=0, sticky="e")

        # ============ Analyse-Ergebnisse (4. Bereich) ============
        self.ergebnisse_frame = ttk.LabelFrame(
            self.main_frame, text="Analyse-Ergebnisse & Empfehlungen", padding=(10, 10)
        )
        self.ergebnisse_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=(5,5))
        self.main_frame.rowconfigure(3, weight=1)  # Ergebnisse können sich ausdehnen

        columns = ("Script", "Ergebnis", "Status")
        self.results_tree = ttk.Treeview(
            self.ergebnisse_frame, columns=columns, show="headings"
        )
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=150, anchor="center")
        self.results_tree.grid(row=0, column=0, columnspan=3, sticky="nsew")

        tree_scrollbar = ttk.Scrollbar(
            self.ergebnisse_frame, orient="vertical", command=self.results_tree.yview
        )
        self.results_tree.configure(yscrollcommand=tree_scrollbar.set)
        tree_scrollbar.grid(row=0, column=3, sticky="ns")

        # Buttons für Details, Vergleich und Export
        details_button = ttk.Button(
            self.ergebnisse_frame, text="Details anzeigen", command=self.show_details
        )
        details_button.grid(row=1, column=0, sticky="ew", padx=2, pady=5)

        compare_button = ttk.Button(
            self.ergebnisse_frame, text="Vergleichsansicht", command=self.compare_results
        )
        compare_button.grid(row=1, column=1, sticky="ew", padx=2, pady=5)

        export_button = ttk.Button(
            self.ergebnisse_frame, text="Exportieren", command=self.export_results
        )
        export_button.grid(row=1, column=2, sticky="ew", padx=2, pady=5)

    # ==================== Funktionen für Links ====================
    def browse_files(self, event=None):
        file_paths = filedialog.askopenfilenames(
            title="Dateien auswählen", filetypes=[("Python Dateien", "*.py")]
        )
        if file_paths:
            for path in file_paths:
                if path not in self.selected_files:
                    self.selected_files.append(path)
                    self.files_listbox.insert(tk.END, path)

    def move_script(self, direction):
        scripts = [s for s in self.pipeline_scripts if s["enabled"].get()]
        if not scripts:
            return
        selected_script = "Name Checker"
        selected_index = next(
            (i for i, s in enumerate(self.pipeline_scripts) if s["name"] == selected_script),
            None,
        )
        if selected_index is None:
            return
        new_index = selected_index + direction
        if 0 <= new_index < len(self.pipeline_scripts):
            self.pipeline_scripts[selected_index], self.pipeline_scripts[new_index] = (
                self.pipeline_scripts[new_index],
                self.pipeline_scripts[selected_index],
            )
            for widget in self.pipeline_frame.winfo_children():
                widget.destroy()
            row_idx = 0
            for script in self.pipeline_scripts:
                cb = ttk.Checkbutton(
                    self.pipeline_frame, text=script["name"], variable=script["enabled"]
                )
                cb.grid(row=row_idx, column=0, sticky="w")
                row_idx += 1
            reorder_frame = ttk.Frame(self.pipeline_frame)
            reorder_frame.grid(row=row_idx, column=0, sticky="ew", pady=5)
            move_up_button = ttk.Button(
                reorder_frame,
                text="🡅 Nach oben",
                command=lambda: self.move_script(-1),
            )
            move_up_button.pack(side="left", expand=True, fill="x", padx=2)

            move_down_button = ttk.Button(
                reorder_frame,
                text="🡇 Nach unten",
                command=lambda: self.move_script(1),
            )
            move_down_button.pack(side="left", expand=True, fill="x", padx=2)

    # ==================== Analyse-Funktionen ====================
    def start_analysis(self):
        if self.is_running:
            messagebox.showwarning("Warnung", "Eine Analyse läuft bereits.")
            return
        if not self.selected_files:
            messagebox.showwarning("Warnung", "Bitte wählen Sie mindestens eine Datei aus.")
            return
        self.is_running = True
        self.progress_var.set(0)
        self.progress_percent.config(text="0%")
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")
        self.results_tree.delete(*self.results_tree.get_children())
        self.results = []
        self.current_step = 0

        # Starte die Analyse in einem separaten Thread
        threading.Thread(target=self.run_analysis, daemon=True).start()

    def run_analysis(self):
        total_steps = len(self.selected_files) * 3
        current_step = 0

        for file_path in self.selected_files:
            checker = NameChecker(file_path)
            checker.generate_report()
            checker.save_report("name_checker_report.md")

            self.results.append(
                {
                    "Script": "Name Checker",
                    "Ergebnis": "Report generiert: name_checker_report.md",
                    "Status": "✅ OK",
                }
            )
            self.update_results_tree(
                "Name Checker", "Report generiert: name_checker_report.md", "✅ OK"
            )

            current_step += 3
            progress = (current_step / total_steps) * 100
            self.update_progress("Fortschritt", progress, "Analyse fortschreitet...")

        self.is_running = False
        self.update_progress_final()

    def update_progress(self, phase: str, progress: float, message: str):
        self.log_message(f"[{phase}] {message}")
        self.progress_var.set(progress)
        self.progress_percent.config(text=f"{int(progress)}%")

    def update_progress_final(self):
        self.progress_var.set(100)
        self.progress_percent.config(text="100%")
        self.log_message("✅ Alle Analysen abgeschlossen.")

    def log_message(self, message: str):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state="disabled")
        self.log_text.see(tk.END)

    def update_results_tree(self, script: str, result: str, status: str):
        self.results_tree.insert("", tk.END, values=(script, result, status))

    # ==================== Funktionen für Ergebnisse ====================
    def show_details(self):
        selected_item = self.results_tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Bitte wählen Sie ein Ergebnis aus.")
            return
        item = self.results_tree.item(selected_item)
        script, result, status = item["values"]
        if script == "Name Checker":
            report_path = result.split(": ")[1]
            try:
                with open(report_path, "r", encoding="utf-8") as f:
                    report_content = f.read()
                detail_window = tk.Toplevel(self)
                detail_window.title(f"Details zu {script}")
                detail_window.geometry("800x600")
                detail_window.resizable(False, False)

                detail_label = ttk.Label(
                    detail_window, text=f"Details zu {script}", font=("Helvetica", 12, "bold")
                )
                detail_label.pack(anchor="w", pady=10, padx=10)

                detail_text = ScrolledText(detail_window, state="normal")
                detail_text.pack(fill="both", expand=True, padx=10, pady=5)
                detail_text.insert(tk.END, report_content)
                detail_text.config(state="disabled")
            except FileNotFoundError:
                messagebox.showerror("Fehler", f"Report-Datei nicht gefunden: {report_path}")
        else:
            detail_window = tk.Toplevel(self)
            detail_window.title(f"Details zu {script}")
            detail_window.geometry("400x300")
            detail_window.resizable(False, False)

            detail_label = ttk.Label(
                detail_window, text=f"Details zu {script}", font=("Helvetica", 12, "bold")
            )
            detail_label.pack(anchor="w", pady=10, padx=10)

            detail_text = ScrolledText(detail_window, state="normal")
            detail_text.pack(fill="both", expand=True, padx=10, pady=5)
            detail_text.insert(
                tk.END,
                f"Ergebnis: {result}\nStatus: {status}\n\nWeitere Details können hier angezeigt werden.",
            )
            detail_text.config(state="disabled")

    def compare_results(self):
        messagebox.showinfo("Info", "Vergleichsansicht ist noch nicht implementiert.")

    def export_results(self):
        if not self.results:
            messagebox.showinfo("Info", "Keine Ergebnisse zum Exportieren.")
            return
        export_window = tk.Toplevel(self)
        export_window.title("Exportieren")
        export_window.geometry("300x200")
        export_window.resizable(False, False)

        export_label = ttk.Label(
            export_window, text="Wählen Sie ein Exportformat:", font=("Helvetica", 12, "bold")
        )
        export_label.pack(pady=10)

        json_button = ttk.Button(
            export_window,
            text="Als JSON exportieren",
            command=lambda: self.export_as("json"),
        )
        json_button.pack(fill="x", padx=20, pady=5)

        csv_button = ttk.Button(
            export_window,
            text="Als CSV exportieren",
            command=lambda: self.export_as("csv"),
        )
        csv_button.pack(fill="x", padx=20, pady=5)

        md_button = ttk.Button(
            export_window,
            text="Als Markdown exportieren",
            command=lambda: self.export_as("md"),
        )
        md_button.pack(fill="x", padx=20, pady=5)

    def export_as(self, format):
        file_path = filedialog.asksaveasfilename(
            defaultextension=f".{format}",
            filetypes=[(f"{format.upper()} Dateien", f"*.{format}")],
        )
        if not file_path:
            return
        try:
            if format == "json":
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(self.results, f, ensure_ascii=False, indent=4)
            elif format == "csv":
                import csv

                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(
                        f, fieldnames=["Script", "Ergebnis", "Status"]
                    )
                    writer.writeheader()
                    writer.writerows(self.results)
            elif format == "md":
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("| Skript | Ergebnis | Status |\n")
                    f.write("|---|---|---|\n")
                    for res in self.results:
                        f.write(
                            f"| {res['Script']} | {res['Ergebnis']} | {res['Status']} |\n"
                        )
            messagebox.showinfo(
                "Erfolg", f"Ergebnisse erfolgreich als {format.upper()} exportiert."
            )
        except Exception as e:
            messagebox.showerror(
                "Fehler", f"Beim Exportieren ist ein Fehler aufgetreten:\n{e}"
            )

if __name__ == "__main__":
    app = AnalysisApp()
    app.mainloop()
