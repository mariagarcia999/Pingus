import threading
import time
import random
import sys
import queue

# Constantes
NUM_BOTS = 3
TRACK_LENGTH = 30
REFRESH_TIME = 0.3
NUM_RONDAS = 6
BOT_NAMES = ["Pinga", "Rocky Jr", "Pingu"]

# Dibujo base
BOT_ASCII = [
    " (o_",
    " //\\",
    " V_/_"
]

# Animación del ganador
WINNER_ASCII_FRAMES = [
    [" >o)", " /\\\\", " _\\_V"],
    [" (o<", " //\\", " V_/_"]
]

# Animación de los perdedores
LOSER_ASCII_FRAMES = [
    [" (*_", " //\\", " V_/\""],
    [" _*)", " /\\\\", " _\\_V"]
]

class Server:
    def __init__(self):
        self.lock = threading.Lock()
        self.positions = [0] * NUM_BOTS
        self.finish_order = []
        self.msg_queues = [queue.Queue() for _ in range(NUM_BOTS)]

    def reset(self):
        with self.lock:
            self.positions = [0] * NUM_BOTS
            self.finish_order = []

    def request_move(self, bot_id):
        with self.lock:
            if self.positions[bot_id] < TRACK_LENGTH:
                self.positions[bot_id] += 1
                if self.positions[bot_id] == TRACK_LENGTH:
                    self.finish_order.append(bot_id)
                return True
            return False

    def get_positions(self):
        with self.lock:
            return list(self.positions)

    def finished(self):
        return len(self.finish_order) == NUM_BOTS

    def simulate_network_delay(self):
        time.sleep(random.uniform(0.1, 0.6))

class Bot(threading.Thread):
    def __init__(self, bot_id, server: Server, move_events: queue.Queue):
        super().__init__()
        self.bot_id = bot_id
        self.server = server
        self.move_events = move_events

    def run(self):
        while self.server.positions[self.bot_id] < TRACK_LENGTH:
            self.server.simulate_network_delay()
            moved = self.server.request_move(self.bot_id)
            if moved:
                self.move_events.put(self.bot_id)

def print_header(round_number, scores):
    sys.stdout.write("\033[H")
    sys.stdout.write("\033[J")
    print(f" RONDA {round_number + 1}/{NUM_RONDAS}".center(50))
    print(" MARCADOR: " + " | ".join([f"{BOT_NAMES[i]}: {scores[i]} pts" for i in range(NUM_BOTS)]))
    print()

def print_track(positions):
    for i in range(NUM_BOTS):
        pos = min(positions[i], TRACK_LENGTH - 1)

        print("          ┌" + "─" * TRACK_LENGTH + "┐")
        for j in range(3):
            line = [" "] * TRACK_LENGTH
            part = BOT_ASCII[j]
            start = max(0, pos - len(part) + 1)
            for k, ch in enumerate(part):
                if start + k < TRACK_LENGTH:
                    line[start + k] = ch
            prefix = f"{BOT_NAMES[i]:>9}" if j == 1 else "         "
            print(f"{prefix} │{''.join(line)}│")
        print("          └" + "─" * TRACK_LENGTH + "┘\n")
    sys.stdout.flush()

def show_final_animation(winner_id, duration=3, interval=0.4):
    start_time = time.time()
    pos = TRACK_LENGTH - 1
    while time.time() - start_time < duration:
        for frame_index in range(len(WINNER_ASCII_FRAMES)):
            sys.stdout.write("\033[H")
            sys.stdout.write("\033[J")
            for bot_id in range(NUM_BOTS):
                is_winner = (bot_id == winner_id)
                frame = WINNER_ASCII_FRAMES[frame_index] if is_winner else LOSER_ASCII_FRAMES[frame_index]
                for j, line in enumerate(frame):
                    track_line = [" "] * TRACK_LENGTH
                    insert = max(0, pos - len(line) + 1)
                    for k, ch in enumerate(line):
                        if insert + k < TRACK_LENGTH:
                            track_line[insert + k] = ch
                    prefix = f"{BOT_NAMES[bot_id]:>9}" if j == 1 else "         "
                    print(f"{prefix} │{''.join(track_line)}│")
                print()
            sys.stdout.flush()
            time.sleep(interval)

def run_race(round_number, scores):
    server = Server()
    move_events = queue.Queue()
    bots = [Bot(i, server, move_events) for i in range(NUM_BOTS)]

    for bot in bots:
        bot.start()

    while not server.finished():
        try:
            move_events.get(timeout=1)
            positions = server.get_positions()
            print_header(round_number, scores)
            print_track(positions)
            time.sleep(REFRESH_TIME)
        except queue.Empty:
            pass

    for bot in bots:
        bot.join()

    # Asignar puntos
    for i, bot_id in enumerate(server.finish_order):
        if i == 0:
            scores[bot_id] += 3
        elif i == 1:
            scores[bot_id] += 1

    # Animación al final de la ronda
    print_header(round_number, scores)
    show_final_animation(server.finish_order[0])
    return scores

def main():
    scores = [0] * NUM_BOTS
    for round_number in range(NUM_RONDAS):
        scores = run_race(round_number, scores)

    # Resultado final
    winner_id = max(range(NUM_BOTS), key=lambda i: scores[i])

    print(" MARCADOR:")
    for i in range(NUM_BOTS):
        print(f"{BOT_NAMES[i]}: {scores[i]} puntos")

    print("\n GANADOR:")
    print(f"\033[95m{BOT_NAMES[winner_id]} <3<3<3\033[0m")


if __name__ == "__main__":
    main()