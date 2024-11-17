import sqlite3

# Verbindung zur generischen SQLite-Datenbank herstellen
db_path = "phoenixai/database/code_quality_tests.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Tabelle für den Pylint-Test erstellen
cursor.execute("""
CREATE TABLE IF NOT EXISTS pylint_test (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    error_code TEXT NOT NULL,
    message_emitted TEXT NOT NULL,
    description TEXT NOT NULL,
    problematic_code TEXT NOT NULL,
    correct_code TEXT NOT NULL
)
""")

# Änderungen speichern und Verbindung schließen
conn.commit()
conn.close()

print("Die Datenbank wurde erfolgreich erstellt. Die Tabelle für den Pylint-Test enthält Daten.")
