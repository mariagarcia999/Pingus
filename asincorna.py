import asyncio
import random
import sys

num_pingus = 3
len_track = 30 #longitud de la pista
waiting = 0.3 #este es el tiempo de espera entre cada movimiento
num_rounds = 6
names_pingus = ["Pinga", "Rocky Jr", "Pingu"]

pingus= [
    " (o_",
    " //\\",
    " V_/_"
]

pingu_caido  = [
    " ~/~A",
    "  \\\/",
    "  ~o)"
]

mosca = [
    " \|/",
    "  o",
    " /|\"
]

pingu_happy = [ #ganador
    [" >o)", " /\\\", " _\\_V"],
    [" (o<", " //\\", " V_/_"]
] 

pingu_sad = [ #perdedor
    [" (*_", " //\\", " V_/_"],
    [" _*)", " /\\\\", " _\\_V"]
]



class Server:
    def __init__(self):
        self.position = [0] * num_pingus #posiciones de los pingus en la pista
        self.caido = [False] * num_pingus #indica si hay algún pingu caido:( (es bool)
        self.finish_order = []
        self.lock = asyncio.Lock() #asíncrono, datos compartidos
        self.position_m = None #mosca en pista
        self.target = None
        self.m_up = False #está la mosca despierta? (solo hace daño si lo está)

    async def start_mosca(self):
        if random.random() < 0.5: #solo se ejecuta la mitad de las veces
            self.position_m = random.randint(5, len_track - 5) #posicion aleatoria
            self.target = random.randint(0, num_pingus - 1) #pingu aleatorio 
            self.m_up = True
            asyncio.create_task(self.ejecutar_mosca()) #la despierta y lanza la tarea

    async def ejecutar_mosca(self):
        while self.m_up and not self.hass_finished():
            await asyncio.sleep(random.uniform(1.0, 2.5)) #espera un tiempo para que la mosca se mueva
            async with self.lock:
                if self.position_m is not None: 
                    move = random.choice([-1, 0, 1]) # o la mueve o a la deja quieta
                    self.position_m = max(5, min(len_track - 5, self.position_m + move)) 

    async def request_move(self, pingu_id):
        async with self.lock:
            if self.caido[pingu_id]: #si está caído vuelve al inicio y luego se pone otra vez como no caido(false)
                self.position[pingu_id] = 0
                self.caido[pingu_id] = False
                return
            if self.position[pingu_id] < len_track: #si no ha llegado a la meta avanza una posicion
                self.position[pingu_id] += 1
                if (self.m_up and self.position_m is not None and #si llega a la misma posicion que la mosca
                    self.target == pingu_id and
                    self.position[pingu_id] == self.position_m):
                    self.caido[pingu_id] = True #se cae:(
                    self.position_m = None #desaparece la mosca
                    self.m_up = False
                if self.position[pingu_id] == len_track: #ha llegado a la meta entonces se añade a la lista de finish_order
                    self.finish_order.append(pingu_id)

    def hass_finished(self):
        return len(self.finish_order) == num_pingus #si han llegado todos los pingus a la meta


async def run_pingu(pingu_id, server):
    while server.position[pingu_id] < len_track:
        await asyncio.sleep(random.uniform(0.1, 0.4))
        await server.request_move(pingu_id) #mientras que no esté en la meta sigue intentando ab¡vanzar


async def animations(server, round_num, scores): 
    while not server.hass_finished():
        sys.stdout.write("\033[H\033[J") #un truquito para limpiar la pantalla jijiji
        print(f"RONDA {round_num + 1}/{num_rounds}".center(50))
        print(" MARCADOR: " + " | ".join([f"{names_pingus[i]}: {scores[i]} pts" for i in range(num_pingus)]))
        print()
        for i in range(num_pingus): #pista
            pos = min(server.position[i], len_track - 1)
            print("          ┌" + "─" * len_track + "┐")
            for j in range(3): #pingus
                line = [" "] * len_track
                art = pingu_caido[j] if server.caido[i] else pingus[j]
                start = max(0, pos - len(art) + 1)
                for k, ch in enumerate(art):
                    if start + k < len_track:
                        line[start + k] = ch
                if server.m_up and server.position_m is not None and server.target == i: #mosca
                    fly = mosca[j]
                    fstart = max(0, server.position_m - len(fly) + 1)
                    for k, ch in enumerate(fly):
                        if fstart + k < len_track:
                            line[fstart + k] = ch
                prefix = f"{names_pingus[i]:>9}" if j == 1 else "         " #nombres de los pingus
                print(f"{prefix} │{''.join(line)}│")
            print("          └" + "─" * len_track + "┘\n")
        await asyncio.sleep(waiting)


async def bailecito(winner_id, d=3, wait_time=0.4):
    start_time = asyncio.get_event_loop().time() #cogemos el tiempo iniial y vamos ejecutando hasta que acabe
    pos = len_track - 1
    while asyncio.get_event_loop().time() - start_time < d:
        for frame_index in range(len(pingu_happy)):
            sys.stdout.write("\033[H\033[J")
            for pingu_id in range(num_pingus): #elegir el pingu ganador
                is_winner = (pingu_id == winner_id)
                frame = pingu_happy[frame_index] if is_winner else pingu_sad[frame_index]
                for j, line in enumerate(frame): #dibujos
                    track_line = [" "] * len_track
                    insert = max(0, pos - len(line) + 1)
                    for k, ch in enumerate(line):
                        if insert + k < len_track:
                            track_line[insert + k] = ch
                    prefix = f"{names_pingus[pingu_id]:>9}" if j == 1 else "         "
                    print(f"{prefix} │{''.join(track_line)}│")
                print()
            await asyncio.sleep(wait_time)


async def carrera(round_num, scores): #crear el servidor y encender a la mosca y pingus
    server = Server()
    await server.start_mosca()
    bots = [run_pingu(i, server) for i in range(num_pingus)]
    printer = asyncio.create_task(animations(server, round_num, scores)) #lanzamos la animacion
    await asyncio.gather(*bots) #terminados
    await printer

    for i, pingu_id in enumerate(server.finish_order):
        if i == 0:
            scores[pingu_id] += 3
        elif i == 1:
            scores[pingu_id] += 1

    print()
    await bailecito(server.finish_order[0])
    return scores


async def main():
    scores = [0] * num_pingus
    for round_num in range(num_rounds):
        scores = await carrera(round_num, scores) #puntos y ejecutar todas las rondas

    winner_id = max(range(num_pingus), key=lambda i: scores[i]) #buscamos al pingu ganador y mostramos los puntos
    print("MARCADOR:")
    for i in range(num_pingus):
        print(f"{names_pingus[i]}: {scores[i]} puntos")
    print("\nGANADOR:")
    print(f"\033[95m{names_pingus[winner_id]} <3<3<3\033[0m")


if __name__ == "__main__":
    asyncio.run(main())
