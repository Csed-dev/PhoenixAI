"""
Dieses Modul konvertiert eine JSON-Datei in einen PDF-Bericht, der die Analyse eines Repositories darstellt.
"""

import json
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit


def json_to_pdf(json_file, output_pdf):
    """
    Konvertiert die Analyse eines Repositorys in ein PDF-Format.
    
    Args:
        json_file (str): Pfad zur JSON-Datei mit der Repository-Analyse.
        output_pdf (str): Pfad, unter dem das erstellte PDF gespeichert wird.
    """
    # Lade das JSON-Dokument
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # PDF-Erstellung initialisieren
    c = canvas.Canvas(output_pdf, pagesize=A4)
    width, height = A4
    y_position = height - 40  # Startposition auf der Seite

    # Titel
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y_position, "Repository Analysis Report")
    y_position -= 30  # Zeilenabstand

    # Überblick des Projekts
    c.setFont("Helvetica", 12)
    c.drawString(40, y_position, "Overview:")
    y_position -= 20
    overview_text = data.get("overview", "No overview available.")
    lines = simpleSplit(overview_text, "Helvetica", 10, width - 160)
    for line in lines:
        c.drawString(60, y_position, line)
        y_position -= 15

    # Dateien durchgehen
    c.setFont("Helvetica-Bold", 14)
    y_position -= 15  # Zusätzlicher Abstand
    c.drawString(40, y_position, "File Analysis:")
    y_position -= 25

    # Detaillierte Dateianalyse
    c.setFont("Helvetica", 10)
    for file_data in data.get("files", []):
        if y_position < 50:  # Seitenumbruch, wenn Platz knapp wird
            c.showPage()
            y_position = height - 40
        c.drawString(40, y_position, f"File: {file_data['filename']}")
        y_position -= 15
        
        # Zweck der Datei mit Zeilenumbruch
        purpose_lines = simpleSplit(
            f"Purpose: {file_data['purpose']}", "Helvetica", 10, width - 80
        )
        for line in purpose_lines:
            c.drawString(60, y_position, line)
            y_position -= 15
        
        # Abhängigkeiten mit Zeilenumbruch
        dependencies = ', '.join(file_data['dependencies'])
        dep_lines = simpleSplit(
            f"Dependencies: {dependencies}", "Helvetica", 10, width - 80
        )
        for line in dep_lines:
            c.drawString(60, y_position, line)
            y_position -= 15
        
        # Klassen durchgehen
        for cls in file_data.get("classes", []):
            class_lines = simpleSplit(
                f"Class: {cls['name']} - {cls['description']}", "Helvetica", 10, width - 100
            )
            for line in class_lines:
                c.drawString(80, y_position, line)
                y_position -= 15
            # Methoden der Klasse
            for method in cls.get("methods", []):
                method_lines = simpleSplit(
                    f"Method: {method['name']} - {method['description']}", "Helvetica", 10, width - 120
                )
                for line in method_lines:
                    c.drawString(100, y_position, line)
                    y_position -= 15

        # Funktionen durchgehen
        for func in file_data.get("functions", []):
            func_lines = simpleSplit(
                f"Function: {func['name']} - {func['description']}", "Helvetica", 10, width - 80
            )
            for line in func_lines:
                c.drawString(60, y_position, line)
                y_position -= 15

        y_position -= 20  # Abstand zwischen Dateien

    c.save()  # Speichert und schließt das PDF
    print(f"PDF gespeichert als '{output_pdf}'")


# Beispielaufruf
json_to_pdf("repo_analysis.json", "repo_analysis_report.pdf")
