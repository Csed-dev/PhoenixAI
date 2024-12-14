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
            return str(delta.seconds) + " Sekunden"
        return "Not completed"

    def get_status(self):
        """Gibt den aktuellen Status zurück."""
        return {
            "Step": self.name,
            "Outcome": self.outcome if self.outcome else "Running",
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

# Beispiel-Funktion zur Simulation
def example_task(duration=2, success=True):
    time.sleep(duration)  # Simuliert Arbeit
    if not success:
        raise Exception("Beispiel-Fehler")

# Pipeline ausführen
if __name__ == "__main__":
    pipeline = Pipeline()
    try:
        pipeline.add_step("1 Black", example_task, duration=2, success=True)
        pipeline.add_step("2 Green", example_task, duration=3, success=False)
        pipeline.add_step("3 Blue", example_task, duration=1, success=True)
    except Exception as e:
        print(f"Fehler in der Pipeline: {e}")
