# scenarios.py

class Scenario:
    def __init__(self, name, vert, orange, rouge, vitesse, densite, clignotant=False):
        self.name = name
        self.vert = vert
        self.orange = orange
        self.rouge = rouge
        self.vitesse = vitesse
        self.densite = densite
        self.clignotant = clignotant


# scenarios.py (version corrigée)

SCENARIOS = {
    "normal": Scenario(
        name="normal",
        vert=5000,  # Augmenté à 20 secondes
        orange=5000,  # Réduit à 2 secondes (plus réaliste)
        rouge=500,  # 15 secondes (la durée du vert sur l'autre axe)
        vitesse=3.5,
        densite=1
    ),

    "pointe": Scenario(
        name="heure_de_pointe",
        vert=15000,  # Augmenté à 20 secondes pour gérer plus de trafic
        orange=1500,  # Réduit à 2 secondes
        rouge=1000,  # Réduit pour favoriser l'axe principal
        vitesse=2.5,
        densite=4
    ),

    # ... les autres scénarios restent inchangés pour l'instant
    "nuit": Scenario(
        name="nuit",
        vert=0,
        orange=0,
        rouge=0,
        vitesse=2.5,
        densite=1,
        clignotant=True
    ),

    "manuel": Scenario(
        name="manuel",
        vert=0,
        orange=0,
        rouge=0,
        vitesse=3,
        densite=3
    )
}
