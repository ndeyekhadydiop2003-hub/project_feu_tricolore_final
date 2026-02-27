carrefour_occupied = None
CARREFOUR_MIN = -70
CARREFOUR_MAX = 70

from traffic_light import TrafficLightSystem
from vehicles import Vehicle
from scenarios import SCENARIOS
from database import DatabaseManager
import random
from turtle_scene import draw_roads, draw_crosswalks, draw_road_markings, pen, screen
import tkinter as tk
from gui import ControlGUI
import turtle
import math

# ================== LOGGER & DATABASE ==================
db = DatabaseManager()


class TrafficLogger:
    def log(self, type_a, action, etat="N/A", scen="N/A"):
        print(f"[LOG] {type_a} | {action} | Feu: {etat} | Scen: {scen}")
        db.log_event(type_a, action, etat, scen)


logger = TrafficLogger()

# ================== ÉTAT GLOBAL ==================
# ✅ MODIFICATION : La simulation commence en mode ARRÊTÉ
running = False  # Changé de True à False
vehicles = []

# ================== INITIALISATION DESSIN ==================
draw_roads()
draw_crosswalks()
draw_road_markings()
pen.goto(0, 380)
pen.pencolor("#2F4F4F")
pen.write("Carrefour Moderne - Simulation Réelle", align="center", font=("Arial", 24, "bold"))

# ================== SYSTÈME DE FEUX ==================
system = TrafficLightSystem(logger)
current_scenario = SCENARIOS["normal"]


def appliquer_scenario(nom):
    global current_scenario
    current_scenario = SCENARIOS[nom]
    system.set_durations(current_scenario.vert, current_scenario.orange, current_scenario.rouge,
                         clignotant=current_scenario.clignotant)
    for v in vehicles: v.speed = current_scenario.vitesse
    logger.log("SCENARIO", f"Passage en mode {nom}", scen=nom)


# ================== GESTION DU TRAFIC ==================
def creer_voiture(direction):
    # Positions de départ réalistes (8 voies)
    params = {
        'east': (-650, -30),
        'west': (650, 30),
        'north': (30, -500),
        'south': (-30, 500)
    }
    x, y = params[direction]

    # Vérifier si l'espace est libre (Distance de sécurité au départ)
    for v in vehicles:
        if math.sqrt((x - v.x) ** 2 + (y - v.y) ** 2) < 130:
            return None

    v = Vehicle(x, y, direction, current_scenario.vitesse)

    # Probabilité de tourner (Réalisme : 40% des voitures tournent)
    if random.random() < 0.4:
        possible_turns = {
            'east': ['north', 'south'],
            'west': ['north', 'south'],
            'north': ['east', 'west'],
            'south': ['east', 'west']
        }
        v.set_target_direction(random.choice(possible_turns[direction]))
    return v


def generer_trafic():
    if running:
        # Génération équilibrée sur les 4 axes
        directions = ['east', 'west', 'north', 'south']
        for d in directions:
            # Densité ajustée pour éviter les bouchons infinis
            if random.random() < current_scenario.densite / 12:
                new_v = creer_voiture(d)
                if new_v: vehicles.append(new_v)
    try:
        screen.ontimer(generer_trafic, 600)
    except:
        pass


# ================== CALLBACKS GUI ==================
# ✅ MODIFICATION : on_play démarre vraiment la simulation
def on_play():
    global running
    running = True
    logger.log("SIMULATION", "Démarrage de la simulation")


def on_pause(paused):
    global running
    running = not paused


def on_stop():
    global running
    running = False
    logger.log("SIMULATION", "Arrêt de la simulation")


def on_reset():
    global vehicles, running
    running = False
    for v in vehicles: v.clear_turtle()
    vehicles.clear()
    appliquer_scenario("normal")
    # ✅ MODIFICATION : Redémarrer automatiquement après reset
    running = True  # Redémarrage automatique
    logger.log("SIMULATION", "Réinitialisation et redémarrage de la simulation")


def on_manual_light(couleur, axe):
    if current_scenario.name == "manuel": system.change_manual(axe, couleur)


# ================== ANIMATION & LOGIQUE ==================
def update_simulation():
    if not running:
        try:
            screen.ontimer(update_simulation, 40)
        except:
            pass
        return

    # Mise à jour de la logique de chaque véhicule
    for v in vehicles[:]:
        try:
            v.move(vehicles, system)
            # Suppression si hors écran
            if abs(v.x) > 700 or abs(v.y) > 700:
                v.clear_turtle()
                if v in vehicles: vehicles.remove(v)
        except:
            if v in vehicles: vehicles.remove(v)

    try:
        turtle.update()
        screen.ontimer(update_simulation, 40)
    except:
        pass


def cycle():
    if running and current_scenario.name != "manuel":
        delay = system.next_phase(current_scenario.name)
        try:
            screen.ontimer(cycle, delay)
        except:
            pass
    else:
        try:
            screen.ontimer(cycle, 500)
        except:
            pass


# ================== LANCEMENT ==================
appliquer_scenario("normal")

# ✅ MODIFICATION : Les boucles démarrent mais ne génèrent rien tant que running=False
generer_trafic()
update_simulation()
cycle()

# Message dans la console
print("=" * 60)
print("🚦 SIMULATION DE CARREFOUR - MODE MANUEL")
print("=" * 60)
print("⏸️  La simulation est en pause.")
print("▶️  Cliquez sur le bouton 'Démarrer' pour lancer la simulation.")
print("=" * 60)

root = tk.Tk()
gui = ControlGUI(root, on_play, on_pause, on_stop, on_reset, appliquer_scenario, on_manual_light)
root.mainloop()