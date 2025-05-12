import threading
import time
import random
import sys

num_pingus = 3
len_track = 30 #longitud de la pista
waiting = 0.3 #este es el tiempo de espera entre cada movimiento
num_rounds = 6
names_pingus = ["Pinga", "Rocky Jr", "Pingu"]

pingus = [
    " (o_",
    " //\\",
    " V_/_"
]

pingu_caido = [
    " ~/~A",
    "  \\\\/",
    "  ~o)"
]

mosca = [
    " \\|/",
    "  o",
    " /|\\"
]

pingu_happy = [ #ganador
    [" >o)", " /\\\\", " _\\_V"],
    [" (o<", " //\\", " V_/_"]
]

pingu_sad = [ #perdedor
    [" (*_", " //\\", " V_/_"],
    [" _*)", " /\\\\", " _\\_V"]
]

class Fly(threading.Thread):
        def __init__(self, server, fly_id):
                super().__init__()  # Inicializa la clase base Thread  # constructor de threads
                self.server = server 
                self.fly_id = fly_id  
                self.target = random.randint(0, num_pingus - 1) 
                self.position = random.randint(5, len_track - 5)  # posición y objetivo aleatoria
                self.active = True  #está la mosca despierta? (solo hace daño si lo está)

        def run(self):
        # Esta función se ejecuta cuando el pingüino comienza a correr.
        # Mientras no llegue al final, intentará avanzar paso a paso.
            while self.active and not self.server.hass_finished():  # carrera & mosca = on
                    time.sleep(random.uniform(1.0, 2.5))  # Espera un tiempo para que la mosca se mueva
                    with self.server.lock:  #evitar conflictos con otros hilos
                        self.position = max(5, min(len_track - 5, self.position + random.choice([-1, 0, 1]))) #puede ir a la derecha, izquierda o no moverse at all
                        self.server.position_m[self.fly_id] = self.position  
                        self.server.target[self.fly_id] = self.target  # actualiza posicio y objetivo

class Server:
        def __init__(self):
            self.lock = threading.Lock()  # Protege los datos
            self.position = [0] * num_pingus  #posiciones de los pingus en la pista
            self.caido = [False] * num_pingus  #indica si hay algún pingu caido:( (es bool)
            self.finish_order = []  
            self.position_m = []  #mosca en pista
            self.target = []  
            self.moscas = []  # moscas despiertas no?
            self.init_moscas()

        def init_moscas(self):
            #crea entre 0 y 2 moscas, para tampoco sobrecargalo y pues los v alanzando (hilos)
            num_flies = random.randint(0, 2)
            #las coloca en un aposicion aletaroia y seleccionan a un pinggu aleatorio, se pueden mover pq son agentes activos
            self.position_m = [random.randint(5, len_track - 5) for _ in range(num_flies)]
            self.target = [random.randint(0, num_pingus - 1) for _ in range(num_flies)]
            for i in range(num_flies):
                mosca = Fly(self, i)
                self.moscas.append(mosca)
                mosca.start()

        def request_move(self, pingu_id):
            with self.lock:
                if self.caido[pingu_id]: #si se ha caido vuelve al inicio
                    self.position[pingu_id] = 0
                    self.caido[pingu_id] = False
                    return
                if self.position[pingu_id] < len_track: #si no ha llegado a la met avanza
                    self.position[pingu_id] += 1
                    for i in range(len(self.position_m)):
                        if self.target[i] == pingu_id and self.position[pingu_id] == self.position_m[i]: #si se choca con mosca = cae
                            self.caido[pingu_id] = True
                            self.position_m[i] = None
                            self.moscas[i].active = False 
                    if self.position[pingu_id] == len_track: #meta=lista de llegados
                        self.finish_order.append(pingu_id)

        def get_position(self):
        # listas de posiciones, caidas, moscas y objetivos
            with self.lock:
                return list(self.position), list(self.caido), list(self.position_m), list(self.target)

        def hass_finished(self):
            return len(self.finish_order) == num_pingus

        def delay(self):
            time.sleep(random.uniform(0.1, 0.6))

class Bot(threading.Thread):
    # Esta clase representa un pingüino que corre en la pista.
    # Cada pingüino es un hilo que avanza paso a paso mientras la carrera está activa.
    def __init__(self, pingu_id, server: Server):
        # Se guarda el identificador del pingüino y una referencia al servidor del juego.
        super().__init__()
        self.pingu_id = pingu_id
        self.server = server

    def run(self):
        while self.server.position[self.pingu_id] < len_track:
            self.server.delay()  # Simula un pequeño retraso (como si hubiera red o tiempo de reacción)
            self.server.request_move(self.pingu_id)  # Solicita avanzar una casilla en la pista

def cabecera(round_num, scores):
    sys.stdout.write("\033[H")
    sys.stdout.write("\033[J")
    print(f"RONDA {round_num + 1}/{num_rounds}".center(50))
    print(" MARCADOR: " + " | ".join([f"{names_pingus[i]}: {scores[i]} pts" for i in range(num_pingus)]))
    print()

def pista(position, caido, position_m, target):
    # Esta función dibuja visualmente el estado actual de la pista en la consola.
    # Muestra cada pingüino con su posición, y si está caído o no.
    # También dibuja las moscas si están activas y apuntando a un pingüino.
    for i in range(num_pingus):
        pos = min(position[i], len_track - 1)
        print("          ┌" + "─" * len_track + "┐")
        for j in range(3):
            line = [" "] * len_track
            part = pingu_caido[j] if caido[i] else pingus[j]
            start = max(0, pos - len(part) + 1)
            for k, ch in enumerate(part):
                if start + k < len_track:
                    line[start + k] = ch
            for fly_pos, target_id in zip(position_m, target):
                if fly_pos is not None and target_id == i:
                    fly_part = mosca[j]
                    fstart = max(0, fly_pos - len(fly_part) + 1)
                    for k, ch in enumerate(fly_part):
                        if fstart + k < len_track:
                            line[fstart + k] = ch
            prefix = f"{names_pingus[i]:>9}" if j == 1 else "         "
            print(f"{prefix} │{''.join(line)}│")
        print("          └" + "─" * len_track + "┘\n")
    sys.stdout.flush()

def bailecito(winner_id, duration=3, interval=0.4):
    # Esta función muestra una animación al final de la carrera.
    # El pingüino que gana aparece feliz y los demás tristes.
    # La animación dura unos segundos y se actualiza en bucle.
    start_time = time.time()
    pos = len_track - 1
    while time.time() - start_time < duration:
        for frame_index in range(len(pingu_happy)):
            sys.stdout.write("\033[H")
            sys.stdout.write("\033[J")
            for pingu_id in range(num_pingus):
                is_winner = (pingu_id == winner_id)
                frame = pingu_happy[frame_index] if is_winner else pingu_sad[frame_index]
                for j, line in enumerate(frame):
                    track_line = [" "] * len_track
                    insert = max(0, pos - len(line) + 1)
                    for k, ch in enumerate(line):
                        if insert + k < len_track:
                            track_line[insert + k] = ch
                    prefix = f"{names_pingus[pingu_id]:>9}" if j == 1 else "         "
                    print(f"{prefix} │{''.join(track_line)}│")
                print()
            sys.stdout.flush()
            time.sleep(interval)

def carrera(round_num, scores):
    # Esta función representa una ronda completa de carrera.
    # Crea el servidor, lanza los pingüinos (hilos), actualiza pantalla,
    # espera que terminen y actualiza los puntajes según orden de llegada.
    server = Server()
    pingus_threads = [Bot(i, server) for i in range(num_pingus)]

    for pingu in pingus_threads:
        pingu.start()

    while not server.hass_finished():
        position, caido, position_m, target = server.get_position()
        cabecera(round_num, scores)
        pista(position, caido, position_m, target)
        time.sleep(waiting)

    for pingu in pingus_threads:
        pingu.join()

    for mosca in server.moscas:
        mosca.active = False

    for i, pingu_id in enumerate(server.finish_order):
        if i == 0:
            scores[pingu_id] += 3
        elif i == 1:
            scores[pingu_id] += 1

    cabecera(round_num, scores)
    bailecito(server.finish_order[0])
    return scores

def main():
    # Esta es la función principal del programa.
    # Ejecuta todas las rondas, acumula los puntajes y muestra al ganador final.
    scores = [0] * num_pingus
    for round_num in range(num_rounds):
        scores = carrera(round_num, scores)

    winner_id = max(range(num_pingus), key=lambda i: scores[i])

    print("MARCADOR FINAL:")
    for i in range(num_pingus):
        print(f"{names_pingus[i]}: {scores[i]} puntos")

    print("\nGANADOR:")
    print(f"\033[95m{names_pingus[winner_id]} <3<3<3\033[0m")

if __name__ == "__main__":
    main()
