import ttkbootstrap as tb
from tkinter import END, filedialog
from tkinter.scrolledtext import ScrolledText
import json
import csv
import webbrowser
import urllib.parse

class ResultManager:
    def __init__(self, parent_frame, results_tree, set_status_callback):
        self.parent_frame = parent_frame
        self.results_tree = results_tree
        self.set_status = set_status_callback
        self.results = []

        self.build_results_section()

    def build_results_section(self):
        """Erstellt den Ergebnisbereich der GUI."""
        ergebnisse_label = tb.Label(
            self.parent_frame,
            text="📊 Analyse-Ergebnisse",
            font=("Helvetica", 16, "bold"),
            bootstyle="secondary"
        )
        ergebnisse_label.pack(anchor="w", pady=(0,10), padx=10)

        # Treeview für Ergebnisse
        columns = ("Script", "Ergebnis", "Status")
        self.results_tree.config(columns=columns)
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=200, anchor="center")
        self.results_tree.pack(fill="both", expand=True, pady=5, padx=10)

        # Buttons für Details, Vergleich, Export
        ergebnisse_buttons = tb.Frame(self.parent_frame)
        ergebnisse_buttons.pack(fill="x", pady=10, padx=10)

        details_button = tb.Button(ergebnisse_buttons, text="Details anzeigen", command=self.show_details, bootstyle="info-outline")
        details_button.pack(side="left", fill="x", expand=True, padx=5)

        compare_button = tb.Button(ergebnisse_buttons, text="Vergleichsansicht", command=self.compare_results, bootstyle="warning-outline")
        compare_button.pack(side="left", fill="x", expand=True, padx=5)

        export_button = tb.Button(ergebnisse_buttons, text="Exportieren", command=self.export_results, bootstyle="success-outline")
        export_button.pack(side="left", fill="x", expand=True, padx=5)

    def update_results_tree(self, script: str, result: str, status: str):
        """
        Fügt einen Eintrag in der Ergebnis-TreeView hinzu
        und speichert ihn in self.results (als Liste von Dicts).
        """
        self.results_tree.insert("", END, values=(script, result, status))
        self.results.append({"Script": script, "Ergebnis": result, "Status": status})

    def show_details(self):
        selected_item = self.results_tree.selection()
        if not selected_item:
            self.set_status("Bitte wählen Sie ein Ergebnis aus.")
            return
        item = self.results_tree.item(selected_item)
        script, result, status = item["values"]

        # Falls im Ergebnis ein Report-Pfad enthalten ist, z.B. "Report: performance_report.md"
        if "Report:" in result:
            # Extrahiere den Pfad (alles nach "Report: ")
            report_path = result.split("Report: ")[1].strip()
            # URL-encode den Report-Pfad, damit er als Query-Parameter übergeben werden kann
            encoded_path = urllib.parse.quote(report_path)
            url = f"http://localhost:5000/view_report?report={encoded_path}"
            webbrowser.open(url)
        else:
            # Fallback: Falls kein Report gefunden wird, öffne ein Standard-Toplevel-Fenster
            detail_window = tb.Toplevel(self.parent_frame)
            detail_window.title(f"Details zu {script}")
            detail_window.geometry("500x400")
            detail_label = tb.Label(detail_window, text=f"Details zu {script}", font=("Helvetica", 14, "bold"), bootstyle="secondary")
            detail_label.pack(anchor="w", pady=10, padx=10)
            detail_text = ScrolledText(detail_window, state="normal", font=("Helvetica", 12))
            detail_text.pack(fill="both", expand=True, padx=10, pady=5)
            detail_text.insert(
                tb.END,
                f"Ergebnis: {result}\nStatus: {status}\n\nWeitere Details können hier angezeigt werden."
            )
            detail_text.config(state="disabled")

    def compare_results(self):
        # Placeholder
        self.set_status("Vergleichsansicht ist noch nicht implementiert.")

    def export_results(self):
        if not self.results:
            self.set_status("Keine Ergebnisse zum Exportieren.")
            return
        export_window = tb.Toplevel(self.parent_frame)
        export_window.title("Exportieren")
        export_window.geometry("350x250")
        export_label = tb.Label(export_window, text="Wählen Sie ein Exportformat:", font=("Helvetica", 14, "bold"), bootstyle="secondary")
        export_label.pack(pady=20)
        json_button = tb.Button(export_window, text="Als JSON exportieren", command=lambda: self.export_as("json"), bootstyle="primary-outline")
        json_button.pack(fill="x", padx=50, pady=10)
        csv_button = tb.Button(export_window, text="Als CSV exportieren", command=lambda: self.export_as("csv"), bootstyle="primary-outline")
        csv_button.pack(fill="x", padx=50, pady=10)
        md_button = tb.Button(export_window, text="Als Markdown exportieren", command=lambda: self.export_as("md"), bootstyle="primary-outline")
        md_button.pack(fill="x", padx=50, pady=10)

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
                with open(file_path, "w", newline='', encoding="utf-8") as f:
                    import csv
                    writer = csv.DictWriter(f, fieldnames=["Script", "Ergebnis", "Status"])
                    writer.writeheader()
                    writer.writerows(self.results)
            elif format == "md":
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("| Skript | Ergebnis | Status |\n")
                    f.write("|---|---|---|\n")
                    for res in self.results:
                        f.write(f"| {res['Script']} | {res['Ergebnis']} | {res['Status']} |\n")
            self.set_status(f"Ergebnisse erfolgreich als {format.upper()} exportiert.")
        except Exception as e:
            tb.messagebox.show_error("Fehler", f"Beim Exportieren ist ein Fehler aufgetreten:\n{e}")
            self.set_status("Fehler beim Exportieren der Ergebnisse.")
