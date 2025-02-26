import ttkbootstrap as tb
from tkinter import messagebox

class ActionManager:
    def __init__(self, parent_frame, analysis_vars, transform_vars, pipeline, set_status_callback):
        self.parent_frame = parent_frame
        self.analysis_vars = analysis_vars
        self.transform_vars = transform_vars
        self.pipeline = pipeline
        self.set_status = set_status_callback

        self.build_actions_section()

    def build_actions_section(self):
        """Erstellt den Aktionen auswählen Abschnitt der GUI."""
        actions_frame = tb.LabelFrame(self.parent_frame, text="Aktionen auswählen", bootstyle="info")
        actions_frame.pack(fill="x", pady=10, padx=10)

        # Analyse
        analysis_frame = tb.LabelFrame(actions_frame, text="Analyse", bootstyle="secondary")
        analysis_frame.pack(side="top", fill="x", padx=5, pady=5)

        for a_name, a_info in self.analysis_vars.items():
            var = a_info["var"]
            cb = tb.Checkbutton(analysis_frame, text=a_name, variable=var, bootstyle="secondary")
            cb.pack(side="left", padx=5, pady=2)

        # Transformation
        transformation_frame = tb.LabelFrame(actions_frame, text="Transformation", bootstyle="secondary")
        transformation_frame.pack(side="top", fill="x", padx=5, pady=5)

        for t_name, t_info in self.transform_vars.items():
            var = t_info["var"]
            cb = tb.Checkbutton(transformation_frame, text=t_name, variable=var, bootstyle="secondary")
            cb.pack(side="left", padx=5, pady=2)

    def confirm_actions(self, selected_file):
        """Bestätigt die ausgewählten Aktionen und fügt sie der Pipeline hinzu."""
        chosen_analysis = [name for name, info in self.analysis_vars.items() if info["var"].get()]
        chosen_transform = [name for name, info in self.transform_vars.items() if info["var"].get()]

        # Prüfe, ob mindestens eine Aktion ausgewählt wurde
        if (not chosen_analysis) and (not chosen_transform):
            tb.messagebox.show_warning("Warnung", "Bitte wähle mindestens eine Aktion (Analyse oder Transform).")
            return

        # Prüfe, ob überhaupt eine Datei ausgewählt wurde
        if not selected_file:
            tb.messagebox.show_warning("Warnung", "Bitte wähle eine Datei aus.")
            return

        for a in chosen_analysis:
            func = self.analysis_vars[a]["function"]
            if func:
                self.pipeline.add_step(a, func, selected_file)

        for t in chosen_transform:
            func = self.transform_vars[t]["function"]
            if func:
                self.pipeline.add_step(t, func, selected_file)

