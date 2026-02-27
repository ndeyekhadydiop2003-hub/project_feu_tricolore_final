import turtle
import random
import math


class Vehicle:
    def __init__(self, x, y, direction='east', speed=2, color=None):
        self.x = x
        self.y = y
        self.direction = direction
        self.base_speed = speed
        self.speed = speed
        self.state = 'moving'
        self.target_direction = None
        self.has_turned = False
        self.length = 45
        self.width = 25

        # Temps de réaction humain (aléatoire entre 0 et 0.5s)
        self.reaction_time = random.uniform(0, 0.5)
        self.waiting_since = 0

        possible_colors = ['#1E90FF', '#FF0000', '#FFA500', '#800080', '#008000', '#FFFF00', '#00FFFF', '#FF69B4',
                           '#FFFFFF', '#FFC0CB']
        self.color = color if color else random.choice(possible_colors)

        self.t = turtle.Turtle()
        self.t.hideturtle()
        self.t.speed(0)
        self.t.penup()

        self._align_to_lane()
        self.t.goto(self.x, self.y)
        self.t.setheading(self._heading())
        self.draw()

    def check_same_direction_ahead(self, vehicles):
        # Dans l'intersection, on ne bloque jamais
        if self.is_in_intersection():
            return False

    def _align_to_lane(self):
        lane_offset = 30
        if self.direction == 'east':
            self.y = -lane_offset
        elif self.direction == 'west':
            self.y = lane_offset
        elif self.direction == 'north':
            self.x = lane_offset
        elif self.direction == 'south':
            self.x = -lane_offset

    def _heading(self):
        return {'east': 0, 'west': 180, 'north': 90, 'south': 270}[self.direction]

    def draw(self):
        try:
            t = self.t
            t.clear()
            t.penup()
            t.goto(self.x, self.y)
            heading = self._heading()
            t.setheading(heading)

            body_color = self.color if self.state != 'accident' else '#555555'
            t.color("black", body_color)
            t.begin_fill()
            t.right(90);
            t.forward(self.width / 2);
            t.left(90)
            for _ in range(2):
                t.forward(self.length);
                t.left(90)
                t.forward(self.width);
                t.left(90)
            t.end_fill()

            # Habitacle
            t.penup();
            t.forward(12);
            t.left(90);
            t.forward(3);
            t.right(90)
            t.color("black", "#222222")
            t.begin_fill()
            for _ in range(2):
                t.forward(20);
                t.left(90)
                t.forward(self.width - 6);
                t.left(90)
            t.end_fill()

            # Phares dynamiques
            t.penup();
            t.goto(self.x, self.y);
            t.setheading(heading)
            t.forward(self.length - 3)
            t.left(90);
            t.forward(self.width / 2 - 5)
            # Jaune en mouvement, Blanc à l'arrêt
            light_color = "yellow" if self.state == 'moving' else "white"
            t.dot(6, light_color)
            t.backward(self.width - 10)
            t.dot(6, light_color)
        except:
            pass

    def set_target_direction(self, new_dir):
        self.target_direction = None
        self.has_turned = True

    def is_in_intersection(self):
        """Zone du carrefour proprement dite."""
        return -155 < self.x < 155 and -155 < self.y < 155

    def is_on_crosswalk(self):
        """Zone des passages piétons."""
        # Nord
        if -60 < self.x < 60 and 70 < self.y < 120: return True
        # Sud
        if -60 < self.x < 60 and -120 < self.y < -70: return True
        # Est
        if 70 < self.x < 120 and -60 < self.y < 60: return True
        # Ouest
        if -120 < self.x < -70 and -60 < self.y < 60: return True
        return False

    def check_collision(self, vehicles):
        # Distance de sécurité proportionnelle à la vitesse (Réalisme)
        safe_dist = 70 + (self.speed * 5)

        for other in vehicles:
            if other == self: continue
            dist = math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

            # 1. Suivi de véhicule (même voie)
            if self.direction == other.direction:
                is_ahead = False
                if self.direction == 'east' and other.x > self.x:
                    is_ahead = True
                elif self.direction == 'west' and other.x < self.x:
                    is_ahead = True
                elif self.direction == 'north' and other.y > self.y:
                    is_ahead = True
                elif self.direction == 'south' and other.y < self.y:
                    is_ahead = True

                if is_ahead and dist < safe_dist:
                    return True

            # 2. Priorité de virage (Règle réelle : on laisse passer celui qui vient en face si on tourne à gauche)
            if self.is_in_intersection() and self.target_direction:
                # Logique simplifiée de priorité en face à face
                opposites = {'east': 'west', 'west': 'east', 'north': 'south', 'south': 'north'}
                if other.direction == opposites[self.direction] and dist < 100:
                    # Si je tourne à gauche (sens anti-horaire en Turtle)
                    return True

        return False

    # ==================== MÉTHODE CORRIGÉE V3 : PRIORITÉ À DROITE SANS DEADLOCK ====================
    def check_priority_night_mode(self, vehicles):
        """
        Vérifie la priorité à droite en mode nuit.
        Retourne True si un véhicule prioritaire EN MOUVEMENT approche de l'intersection.

        CORRECTION V3 : On ne cède le passage que si le véhicule prioritaire est EN MOUVEMENT.
        Cela évite le deadlock où tous les véhicules attendent mutuellement.
        """
        # Définir qui a la priorité sur qui (priorité à droite)
        priority_map = {
            'east': 'north',  # East cède le passage à North (qui vient de sa droite)
            'north': 'west',  # North cède le passage à West
            'west': 'south',  # West cède le passage à South
            'south': 'east'  # South cède le passage à East
        }

        priority_direction = priority_map.get(self.direction)
        if not priority_direction:
            return False

        # Zone d'approche de l'intersection
        approach_zone = 180

        for other in vehicles:
            if other == self:
                continue

            # Vérifier si l'autre véhicule vient de la direction prioritaire
            if other.direction == priority_direction:
                # ✅ CORRECTION V3 : Vérifier que l'autre véhicule est EN MOUVEMENT
                if other.state != 'moving':
                    continue  # Si l'autre est arrêté, on ne lui cède pas le passage

                # Calculer la distance de l'autre véhicule à l'intersection
                other_dist_to_intersection = self._distance_to_intersection(other)
                my_dist_to_intersection = self._distance_to_intersection(self)

                # Si l'autre véhicule est dans la zone d'approche
                if other_dist_to_intersection < approach_zone:
                    # Si l'autre est plus proche de l'intersection ou déjà engagé
                    if other_dist_to_intersection <= my_dist_to_intersection or other.is_in_intersection():
                        return True  # Je dois céder le passage

        return False

    # ==================== MÉTHODE CORRIGÉE V3 : COLLISION DANS L'INTERSECTION ====================
    def check_intersection_collision_night_mode(self, vehicles):
        """
        Vérifie s'il y a un risque de collision dans l'intersection en mode nuit.
        Retourne True si un autre véhicule EN MOUVEMENT est trop proche dans l'intersection.

        CORRECTION V3 : On ne s'arrête que si l'autre véhicule est EN MOUVEMENT.
        """
        if not self.is_in_intersection():
            return False

        collision_distance = 50  # Distance minimale de sécurité dans l'intersection

        for other in vehicles:
            if other == self:
                continue

            # ✅ CORRECTION V3 : Vérifier que l'autre véhicule est EN MOUVEMENT
            if other.state != 'moving':
                continue  # Si l'autre est arrêté, pas de risque immédiat

            # Si l'autre véhicule est aussi dans l'intersection
            if other.is_in_intersection():
                dist = math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

                # Si trop proche, risque de collision
                if dist < collision_distance:
                    # Vérifier si on a la priorité
                    priority_map = {
                        'east': 'north',
                        'north': 'west',
                        'west': 'south',
                        'south': 'east'
                    }

                    priority_direction = priority_map.get(self.direction)

                    # Si l'autre véhicule vient de ma direction prioritaire, je dois m'arrêter
                    if other.direction == priority_direction:
                        return True

                    # Si on vient de directions perpendiculaires, vérifier qui est le plus proche du centre
                    # Celui qui est le plus avancé a la priorité
                    if self._distance_to_intersection(other) < self._distance_to_intersection(self):
                        return True

        return False

    def _distance_to_intersection(self, vehicle):
        """Calcule la distance approximative d'un véhicule au centre de l'intersection."""
        intersection_center = (0, 0)
        return math.sqrt((vehicle.x - intersection_center[0]) ** 2 +
                         (vehicle.y - intersection_center[1]) ** 2)

    # ==================== MÉTHODE MOVE FINALE V3 ====================
    def move(self, vehicles, traffic_light_system):
        # Détection du mode nuit
        is_night_mode = traffic_light_system.is_night_mode()

        if self.state == 'accident':
            return

        # ==================== MODE NUIT : GESTION ANTI-DEADLOCK ====================
        if is_night_mode:
            # DANS L'INTERSECTION : Vérifier les collisions avec véhicules EN MOUVEMENT
            if self.is_in_intersection():
                if self.check_intersection_collision_night_mode(vehicles):
                    self.stop()
                else:
                    self.go()
            # AVANT L'INTERSECTION : Vérifier priorité à droite
            else:
                # Ligne d'arrêt réelle (avant le passage piéton)
                at_stop_line = False
                if self.direction == 'east' and -180 < self.x < -145:
                    at_stop_line = True
                elif self.direction == 'west' and 145 < self.x < 180:
                    at_stop_line = True
                elif self.direction == 'north' and -180 < self.y < -145:
                    at_stop_line = True
                elif self.direction == 'south' and 145 < self.y < 180:
                    at_stop_line = True

                if at_stop_line:
                    # Vérifier s'il y a un véhicule prioritaire EN MOUVEMENT
                    if self.check_priority_night_mode(vehicles):
                        self.stop()
                    # Vérifier également les collisions normales
                    elif self.check_collision(vehicles):
                        self.stop()
                    else:
                        # Temps de réaction humain au démarrage
                        if self.state == 'stopped':
                            self.waiting_since += 0.04
                            if self.waiting_since >= self.reaction_time:
                                self.go()
                                self.waiting_since = 0
                        else:
                            self.go()
                elif self.check_collision(vehicles):
                    self.stop()
                else:
                    self.go()

        # ==================== MODE NORMAL : FEUX TRICOLORES ====================
        else:
            # RÈGLE RÉELLE : Si on est déjà engagé dans l'intersection, on NE S'ARRÊTE PAS
            if self.is_in_intersection():
                self.go()
            else:
                light_state = traffic_light_system.get_axe_etat(self.direction)

                # Ligne d'arrêt réelle (avant le passage piéton)
          
                at_stop_line = False
                if self.direction == 'east' and -180 < self.x < -145:
                    at_stop_line = True
                elif self.direction == 'west' and 145 < self.x < 180:
                    at_stop_line = True
                elif self.direction == 'north' and -180 < self.y < -145:
                    at_stop_line = True
                elif self.direction == 'south' and 145 < self.y < 180:
                    at_stop_line = True


                # RÈGLE RÉELLE : Ne pas s'engager si le carrefour est bloqué
                path_blocked = False
                if at_stop_line:
                    for v in vehicles:
                        if v != self and v.is_in_intersection():
                            path_blocked = True
                            break

                if at_stop_line and light_state in ('ROUGE', 'ORANGE'):
                    self.stop()
                elif self.check_collision(vehicles):
                    self.stop()
                else:
                    # Temps de réaction humain au démarrage
                    if self.state == 'stopped':
                        self.waiting_since += 0.04  # Incrément basé sur le timer de 40ms
                        if self.waiting_since >= self.reaction_time:
                            self.go()
                            self.waiting_since = 0
                    else:
                        self.go()

        if self.state == 'moving':
            self.check_turn()
            if self.direction == 'east':
                self.x += self.speed
            elif self.direction == 'west':
                self.x -= self.speed
            elif self.direction == 'north':
                self.y += self.speed
            elif self.direction == 'south':
                self.y -= self.speed

        self.draw()

    def check_turn(self):
        if self.has_turned or not self.target_direction: return
        # Virage fluide au centre de la voie
        tp = 30
        should_turn = False
        if self.direction == 'east' and self.x >= -tp:
            if self.target_direction == 'north':
                self.x, self.y = tp, -30;
                should_turn = True
            elif self.target_direction == 'south':
                self.x, self.y = -tp, -30;
                should_turn = True
        elif self.direction == 'west' and self.x <= tp:
            if self.target_direction == 'north':
                self.x, self.y = tp, 30;
                should_turn = True
            elif self.target_direction == 'south':
                self.x, self.y = -tp, 30;
                should_turn = True
        elif self.direction == 'north' and self.y >= -tp:
            if self.target_direction == 'east':
                self.x, self.y = 30, -tp;
                should_turn = True
            elif self.target_direction == 'west':
                self.x, self.y = 30, tp;
                should_turn = True
        elif self.direction == 'south' and self.y <= tp:
            if self.target_direction == 'east':
                self.x, self.y = -30, -tp;
                should_turn = True
            elif self.target_direction == 'west':
                self.x, self.y = -30, tp;
                should_turn = True

        if should_turn:
            self.direction = self.target_direction
            self.target_direction = None
            self.has_turned = True
            self.t.setheading(self._heading())

    def stop(self):
        self.state = 'stopped'

    def go(self):
        self.state = 'moving'

    def clear_turtle(self):
        try:
            self.t.clear()
            self.t.hideturtle()
        except:
            pass