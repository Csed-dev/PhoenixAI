import requests
from bs4 import BeautifulSoup
import sqlite3
import time

# Funktion zur Extraktion von Details einer spezifischen Fehlermeldung
def extract_error_details(error_url):
    response = requests.get(error_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extrahiere die Fehlermeldung (Message Emitted)
    message_emitted_tag = soup.find("p", string="Message emitted:")
    if message_emitted_tag:
        spans = message_emitted_tag.find_next("code").find_all("span", class_="pre")
        message_emitted = " ".join(span.get_text(strip=True) for span in spans)
    else:
        message_emitted = "Not found"

    # Extrahiere die Beschreibung
    description_tag = soup.find("p", string="Description:")
    if description_tag:
        description = description_tag.find_next("p").get_text(strip=True)
    else:
        description = "Not found"

    # Extrahiere problematischen und korrekten Code
    code_blocks = soup.find_all("pre")
    if len(code_blocks) >= 2:
        problematic_code = " ".join(
            span.get_text(strip=True) for span in code_blocks[0].find_all("span")
        )
        correct_code = " ".join(
            span.get_text(strip=True) for span in code_blocks[1].find_all("span")
        )
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

    # Tabelle für bereits verarbeitete Fehlercodes überprüfen oder erstellen
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_errors (
            error_code TEXT PRIMARY KEY
        )
    """)
    conn.commit()

    # Pylint-Übersicht-Seite
    overview_url = "https://pylint.readthedocs.io/en/stable/user_guide/messages/messages_overview.html"
    error_links = extract_links_from_overview(overview_url)

    # Liste bereits verarbeiteter Fehlercodes abrufen
    cursor.execute("SELECT error_code FROM processed_errors")
    processed_error_codes = {row[0] for row in cursor.fetchall()}

    # Für jeden Link Details extrahieren und in die Datenbank einfügen
    for error_code, error_url in error_links:
        if error_code in processed_error_codes:
            print(f"Skipping already processed error code: {error_code}")
            continue

        retries = 3
        while retries > 0:
            try:
                # Extrahiere Details und füge sie in die Haupttabelle ein
                message_emitted, description, problematic_code, correct_code = extract_error_details(error_url)
                cursor.execute("""
                    INSERT INTO pylint_test (error_code, message_emitted, description, problematic_code, correct_code)
                    VALUES (?, ?, ?, ?, ?)
                """, (error_code, message_emitted, description, problematic_code, correct_code))
                
                # Markiere den Fehlercode als verarbeitet
                cursor.execute("INSERT INTO processed_errors (error_code) VALUES (?)", (error_code,))
                conn.commit()
                print(f"Successfully processed: {error_code}")
                break
            except requests.exceptions.RequestException as e:
                retries -= 1
                print(f"Error fetching {error_code}: {e}. Retries left: {retries}")
                time.sleep(5)  # Warte 5 Sekunden vor erneutem Versuch
            except Exception as e:
                print(f"Unexpected error processing {error_code}: {e}")
                break

        if retries == 0:
            print(f"Failed to process {error_code} after multiple retries.")

    # Verbindung schließen
    conn.close()
    print("Datenbank erfolgreich gefüllt.")

# Funktion ausführen
populate_database()
