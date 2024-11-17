import requests
from bs4 import BeautifulSoup
import sqlite3

# Funktion zur Extraktion von Details einer spezifischen Fehlermeldung
def extract_error_details(error_url):
    response = requests.get(error_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extrahiere die Fehlermeldung
    message_emitted_tag = soup.find("p", string="Message emitted:")
    if message_emitted_tag and message_emitted_tag.find_next("p"):
        message_emitted = message_emitted_tag.find_next("p").get_text(strip=True)
    else:
        message_emitted = "Not found"

    # Extrahiere die Beschreibung
    description_tag = soup.find("p", string="Description:")
    if description_tag and description_tag.find_next("p"):
        description = description_tag.find_next("p").get_text(strip=True)
    else:
        description = "Not found"

    # Extrahiere problematischen und korrekten Code
    code_blocks = soup.find_all("pre")
    if len(code_blocks) >= 2:
        problematic_code = code_blocks[0].get_text(strip=True)
        correct_code = code_blocks[1].get_text(strip=True)
    else:
        problematic_code = "Not found"
        correct_code = "Not found"

    return message_emitted, description, problematic_code, correct_code

# Funktion, um Links zu spezifischen Fehlermeldungen von der Übersicht zu extrahieren
def extract_links_from_overview(overview_url):
    response = requests.get(overview_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Suche nach Links zu den Fehlermeldungsseiten
    error_links = []
    sections = soup.find_all("section")
    for section in sections:
        links = section.find_all("a", class_="reference internal")[6:]  # Ignoriere die ersten 6 irrelevanten Links
        for link in links:
            href = link.get("href")
            error_code = link.get_text().split(" / ")[-1]
            error_links.append((error_code, f"https://pylint.readthedocs.io/en/stable/user_guide/messages/{href}"))
    return error_links

# Funktion, um Daten in die Datenbank einzufügen
def populate_database():
    # Verbindung zur SQLite-Datenbank herstellen
    db_path = "phoenixai/database/code_quality_tests.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Pylint-Übersicht-Seite
    overview_url = "https://pylint.readthedocs.io/en/stable/user_guide/messages/messages_overview.html"
    error_links = extract_links_from_overview(overview_url)

    # Für jeden Link Details extrahieren und in die Datenbank einfügen
    for error_code, error_url in error_links:
        if error_code == "I0021":
            print(f"Stopping extraction at error code: {error_code}")
            break  # Stoppe die Schleife, wenn der spezifische Fehlercode erreicht ist

        try:
            message_emitted, description, problematic_code, correct_code = extract_error_details(error_url)
            cursor.execute("""
                INSERT INTO pylint_test (error_code, message_emitted, description, problematic_code, correct_code)
                VALUES (?, ?, ?, ?, ?)
            """, (error_code, message_emitted, description, problematic_code, correct_code))
            print(f"Inserted: {error_code}")
        except Exception as e:
            print(f"Error processing {error_code}: {e}")

    # Änderungen speichern und Verbindung schließen
    conn.commit()
    conn.close()
    print("Datenbank erfolgreich gefüllt.")

# Funktion ausführen
populate_database()
