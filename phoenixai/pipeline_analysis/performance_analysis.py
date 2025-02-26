#!/usr/bin/env python3
"""
Analysiert die Performance einer Python-Datei oder eines Ordners und gibt Empfehlungen zur Verbesserung.
Verwendete Tools:
- cProfile (für CPU-Analyse)
- memory_profiler (für Speicheranalyse)
- Scalene (detaillierte CPU- und Speicheranalyse)
- VizTracer (Tracing für Funktionsaufrufe)
"""

import os
import subprocess
import cProfile
import pstats
import io
from memory_profiler import memory_usage

def analyze_cpu(file_path: str) -> str:
    pr = cProfile.Profile()
    try:
        pr.runctx("exec(open(file_path).read())", globals(), locals())
    except Exception as e:
        return f"Fehler beim Ausführen der Datei: {e}"
    stream = io.StringIO()
    stats = pstats.Stats(pr, stream=stream).sort_stats("cumulative")
    stats.print_stats(10)
    return stream.getvalue()

def analyze_memory(file_path: str) -> str:
    try:
        cmd = ["python", file_path]
        mem_usage = memory_usage(proc=(subprocess.Popen, (cmd,)), interval=0.1, timeout=60)
        if mem_usage:
            avg_memory = sum(mem_usage) / len(mem_usage)
            return f"Durchschnittliche Speichernutzung: {avg_memory:.2f} MiB"
        else:
            return "Keine Speicherdaten erfasst."
    except Exception as e:
        return f"Fehler bei der Speicheranalyse: {e}"

def run_scalene(file_path: str) -> str:
    try:
        result = subprocess.run(
            ["scalene", file_path],
            capture_output=True,
            text=True,
            timeout=120
        )
        return result.stdout if result.stdout else "Keine Scalene-Ausgabe erhalten."
    except Exception as e:
        return f"Fehler beim Ausführen von Scalene: {e}"

def run_viztracer(file_path: str) -> str:
    try:
        result = subprocess.run(
            ["viztracer", file_path, "--log_file", "viztracer.log", "--max_stack", "10"],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            try:
                with open("viztracer.log", "r", encoding="utf-8") as log_file:
                    log_content = log_file.read()
                return log_content
            except Exception as e:
                return f"VizTracer-Log wurde erstellt, konnte aber nicht gelesen werden: {e}"
        else:
            return f"Fehler bei VizTracer: {result.stderr}"
    except Exception as e:
        return f"Fehler beim Ausführen von VizTracer: {e}"


def generate_recommendations(cpu_output: str, memory_output: str, scalene_output: str, viztracer_output: str) -> str:
    recommendations = []
    if "Fehler" in cpu_output:
        recommendations.append("Überprüfen Sie den Code auf Ausführungsfehler während der CPU-Analyse.")
    else:
        recommendations.append("Analysieren Sie die cProfile-Ausgabe, um Engpässe im Code zu identifizieren.")
    if "Fehler" in memory_output:
        recommendations.append("Stellen Sie sicher, dass die Speicheranalyse korrekt durchgeführt wird.")
    else:
        recommendations.append("Falls die Speichernutzung hoch ist, erwägen Sie Optimierungen wie Caching oder eine Speicherbereinigung.")
    recommendations.append("Nutzen Sie Scalene für eine detaillierte Betrachtung von CPU- und Speicherengpässen.")
    recommendations.append("VizTracer kann helfen, den Ablauf der Funktionsaufrufe zu verstehen und Engpässe zu erkennen.")
    recommendations.append("Erwägen Sie Parallelisierung oder asynchrone Programmierung, falls die CPU-Auslastung hoch ist.")
    return "\n".join(f"- {rec}" for rec in recommendations)

def analyze_file(file_path: str) -> dict:
    analysis = {}
    analysis["cpu_profile"] = analyze_cpu(file_path)
    analysis["memory_profile"] = analyze_memory(file_path)
    analysis["scalene"] = run_scalene(file_path)
    analysis["viztracer"] = run_viztracer(file_path)
    analysis["recommendations"] = generate_recommendations(
        analysis["cpu_profile"],
        analysis["memory_profile"],
        analysis["scalene"],
        analysis["viztracer"]
    )
    return analysis

def analyze_target(target_path: str) -> dict:
    results = {}
    if os.path.isfile(target_path) and target_path.endswith(".py"):
        print(f"Analysiere Datei: {target_path}")
        results[target_path] = analyze_file(target_path)
    elif os.path.isdir(target_path):
        for root, _, files in os.walk(target_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    print(f"Analysiere Datei: {file_path}")
                    results[file_path] = analyze_file(file_path)
    else:
        print("Bitte geben Sie eine gültige Python-Datei oder ein Verzeichnis an.")
    return results


def generate_report(results: dict, output_file: str = None) -> None:
    """
    Erzeugt für jede analysierte Python-Datei einen Performance-Report in einer
    hierarchischen Verzeichnisstruktur. Die Struktur soll folgendermaßen aussehen:

      reports/
          Performance/
              <Dateiname ohne Extension>/
                  performance_report_v<version>_<timestamp>.md

    Für jede Analyse wird eine neue Version mit Zeitstempel erzeugt. Wird output_file nicht
    angegeben, wird der Reportpfad automatisch anhand der analysierten Datei ermittelt.
    """
    import datetime
    # Falls output_file nicht vorgegeben ist, muss für jede Datei separat gespeichert werden.
    if output_file is None:
        # Diese Funktion wird in generate_report in performance_analysis.py nicht direkt
        # verwendet – stattdessen erfolgt die Pfaderzeugung in run_performance_analysis.
        raise ValueError("output_file muss angegeben werden.")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Performance Analysis Report\n\n")
        for file_path, analysis in results.items():
            f.write(f"## Datei: {file_path}\n\n")
            f.write("### CPU Profiling (cProfile)\n")
            f.write("```\n")
            f.write(analysis["cpu_profile"])
            f.write("\n```\n\n")
            f.write("### Memory Profiling\n")
            f.write("```\n")
            f.write(analysis["memory_profile"])
            f.write("\n```\n\n")
            f.write("### Scalene Output\n")
            f.write("```\n")
            f.write(analysis["scalene"])
            f.write("\n```\n\n")
            f.write("### VizTracer Output\n")
            f.write("```\n")
            f.write(analysis["viztracer"])
            f.write("\n```\n\n")
            f.write("### Empfehlungen zur Performance-Optimierung\n")
            f.write(analysis["recommendations"])
            f.write("\n\n---\n\n")
    print(f"Report wurde erstellt: {output_file}")
