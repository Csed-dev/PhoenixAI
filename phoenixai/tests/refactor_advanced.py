import datetime
import json
import os
import random
import statistics

"""
Test File: complex_test.py

Dieses Modul enthält mehrere Funktionen, die mehrere Aufgaben gleichzeitig erfüllen.
Jede Funktion kombiniert verschiedene Verantwortlichkeiten, z. B. Daten verarbeiten,
Dateien lesen/schreiben und Protokolle erstellen. Die Datei ist ausführbar, sodass du sie
direkt starten kannst, um die Ergebnisse zu sehen.
"""


def manage_user_data(file_path, user_data, log_file="user_log.txt"):
    """
    Verarbeitet und speichert Benutzerdaten.
    Aufgaben:
      - Prüfen, ob die Datei existiert, andernfalls wird eine neue JSON-Datei erstellt.
      - Aktuelle Benutzerdaten aus der Datei laden.
      - Neue Benutzerdaten hinzufügen.
      - Die aktualisierte Datenliste in die Datei schreiben.
      - Einen Log-Eintrag mit Zeitstempel erstellen.
    """
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([], f)
        print("Created a new user data file.")
    try:
        with open(file_path, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data.append(user_data)
            f.seek(0)
            json.dump(data, f, indent=4)
        print(f"Total users: {len(data)}")
        with open(log_file, "a", encoding="utf-8") as log:
            log.write(f"{datetime.datetime.now()}: Added user {user_data}\n")
    except Exception as e:
        print(f"Error managing user data: {e}")


def process_orders(orders, report_file="orders_report.txt"):
    """
    Verarbeitet Bestellungen und erstellt einen Bericht.
    Aufgaben:
      - Gesamtumsatz berechnen.
      - Die teuerste Bestellung ermitteln.
      - Anzahl der Bestellungen über 100 USD zählen.
      - Einen zusammenfassenden Bericht in eine Datei schreiben.
    """
    if not orders:
        print("No orders to process.")
        return
    total_revenue = sum(order.get("amount", 0) for order in orders)
    most_expensive = max(orders, key=lambda x: x.get("amount", 0))
    high_value_count = len([order for order in orders if order.get("amount", 0) > 100])
    summary = (
        f"Total Revenue: ${total_revenue}\n"
        f"Most Expensive Order: {most_expensive}\n"
        f"Orders > $100: {high_value_count}\n"
    )
    print(summary)
    try:
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(summary)
    except Exception as e:
        print(f"Error writing orders report: {e}")


def generate_random_data(file_path, num_users=10):
    """
    Generiert zufällige Benutzerdaten und protokolliert die Aktion.
    Aufgaben:
      - Erstellen einer Liste von Benutzerprofilen mit zufälligen Namen und Alter.
      - Speichern der Profile als JSON in eine Datei.
      - Berechnen des Durchschnittsalters.
      - Einen Log-Eintrag mit Zeitstempel anfügen.
    """
    user_profiles = [
        {"name": f"User{random.randint(1, 1000)}", "age": random.randint(18, 60)}
        for _ in range(num_users)
    ]
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(user_profiles, f, indent=4)
        avg_age = statistics.mean(profile["age"] for profile in user_profiles)
        print(f"Generated {len(user_profiles)} user profiles. Average Age: {avg_age:.1f}")
        with open("data_generation.log", "a", encoding="utf-8") as log:
            log.write(f"{datetime.datetime.now()}: Generated {num_users} profiles in {file_path}\n")
    except Exception as e:
        print(f"Error generating random data: {e}")


def analyze_weather_data(data):
    """
    Analysiert Wetterdaten und gibt Ergebnisse aus.
    Aufgaben:
      - Durchschnittstemperatur berechnen.
      - Den Tag mit der höchsten Temperatur ermitteln.
      - Anzahl der Tage mit Regen zählen.
    """
    if not data:
        print("No weather data provided.")
        return
    try:
        average_temp = sum(day.get("temperature", 0) for day in data) / len(data)
        hottest_day = max(data, key=lambda d: d.get("temperature", 0))
        rainy_days = sum(1 for day in data if day.get("rain", False))
        print(f"Average Temperature: {average_temp:.1f}°C")
        print(f"Hottest Day: {hottest_day}")
        print(f"Number of Rainy Days: {rainy_days}")
    except Exception as e:
        print(f"Error analyzing weather data: {e}")


if __name__ == "__main__":
    print("Running complex test file...")

    # Test manage_user_data
    test_user_file = "test_users.json"
    manage_user_data(test_user_file, {"name": "Alice", "age": 30})

    # Test process_orders
    orders = [
        {"id": 1, "amount": 150.75},
        {"id": 2, "amount": 50.25},
        {"id": 3, "amount": 200.00},
        {"id": 4, "amount": 90.50},
    ]
    process_orders(orders)

    # Test generate_random_data
    generate_random_data("test_random_users.json", num_users=15)

    # Test analyze_weather_data
    weather_data = [
        {"day": "Monday", "temperature": 22, "rain": False},
        {"day": "Tuesday", "temperature": 28, "rain": True},
        {"day": "Wednesday", "temperature": 25, "rain": False},
        {"day": "Thursday", "temperature": 30, "rain": True},
        {"day": "Friday", "temperature": 20, "rain": False},
    ]
    analyze_weather_data(weather_data)
