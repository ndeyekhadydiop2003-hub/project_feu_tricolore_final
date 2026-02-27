import tkinter as tk

class ControlGUI:
    def __init__(self, root, on_play, on_pause, on_stop, on_reset, on_scenario_change, on_manual_light):
        self.root = root
        self.root.title("Contrôle Carrefour")
        # Fenêtre compacte pour s'afficher à côté du carrefour
        self.root.geometry("300x650")
        self.root.configure(bg="#1a1a1a") # Fond noir moderne

        # Callbacks
        self.on_play = on_play
        self.on_pause = on_pause
        self.on_stop = on_stop
        self.on_reset = on_reset
        self.on_scenario_change = on_scenario_change
        self.on_manual_light = on_manual_light
        self.paused = False

        # --- STYLE ---
        self.bg_black = "#1a1a1a"
        self.bg_card = "#2d2d2d"
        self.text_white = "#ffffff"
        self.font_bold = ("Arial", 10, "bold")

        # --- TITRE ---
        tk.Label(root, text="DASHBOARD TRAFIC", font=("Arial", 12, "bold"),
                 bg="#34495e", fg="white", pady=15).pack(fill=tk.X)

        # --- SECTION ÉTAT ---
        self.frame_status = tk.Frame(root, bg=self.bg_card, padx=10, pady=10)
        self.frame_status.pack(fill="x", padx=15, pady=10)

        self.lbl_scenario = tk.Label(self.frame_status, text="Scénario : NORMAL",
                                     fg="#3498db", bg=self.bg_card, font=self.font_bold)
        self.lbl_scenario.pack()

        self.lbl_running = tk.Label(self.frame_status, text="Simulation : EN COURS",
                                    fg="#2ecc71", bg=self.bg_card, font=("Arial", 9))
        self.lbl_running.pack()

        # --- SECTION SCÉNARIOS ---
        self._label("CHOIX DU SCÉNARIO")
        self.frame_scen = tk.Frame(root, bg=self.bg_black)
        self.frame_scen.pack(fill="x", padx=20)

        scenarios = [("Normal", "normal", "#7f8c8d"), ("Heure de Pointe", "pointe", "#d35400"),
                     ("Mode Nuit", "nuit", "#2980b9"), ("Mode Manuel", "manuel", "#c0392b")]

        for text, key, color in scenarios:
            tk.Button(self.frame_scen, text=text, bg=color, fg="white", relief="flat",
                      font=("Arial", 9), command=lambda k=key: self._change_scen(k)).pack(fill="x", pady=2)

        # --- SECTION SIMULATION (Simplifiée) ---
        self._label("CONTRÔLES SIMULATION")
        self.frame_sim = tk.Frame(root, bg=self.bg_black)
        self.frame_sim.pack(fill="x", padx=20)

        # Bouton Démarrer
        tk.Button(self.frame_sim, text="▶ DÉMARRER", bg="#27ae60", fg="white", relief="flat",
                  font=self.font_bold, command=self._play_click).pack(fill="x", pady=2)

        # Bouton Pause / Reprendre
        self.btn_pause = tk.Button(self.frame_sim, text="⏸ PAUSE", bg="#f1c40f", fg="black", relief="flat",
                                   font=self.font_bold, command=self.toggle_pause)
        self.btn_pause.pack(fill="x", pady=2)

        # Bouton Réinitialiser (Sans confirmation)
        tk.Button(self.frame_sim, text="🔄 RÉINITIALISER", bg="#ecf0f1", fg="#2c3e50", relief="flat",
                  font=self.font_bold, command=self._reset_direct).pack(fill="x", pady=10)

        # Bouton Quitter (ajouté en bas de réinitialiser)
        tk.Button(self.frame_sim, text="❌ QUITTER", bg="#e74c3c", fg="white", relief="flat",
                  font=self.font_bold, command=self.root.quit).pack(fill="x", pady=2)

        # --- SECTION MANUEL ---
        self._label("FEUX MANUELS")
        self.frame_man = tk.Frame(root, bg=self.bg_black)
        self.frame_man.pack(fill="x", padx=10)

        self._create_manual_btns(self.frame_man, "AXE HORIZONTAL (E-W)", "horizontal")
        self._create_manual_btns(self.frame_man, "AXE VERTICAL (N-S)", "vertical")

    def _label(self, text):
        tk.Label(self.root, text=text, bg=self.bg_black, fg="#7f8c8d", font=("Arial", 8, "bold"), pady=10).pack()

    def _create_manual_btns(self, parent, text, axe):
        tk.Label(parent, text=text, bg=self.bg_black, fg="white", font=("Arial", 7)).pack()
        f = tk.Frame(parent, bg=self.bg_black)
        f.pack(pady=3)
        for c_name, color in [("VERT", "#2ecc71"), ("ORANGE", "#f39c12"), ("ROUGE", "#e74c3c")]:
            tk.Button(f, text=c_name, bg=color, fg="white", font=("Arial", 7, "bold"), relief="flat",
                      width=8, command=lambda cn=c_name, ax=axe: self.on_manual_light(cn, ax)).pack(side=tk.LEFT, padx=2)

    def _change_scen(self, key):
        self.lbl_scenario.config(text=f"Scénario : {key.upper()}")
        self.on_scenario_change(key)

    def _play_click(self):
        self.lbl_running.config(text="Simulation : EN COURS", fg="#2ecc71")
        self.on_play()

    def toggle_pause(self):
        self.paused = not self.paused
        self.lbl_running.config(text="Simulation : EN PAUSE" if self.paused else "Simulation : EN COURS",
                                fg="#f39c12" if self.paused else "#2ecc71")
        self.btn_pause.config(text="▶ REPRENDRE" if self.paused else "⏸ PAUSE")
        self.on_pause(self.paused)

    def _reset_direct(self):
        # Réinitialisation immédiate sans fenêtre de confirmation
        self.lbl_scenario.config(text="Scénario : NORMAL")
        self.lbl_running.config(text="Simulation : EN COURS", fg="#2ecc71")
        self.on_reset()