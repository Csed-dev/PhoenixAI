import logging
import json
import re
from typing import List, Optional, Dict

import typing_extensions
import google.generativeai as genai

from phoenixai.utils.base_prompt_handling import (
    read_file,
    load_llm_model,
)

# Neues Schema für strukturierte LLM-Ausgabe
class NameChange(typing_extensions.TypedDict):
    old_name: str
    new_name: str
    reason: str
    type: str  # 'function', 'variable', 'class', 'method'


def extract_line_numbers(code_content: str, names: List[str]) -> dict:
    lines = code_content.split("\n")
    name_lines = {name: [] for name in names}

    for line_num, line in enumerate(lines, start=1):
        for name in names:
            if re.search(rf"\b{name}\b", line):
                name_lines[name].append(line_num)

    return name_lines


def call_structured_llm(prompt: str, response_schema, temperature: float = 0.3) -> str:
    try:
        model = load_llm_model("gemini-1.5-flash")
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                response_mime_type="application/json",
                response_schema=response_schema,
            ),
        )

        if response and response.candidates:
            raw_text = response.candidates[0].content.parts[0].text
            return raw_text

        logging.error("Keine validen Ergebnisse vom LLM erhalten.")
        return "[]"

    except Exception as e:
        logging.error(f"Fehler beim Aufrufen des LLM für strukturierte Ausgabe: {e}")
        return "[]"


class NameChecker:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.report: List[str] = []

    # <<< HINZUGEFÜGT >>>
    def update_progress(self, phase: str, progress: float, message: str):
        """
        Platzhalterfunktion, damit es in einer Pipeline nicht zu Fehlern kommt.
        Kann nach Bedarf erweitert werden.
        """
        pass
    # <<< ENDE HINZUGEFÜGT >>>

    def analyze_names(self, code_content: str) -> Optional[List[NameChange]]:
        prompt = f"""
Analysiere den folgenden Python-Code und identifiziere nichtssagende Funktions-, Method- und Klassennamen.
Für jede identifizierte Variable, Funktion, Methode oder Klasse, gib das alte Name, das empfohlene neue Name und eine Begründung an.
Berücksichtige dabei die Funktionsparameter und Rückgabewerte, um aussagekräftigere Namen vorzuschlagen.
Formatiere die Antwort als JSON-Liste mit Objekten, die die folgenden Felder enthalten:
1. **old_name** → Der ursprüngliche Name
2. **new_name** → Ein präziserer, besserer Name
3. **reason** → Warum die Änderung vorgeschlagen wird
4. **type** → Entweder 'function', 'variable', 'class' oder 'method'

Hier ist der gesamte Code:

{code_content}
        """

        schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "old_name": {"type": "string"},
                    "new_name": {"type": "string"},
                    "reason": {"type": "string"},
                    "type": {"type": "string", "enum": ["function", "variable", "class", "method"]}
                },
                "required": ["old_name", "new_name", "reason", "type"]
            }
        }

        try:
            response = call_structured_llm(prompt, schema)
            suggestions = json.loads(response)

            if isinstance(suggestions, list):
                return suggestions

            logging.error("Das LLM antwortete nicht mit einer Liste.")
            return None

        except json.JSONDecodeError as e:
            logging.error(f"Fehler beim Parsen der LLM-Antwort: {e}")
            return None
        except Exception as e:
            logging.error(f"Allgemeiner Fehler bei der Analyse: {e}")
            return None

    def cluster_suggestions(self, suggestions: List[NameChange]) -> List[NameChange]:
        name_mapping = {}
        cleaned_suggestions = []

        for suggestion in suggestions:
            if "old_name" not in suggestion and "new_name" not in suggestion:
                logging.warning(f"Überspringe ungültige Suggestion: {suggestion}")
                continue

            if "old_name" not in suggestion:
                suggestion["old_name"] = "UNKNOWN"
            if "new_name" not in suggestion:
                suggestion["new_name"] = f"{suggestion['old_name']}_suggested"
            if "reason" not in suggestion:
                suggestion["reason"] = "Keine Begründung verfügbar"

            old_name = suggestion["old_name"]
            new_name = suggestion["new_name"]

            if new_name in name_mapping:
                name_mapping[new_name].append(old_name)
            else:
                name_mapping[new_name] = [old_name]

            cleaned_suggestions.append(suggestion)

        clustered_suggestions = []
        for new_name, old_names in name_mapping.items():
            for old_name in old_names:
                original = next(
                    (s for s in cleaned_suggestions if s["old_name"] == old_name and s["new_name"] == new_name),
                    None
                )
                if original:
                    clustered_suggestions.append(original)
        return clustered_suggestions

    def generate_report(self):
        self.update_progress("📝 Report generieren", 0, "Generiere Report...")
        code_content = read_file(self.file_path)
        suggestions = self.analyze_names(code_content)

        self.report.append("# Name Checker Report\n")
        self.report.append(f"**Datei:** `{self.file_path}`\n\n")

        if not suggestions:
            self.report.append("Keine Namensänderungsvorschläge gefunden oder Fehler bei der Analyse.\n")
            self.update_progress("📝 Report generieren", 100, "Report erfolgreich generiert.")
            return

        suggestions = self.cluster_suggestions(suggestions)

        names = [s['old_name'] for s in suggestions]
        name_line_numbers = extract_line_numbers(code_content, names)

        for s in suggestions:
            s['line_numbers'] = name_line_numbers.get(s['old_name'], [])

        func_suggestions = [s for s in suggestions if s["type"] == "function"]
        var_suggestions = [s for s in suggestions if s["type"] == "variable"]
        class_suggestions = [s for s in suggestions if s["type"] == "class"]
        method_suggestions = [s for s in suggestions if s["type"] == "method"]

        self.report.append("## Funktionen\n")
        if func_suggestions:
            for s in func_suggestions:
                lines = ", ".join(map(str, s.get("line_numbers", [])))
                self.report.append(
                    f"- **Altes Name:** `{s['old_name']}` (Zeile(n): {lines})\n"
                    f"  - **Neues Name:** `{s['new_name']}`\n"
                    f"  - **Begründung:** {s['reason']}\n"
                )
        else:
            self.report.append("Keine Funktionsnamen gefunden, die verbessert werden müssen.\n")

        self.report.append("\n## Methoden\n")
        if method_suggestions:
            for s in method_suggestions:
                lines = ", ".join(map(str, s.get("line_numbers", [])))
                self.report.append(
                    f"- **Altes Name:** `{s['old_name']}` (Zeile(n): {lines})\n"
                    f"  - **Neues Name:** `{s['new_name']}`\n"
                    f"  - **Begründung:** {s['reason']}\n"
                )
        else:
            self.report.append("Keine Methodennamen gefunden, die verbessert werden müssen.\n")

        self.report.append("\n## Klassen\n")
        if class_suggestions:
            for s in class_suggestions:
                lines = ", ".join(map(str, s.get("line_numbers", [])))
                self.report.append(
                    f"- **Altes Name:** `{s['old_name']}` (Zeile(n): {lines})\n"
                    f"  - **Neues Name:** `{s['new_name']}`\n"
                    f"  - **Begründung:** {s['reason']}\n"
                )
        else:
            self.report.append("Keine Klassennamen gefunden, die verbessert werden müssen.\n")

        self.report.append("\n## Variablen\n")
        if var_suggestions:
            for s in var_suggestions:
                lines = ", ".join(map(str, s.get("line_numbers", [])))
                self.report.append(
                    f"- **Altes Name:** `{s['old_name']}` (Zeile(n): {lines})\n"
                    f"  - **Neues Name:** `{s['new_name']}`\n"
                    f"  - **Begründung:** {s['reason']}\n"
                )
        else:
            self.report.append("Keine Variablennamen gefunden, die verbessert werden müssen.\n")

        self.update_progress("📝 Report generieren", 100, "Report erfolgreich generiert.")

    def save_report(self, output_path: str):
        with open(output_path, "w", encoding="utf-8") as f:
            f.writelines(self.report)
        print(f"Report gespeichert unter: {output_path}")


def main():
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(
        description="Name Checker: Analysiert Variablen- und Funktionsnamen ohne internes Code-Parsen."
    )
    parser.add_argument("file", help="Pfad zur Python-Datei, die analysiert werden soll.")
    parser.add_argument(
        "-o",
        "--output",
        help="Pfad zur Ausgabedatei für den Report.",
        default="name_checker_report.md",
    )

    args = parser.parse_args()

    if not Path(args.file).is_file():
        print(f"Datei nicht gefunden: {args.file}")
        return

    checker = NameChecker(args.file)
    checker.generate_report()
    checker.save_report(args.output)

if __name__ == "__main__":
    main()
