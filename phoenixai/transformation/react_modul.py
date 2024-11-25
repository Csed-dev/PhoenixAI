class ReActAgent:
    """
    Allgemeines ReAct-Modul, das iterative Zyklen aus Denken, Handeln und Beobachten durchführt.
    """

    def __init__(self, max_iterations=5):
        """
        Initialisiert den Agenten.

        :param max_iterations: Maximale Anzahl von Iterationen (Zyklen).
        """
        self.max_iterations = max_iterations
        self.thought_history = []
        self.observation_history = []

    def think(self, current_context):
        """
        Implementiert den Denken-Schritt.

        :param current_context: Der aktuelle Kontext, bestehend aus bisherigen Gedanken und Beobachtungen.
        :return: Ein neuer Gedanke als String.
        """
        raise NotImplementedError(
            "Die Methode 'think' muss in einer Unterklasse implementiert werden."
        )

    def act(self, thought):
        """
        Implementiert den Handeln-Schritt basierend auf einem Gedanken.

        :param thought: Der Gedanke, auf dessen Basis die Aktion ausgeführt wird.
        :return: Eine Aktion und ggf. ihre Ergebnisse.
        """
        raise NotImplementedError(
            "Die Methode 'act' muss in einer Unterklasse implementiert werden."
        )

    def observe(self, action_result):
        """
        Implementiert den Beobachten-Schritt basierend auf den Ergebnissen der Aktion.

        :param action_result: Das Ergebnis der Aktion.
        :return: Eine Beobachtung als String.
        """
        raise NotImplementedError(
            "Die Methode 'observe' muss in einer Unterklasse implementiert werden."
        )

    def run(self, initial_context):
        """
        Führt den Denken-Handeln-Beobachten-Zyklus iterativ aus.

        :param initial_context: Der Startkontext, der die Aufgabe definiert.
        :return: Das Endergebnis nach Abschluss der Iterationen.
        """
        context = initial_context
        for iteration in range(1, self.max_iterations + 1):
            print(f"--- Iteration {iteration} ---")

            # Denken
            thought = self.think(context)
            self.thought_history.append(thought)
            print(f"[Denken] {thought}")

            # Handeln
            action_result = self.act(thought)
            print(f"[Handeln] Aktionsergebnis: {action_result}")

            # Beobachten
            observation = self.observe(action_result)
            self.observation_history.append(observation)
            print(f"[Beobachten] {observation}")

            # Kontext aktualisieren
            context = {
                "thoughts": self.thought_history,
                "observations": self.observation_history,
                "current_observation": observation,
            }

            # Abbruchbedingung
            if self.is_task_complete(context):
                print("[Info] Aufgabe abgeschlossen.")
                return context

        print("[Info] Maximale Iterationen erreicht.")
        return context

    def is_task_complete(self, context):
        """
        Überprüft, ob die Aufgabe abgeschlossen ist.

        :param context: Der aktuelle Kontext.
        :return: True, wenn die Aufgabe abgeschlossen ist, ansonsten False.
        """
        # Standardmäßig immer False; in Unterklassen spezifizieren.
        return False
