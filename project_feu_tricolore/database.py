import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name="simulation_trafic.db"):
        self.db_name = db_name
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                type_action TEXT,
                action TEXT,
                etat_feu TEXT,
                scenario TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def log_event(self, type_a, action, etat, scen):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO logs (timestamp, type_action, action, etat_feu, scenario) VALUES (?,?,?,?,?)",
                       (ts, type_a, action, etat, scen))
        conn.commit()
        conn.close()