from database import DatabaseManager

class TrafficLogger:
    def __init__(self):
        self.db = DatabaseManager()

    def log(self, type_action, action, etat_feu="N/A", scenario="N/A"):
        # Affiche dans la console pour le debug
        print(f"LOG: [{type_action}] {action} | Feu: {etat_feu} | Scénario: {scenario}")
        # Enregistre dans SQLite
        self.db.log_event(type_action, action, etat_feu, scenario)