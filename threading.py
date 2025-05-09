import threading
import time
import random
import sys

# Constantes
NUM_BOTS = 3
TRACK_LENGTH = 30
REFRESH_TIME = 0.3
NUM_RONDAS = 6
BOT_NAMES = ["Pinga", "Rocky Jr", "Pingu"]

BOT_ASCII = [
    " (o_",
    " //\\",
    " V_/_"
]

FALLEN_ASCII = [
    " ~/~A",
    "  \\\\/",
    "  ~o)"
]

FLY_ASCII = [
    " \\|/",
    "  o",
    " /|\\"
]

WINNER_ASCII_FRAMES = [
    [" >o)", " /\\\\", " _\\_V"],
    [" (o<", " //\\", " V_/_"]
]

LOSER_ASCII_FRAMES = [
    [" (*_", " //\\", " V_/_"],
    [" _*)", " /\\\\", " _\\_V"]
]

class Fly(threading.Thread):
    def __init__(self, server, fly_id):
        super().__init__()
        self.server = server
        self.fly_id = fly_id
        self.target = random.randint(0, NUM_BOTS - 1)
        self.position = random.randint(5, TRACK_LENGTH - 5)
        self.active = True

    def run(self):
        while self.active and not self.server.finished():
            time.sleep(random.uniform(1.0, 2.5))
            with self.server.lock:
                self.position = max(5, min(TRACK_LENGTH - 5, self.position + random.choice([-1, 0, 1])))
                self.server.fly_positions[self.fly_id] = self.position
                self.server.fly_targets[self.fly_id] = self.target

class Server:
    def __init__(self):
        self.lock = threading.Lock()
        self.positions = [0] * NUM_BOTS
        self.finish_order = []
        self.fallen_flags = [False] * NUM_BOTS
        self.fly_positions = []
        self.fly_targets = []
        self.flies = []
        self.init_flies()

    def init_flies(self):
        num_flies = random.randint(0, 2)
        self.fly_positions = [random.randint(5, TRACK_LENGTH - 5) for _ in range(num_flies)]
        self.fly_targets = [random.randint(0, NUM_BOTS - 1) for _ in range(num_flies)]
        for i in range(num_flies):
            fly = Fly(self, i)
            self.flies.append(fly)
            fly.start()

    def request_move(self, bot_id):
        with self.lock:
            if self.fallen_flags[bot_id]:
                self.positions[bot_id] = 0
                self.fallen_flags[bot_id] = False
                return
            if self.positions[bot_id] < TRACK_LENGTH:
                self.positions[bot_id] += 1
                for i in range(len(self.fly_positions)):
                    if self.fly_targets[i] == bot_id and self.positions[bot_id] == self.fly_positions[i]:
                        self.fallen_flags[bot_id] = True
                        self.fly_positions[i] = None
                        self.flies[i].active = False
                if self.positions[bot_id] == TRACK_LENGTH:
                    self.finish_order.append(bot_id)

    def get_positions(self):
        with self.lock:
            return list(self.positions), list(self.fallen_flags), list(self.fly_positions), list(self.fly_targets)

    def finished(self):
        return len(self.finish_order) == NUM_BOTS

    def simulate_network_delay(self):
        time.sleep(random.uniform(0.1, 0.6))

class Bot(threading.Thread):
    def __init__(self, bot_id, server: Server):
        super().__init__()
        self.bot_id = bot_id
        self.server = server

    def run(self):
        while self.server.positions[self.bot_id] < TRACK_LENGTH:
            self.server.simulate_network_delay()
            self.server.request_move(self.bot_id)

def print_header(round_number, scores):
    sys.stdout.write("\033[H")
    sys.stdout.write("\033[J")
    print(f"RONDA {round_number + 1}/{NUM_RONDAS}".center(50))
    print(" MARCADOR: " + " | ".join([f"{BOT_NAMES[i]}: {scores[i]} pts" for i in range(NUM_BOTS)]))
    print()

def print_track(positions, fallen_flags, flies, fly_targets):
    for i in range(NUM_BOTS):
        pos = min(positions[i], TRACK_LENGTH - 1)
        print("          ┌" + "─" * TRACK_LENGTH + "┐")
        for j in range(3):
            line = [" "] * TRACK_LENGTH
            part = FALLEN_ASCII[j] if fallen_flags[i] else BOT_ASCII[j]
            start = max(0, pos - len(part) + 1)
            for k, ch in enumerate(part):
                if start + k < TRACK_LENGTH:
                    line[start + k] = ch
            for fly_pos, target_id in zip(flies, fly_targets):
                if fly_pos is not None and target_id == i:
                    fly_part = FLY_ASCII[j]
                    fstart = max(0, fly_pos - len(fly_part) + 1)
                    for k, ch in enumerate(fly_part):
                        if fstart + k < TRACK_LENGTH:
                            line[fstart + k] = ch
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
    bots = [Bot(i, server) for i in range(NUM_BOTS)]

    for bot in bots:
        bot.start()

    while not server.finished():
        positions, fallen_flags, flies, fly_targets = server.get_positions()
        print_header(round_number, scores)
        print_track(positions, fallen_flags, flies, fly_targets)
        time.sleep(REFRESH_TIME)

    for bot in bots:
        bot.join()

    for fly in server.flies:
        fly.active = False

    for i, bot_id in enumerate(server.finish_order):
        if i == 0:
            scores[bot_id] += 3
        elif i == 1:
            scores[bot_id] += 1

    print_header(round_number, scores)
    show_final_animation(server.finish_order[0])
    return scores

def main():
    scores = [0] * NUM_BOTS
    for round_number in range(NUM_RONDAS):
        scores = run_race(round_number, scores)

    winner_id = max(range(NUM_BOTS), key=lambda i: scores[i])

    print("MARCADOR FINAL:")
    for i in range(NUM_BOTS):
        print(f"{BOT_NAMES[i]}: {scores[i]} puntos")

    print("\nGANADOR:")
    print(f"\033[95m{BOT_NAMES[winner_id]} <3<3<3\033[0m")

if __name__ == "__main__":
    main()
