import turtle


def _lamp(x, y):
    # On crée une tortue spécifique pour chaque ampoule
    l = turtle.Turtle(shape='circle')
    l.shapesize(0.8)
    l.speed(0)
    l.penup()
    l.goto(x, y)
    l.color('grey')
    return l


class TrafficLight:
    def __init__(self, position, orientation='vertical'):
        self.vert = None
        self.rouge = None
        self.orange = None
        self.etat = 'ROUGE'
        self.position = position
        self.orientation = orientation
        # On garde une trace du "boîtier" pour pouvoir le manipuler si besoin
        self.body_pen = turtle.Turtle()
        self.body_pen.hideturtle()

        self.draw()
        self.clignotant_state = False

    def draw(self):
        # On nettoie l'ancien boîtier avant de dessiner
        self.body_pen.clear()
        self.body_pen.speed(0)
        self.body_pen.penup()
        self.body_pen.goto(self.position)
        self.body_pen.pendown()
        self.body_pen.fillcolor('black')
        self.body_pen.begin_fill()

        if self.orientation == 'vertical':
            w, h = 30, 80
        else:
            w, h = 80, 30

        for _ in range(2):
            self.body_pen.forward(w)
            self.body_pen.left(90)
            self.body_pen.forward(h)
            self.body_pen.left(90)
        self.body_pen.end_fill()

        bx, by = self.position
        # On ne recrée les lampes que si elles n'existent pas
        if not self.rouge:
            if self.orientation == 'vertical':
                self.rouge = _lamp(bx + 15, by + 65)
                self.orange = _lamp(bx + 15, by + 40)
                self.vert = _lamp(bx + 15, by + 15)
            else:
                self.rouge = _lamp(bx + 15, by + 15)
                self.orange = _lamp(bx + 40, by + 15)
                self.vert = _lamp(bx + 65, by + 15)

        self.set_etat(self.etat)

    def set_etat(self, etat):
        self.etat = etat
        # Sécurité : si on est en mode "OFF", tout est gris
        self.vert.color('grey')
        self.orange.color('grey')
        self.rouge.color('grey')

        if etat == 'VERT':
            self.vert.color('green')
        elif etat == 'ORANGE':
            self.orange.color('orange')
        elif etat == 'ROUGE':
            self.rouge.color('red')
        # Pas de turtle.update() ici pour éviter les lags, on le laisse au main

    def toggle_clignotant(self):
        self.vert.color('grey')
        self.rouge.color('grey')
        self.clignotant_state = not self.clignotant_state
        self.orange.color('orange' if self.clignotant_state else 'grey')


class TrafficLightSystem:
    def __init__(self, loggers):
        self.loggers = loggers  # Prêt pour la base de données
        self.west = TrafficLight((-150, -110), 'horizontal')
        self.east = TrafficLight((70, 80), 'horizontal')
        self.north = TrafficLight((80, -150), 'vertical')
        self.south = TrafficLight((-110, 70), 'vertical')

        self.phase = 'HORIZ_VERT'
        self.durations = {'vert': 5000, 'orange': 2000, 'rouge': 1500}
        self.clignotant = False

        # --- ATTRIBUTS POUR LA LOGIQUE DE PRIORITÉ ---
        self.phase_start_time = None  # Timestamp du début de la phase actuelle
        self.phase_duration = 0  # Durée prévue de la phase actuelle
        self.liste_vehicules = []  # Référence à la liste des véhicules (sera définie depuis main.py)

        self.set_phase()

    def change_manual(self, axe, couleur):
        """Méthode pour le contrôle manuel via le GUI"""
        if axe == "horizontal":
            self.west.set_etat(couleur)
            self.east.set_etat(couleur)
        else:
            self.north.set_etat(couleur)
            self.south.set_etat(couleur)
        turtle.update()

    def set_durations(self, v, o, r, clignotant=False):
        self.durations = {'vert': v, 'orange': o, 'rouge': r}
        self.clignotant = clignotant
        if clignotant:
            # ✅ NOUVEAU : Déclencher le clignotement immédiatement
            for light in [self.west, self.east, self.north, self.south]:
                light.set_etat('OFF')
                light.clignotant_state = False  # Réinitialiser l'état
            # Forcer le premier clignotement immédiatement
            self.west.toggle_clignotant()
            self.east.toggle_clignotant()
            self.north.toggle_clignotant()
            self.south.toggle_clignotant()
            turtle.update()

    def set_phase(self):
        if self.clignotant:
            return

        states = {
            'HORIZ_VERT': [('VERT', 'VERT'), ('ROUGE', 'ROUGE')],
            'HORIZ_ORANGE': [('ORANGE', 'ORANGE'), ('ROUGE', 'ROUGE')],
            'ALL_ROUGE_1': [('ROUGE', 'ROUGE'), ('ROUGE', 'ROUGE')],
            'VERT_VERT': [('ROUGE', 'ROUGE'), ('VERT', 'VERT')],
            'VERT_ORANGE': [('ROUGE', 'ROUGE'), ('ORANGE', 'ORANGE')],
            'ALL_ROUGE_2': [('ROUGE', 'ROUGE'), ('ROUGE', 'ROUGE')]
        }
        h, v = states[self.phase]
        self.west.set_etat(h[0]);
        self.east.set_etat(h[1])
        self.north.set_etat(v[0]);
        self.south.set_etat(v[1])
        turtle.update()

    # --- Vérifier si l'intersection est dégagée ---
    def intersection_est_degagee(self):
        """
        Vérifie si des voitures se trouvent dans la zone de l'intersection.
        Retourne True si l'intersection est vide, False sinon.
        """
        ZONE_INTERSECTION = {"x_min": -65, "x_max": 65, "y_min": -65, "y_max": 65}

        for voiture in self.liste_vehicules:
            vx, vy = voiture.xcor(), voiture.ycor()
            if (ZONE_INTERSECTION["x_min"] < vx < ZONE_INTERSECTION["x_max"] and
                    ZONE_INTERSECTION["y_min"] < vy < ZONE_INTERSECTION["y_max"]):
                return False  # Une voiture est dans l'intersection

        return True  # L'intersection est libre

    # --- MÉTHODE CORRIGÉE : next_phase avec logique de priorité améliorée ---
    def next_phase(self, scenario_name):
        if self.clignotant:
            # Fait clignoter l'orange sur tous les feux
            self.west.toggle_clignotant()
            self.east.toggle_clignotant()
            self.north.toggle_clignotant()
            self.south.toggle_clignotant()
            turtle.update()
            return 300  # Clignotement plus rapide (300ms au lieu de 500ms)

        # 1. Définir l'ordre des phases
        order = ['HORIZ_VERT', 'HORIZ_ORANGE', 'ALL_ROUGE_1', 'VERT_VERT', 'VERT_ORANGE', 'ALL_ROUGE_2']

        # 2. Associer chaque phase à sa durée configurée dans self.durations
        durs = {
            'HORIZ_VERT': self.durations['vert'],
            'HORIZ_ORANGE': self.durations['orange'],
            'ALL_ROUGE_1': self.durations['rouge'],
            'VERT_VERT': self.durations['vert'],
            'VERT_ORANGE': self.durations['orange'],
            'ALL_ROUGE_2': self.durations['rouge']
        }

        # --- LOGIQUE DE PRIORITÉ AMÉLIORÉE (MODE NORMAL UNIQUEMENT) ---

        # NOUVEAU : Bloquer le passage au vert si l'intersection n'est pas dégagée
        if self.phase in ['ALL_ROUGE_1', 'ALL_ROUGE_2']:
            if not self.intersection_est_degagee():
                # On reste en phase rouge et on revérifie dans 500ms
                return 500

        # Prolonger le feu vert si l'intersection n'est pas dégagée
        if self.phase in ['HORIZ_VERT', 'VERT_VERT']:
            if not self.intersection_est_degagee():
                # On prolonge de 500ms et on revérifie au prochain cycle
                return 500

        # 3. Passer à la phase suivante (l'intersection est dégagée ou ce n'est pas une phase critique)
        idx = order.index(self.phase)
        next_idx = (idx + 1) % len(order)
        self.phase = order[next_idx]

        # 4. Appliquer visuellement
        self.set_phase()

        # 5. RETOURNER LA DURÉE PRÉCISE
        return durs[self.phase]

    def get_axe_etat(self, direction):
        """Retourne l'état du feu correspondant à la direction du véhicule."""
        if direction in ('east', 'west'):
            return self.west.etat
        else:
            return self.north.etat

    def is_night_mode(self):
        """Retourne True si le système est en mode nuit (clignotant)."""
        return self.clignotant