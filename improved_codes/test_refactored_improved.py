import math


def is_valid(item):
    """Überprüft, ob ein Datenpunkt gültig ist."""
    # Beispielvalidierungslogik
    return isinstance(item, (int, float)) and item >= 0

def clean_item(item):
    """Bereinigt einen einzelnen Datenpunkt."""
    # Beispielbereinigung: Rundet auf zwei Dezimalstellen
    return round(item, 2)

def transform_item(item):
    """Transformiert einen einzelnen Datenpunkt."""
    # Beispieltransformation: Quadratwurzel berechnen
    return math.sqrt(item)

def analyze_data(data):
    """Analysiert die transformierten Daten."""
    # Beispielanalyse: Durchschnitt berechnen
    if not data:
        return 0
    return sum(data) / len(data)

def save_results(analysis):
    """Speichert die Analyseergebnisse."""
    # Beispiel-Speicherlogik: Ausgabe in der Konsole
    print(f"Durchschnitt der transformierten Daten: {analysis}")

def handle_user_input(user_input):
    """
    Diese Funktion ist ebenfalls zu lang und erfüllt mehrere Aufgaben:
    1. Benutzereingabe parsen
    2. Benutzereingabe validieren
    3. Benutzereingabe verarbeiten
    4. Feedback geben
    """
    # Aufgabe 1: Eingabe parsen
    parsed_input = parse_input(user_input)
    
    # Aufgabe 2: Eingabe validieren
    if not validate_input(parsed_input):
        print("Ungültige Eingabe. Bitte geben Sie eine positive Zahl ein.")
        return
    
    # Aufgabe 3: Eingabe verarbeiten
    result = process_input(parsed_input)
    
    # Aufgabe 4: Feedback geben
    provide_feedback(result)

def parse_input(user_input):
    """Parst die Benutzereingabe."""
    try:
        return float(user_input)
    except ValueError:
        return None

def validate_input(parsed_input):
    """Validiert die geparste Eingabe."""
    return parsed_input is not None and parsed_input > 0

def process_input(parsed_input):
    """Verarbeitet die validierte Eingabe."""
    # Beispielprozess: Quadrat berechnen
    return parsed_input ** 2

def provide_feedback(result):
    """Gibt Feedback zum Verarbeitungsergebnis."""
    print(f"Das Quadrat der eingegebenen Zahl ist: {result}")

def main():
    """Hauptfunktion, die den gesamten Prozess steuert."""
    data = load_data()
    process_data(data)
    
    while True:
        user_input = get_user_input()
        if user_input.lower() in ('exit', 'quit'):
            print("Programm wird beendet.")
            break
        handle_user_input(user_input)

def load_data():
    """Lädt Daten aus einer Quelle."""
    # Beispiel: Rückgabe einer Liste von Zahlen
    return [25, 16, 9, -4, 0, 49]

def get_user_input():
    """Holt Eingabe vom Benutzer."""
    return input("Bitte geben Sie eine positive Zahl ein (oder 'exit' zum Beenden): ")

if __name__ == "__main__":
    main()

def is_valid(item):
    # Implementierung der Validierung
    pass

def clean_item(item):
    # Implementierung der Bereinigung
    pass

def transform_item(item):
    # Implementierung der Transformation
    pass

def analyze_data(data):
    # Implementierung der Datenanalyse
    pass

def save_results(analysis):
    # Implementierung des Speicherns der Ergebnisse
    pass

def clean_data(data):
    return [clean_item(item) for item in data if is_valid(item)]

def transform_data(data):
    return [transform_item(item) for item in data]

def process_data(data):
    cleaned_data = clean_data(data)
    transformed_data = transform_data(cleaned_data)
    analysis = analyze_data(transformed_data)
    save_results(analysis)