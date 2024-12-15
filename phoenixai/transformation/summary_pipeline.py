import time
import datetime

class PipelineStep:
    def __init__(self, name):
        self.name = name
        self.start_time = None
        self.end_time = None
        self.outcome = None  # "success" oder "failure"
    
    def run(self, function, *args, **kwargs):
        """Führt den Schritt aus und protokolliert die Zeit und das Ergebnis."""
        self.start_time = datetime.datetime.now()
        try:
            function(*args, **kwargs)  # Die tatsächliche Funktion des Schrittes
            self.outcome = "success"
        except Exception as e:
            self.outcome = f"failure: {e}"
        finally:
            self.end_time = datetime.datetime.now()

    def get_time_taken(self):
        """Gibt die benötigte Zeit als String zurück."""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return f"{str(delta.seconds)} Sekunden"
        return "Not completed"

    def get_status(self):
        """Gibt den aktuellen Status zurück."""
        return {
            "Step": self.name,
            "Outcome": self.outcome or "Running",
            "Time Taken": self.get_time_taken(),
            "Timestamp": self.start_time.strftime("%H:%M:%S") if self.start_time else "N/A",
        }


class Pipeline:
    def __init__(self):
        self.steps = []
    
    def add_step(self, name, function, *args, **kwargs):
        """Fügt einen Schritt zur Pipeline hinzu."""
        self.steps.append(PipelineStep(name))
        self.steps[-1].run(function, *args, **kwargs)
        self.display_status()
    
    def display_status(self):
        """Aktualisiert die Ausgabe in der Konsole."""
        print("\nAktueller Pipeline-Status:")
        print("-" * 50)
        for step in self.steps:
            status = step.get_status()
            print(f"Schritt: {status['Step']}")
            print(f"Ergebnis: {status['Outcome']}")
            print(f"Zeit: {status['Time Taken']}")
            print(f"Startzeit: {status['Timestamp']}")
            print("-" * 50)
