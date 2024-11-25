import random
from typing import Callable, List, Dict, Any


class MultiChainComparison:
    """
    Führt den gleichen Prompt mit verschiedenen Temperaturen aus und bewertet die Ergebnisse.
    """
    def __init__(self, prompt: str, temperatures: List[float], test_type: str):
        """
        :param prompt: Der Eingabeprompt, der mehrmals ausgeführt wird.
        :param temperatures: Eine Liste von Temperaturen für die LLM-Ausführung.
        :param test_type: Der Testtyp, um die Vergleichsfunktion auszuwählen.
        """
        self.prompt = prompt
        self.temperatures = temperatures
        self.test_type = test_type
        self.comparison_functions = {}

    def register_comparison_function(self, test_type: str, func: Callable):
        """
        Registriert eine Vergleichsfunktion für einen bestimmten Testtyp.
        :param test_type: Der Name des Testtyps.
        :param func: Die Vergleichsfunktion.
        """
        self.comparison_functions[test_type] = func

    def compare_results(self, results: List[Any], temperatures: List[float]) -> Any:
        """
        Vergleicht die Ergebnisse basierend auf der registrierten Vergleichsfunktion.

        :param results: Eine Liste von Ergebnissen.
        :param temperatures: Eine Liste von Temperaturen.
        :return: Das beste Ergebnis.
        """
        if self.test_type not in self.comparison_functions:
            raise ValueError(f"Keine Vergleichsfunktion für den Testtyp '{self.test_type}' registriert.")
        return self.comparison_functions[self.test_type](results, temperatures)


    def run(self, llm_function: Callable[[str, float], Any]) -> Any:
        """
        Führt den MultiChain-Prozess durch und wählt das beste Ergebnis.
        :param llm_function: Die Funktion, die den Prompt mit einer bestimmten Temperatur ausführt.
        :return: Das beste Ergebnis.
        """
        # Ergebnisse sammeln
        results = []
        for temp in self.temperatures:
            print(f"[MultiChain] Ausführen mit Temperatur {temp}")
            result = llm_function(self.prompt, temp)
            results.append((temp, result))

        # Vergleich der Ergebnisse
        print("[MultiChain] Ergebnisse werden verglichen...")
        result_texts = [r[1] for r in results]
        temps = [r[0] for r in results]
        best_index, best_result = self.compare_results(result_texts, temps)
        best_temp = results[best_index][0]
        print(f"[MultiChain] Bestes Ergebnis bei Temperatur {best_temp}")
        return best_result