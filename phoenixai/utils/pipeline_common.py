# pipeline_common.py
import time
from tkinter import messagebox
from typing import Callable, Optional, Any, List



class PipelineStep:
    def __init__(self, name: str, function: Callable, *args, **kwargs):
        self.name = name
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.status = "Pending"
        self.duration = None

    def run(self):
        start_time = time.time()
        try:
            self.status = "Running..."

            if self.function:
                self.function(*self.args, **self.kwargs)
            self.status = "🟢 Success"
        except Exception as e:
            self.status = f"🔴 Failed: {e}"
        finally:
            end_time = time.time()
            self.duration = end_time - start_time


class Pipeline:
    def __init__(self, treeview, step_callback: Optional[Callable[[PipelineStep], Any]] = None):
        """
        :param treeview: Das Treeview-Widget zur Anzeige der Pipeline-Schritte.
        :param step_callback: Eine optionale Callback-Funktion, die nach jedem Schritt aufgerufen wird.
                              Sie erhält das abgeschlossene PipelineStep-Objekt als Parameter.
        """
        self.steps: List[PipelineStep] = []
        self.current_step = 0
        self.treeview = treeview
        self.step_callback = step_callback

    def add_step(self, name: str, function: Callable, *args, **kwargs):
        step = PipelineStep(name, function, *args, **kwargs)
        self.steps.append(step)
        self.display_status()

    def display_status(self):
        # TreeView-Einträge leeren
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        # Aktuelle Steps eintragen
        for idx, step in enumerate(self.steps, start=1):
            duration_text = f"{step.duration:.2f}s" if step.duration else "N/A"
            file_path_display = self._truncate_path(step.args[0]) if step.args else "N/A"
            self.treeview.insert(
                "",
                "end",
                iid=str(idx),
                values=(step.status, step.name, file_path_display, duration_text)
            )

    def run_next_step(self):
        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            step.status = "Running..."
            self.display_status()
            self.treeview.update_idletasks()  # Erzwingt die GUI-Aktualisierung

            step.run()
            self.display_status()

            if self.step_callback:
                self.step_callback(step)

            self.current_step += 1
        else:
            messagebox.showinfo("Info", "Alle Schritte sind abgeschlossen.")

    def reset(self):
        self.steps.clear()
        self.current_step = 0
        self.display_status()

    def _truncate_path(self, path: str) -> str:
        import os
        parts = path.split(os.sep)
        if len(parts) > 4:
            # Sicherstellen, dass alle Teile als str vorliegen
            return os.path.join(*map(str, parts[-4:]))
        return path
