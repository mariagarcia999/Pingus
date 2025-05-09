import asyncio
import random
import sys

# Constantes
NUM_BOTS = 3
TRACK_LENGTH = 30
REFRESH_TIME = 0.3
NUM_RONDAS = 6
BOT_NAMES = ["Pinga", "Rocky Jr", "Pingu"]

BOT_ASCII = [" (o_", " //\\", " V_/_"]
FALLEN_ASCII = [" ~/~A", "  \\\\/", "  ~o)"]
FLY_ASCII = [" \\|/", "  o", " /|\\"]
WINNER_ASCII_FRAMES = [[" >o)", " /\\", " _\\_V"], [" (o<", " //\\", " V_/_"]]
LOSER_ASCII_FRAMES = [[" (*_", " //\\", " V_/_"], [" _*)", " /\\", " _\\_V"]]


class Server:
    def __init__(self):
        self.positions = [0] * NUM_BOTS
        self.fallen_flags = [False] * NUM_BOTS
        self.finish_order = []
        self.lock = asyncio.Lock()
        self.fly_pos = None
        self.fly_target = None
        self.fly_active = False

    async def start_fly(self):
        if random.random() < 0.5:
            self.fly_pos = random.randint(5, TRACK_LENGTH - 5)
            self.fly_target = random.randint(0, NUM_BOTS - 1)
            self.fly_active = True
            asyncio.create_task(self.run_fly())

    async def run_fly(self):
        while self.fly_active and not self.is_finished():
            await asyncio.sleep(random.uniform(1.0, 2.5))
            async with self.lock:
                if self.fly_pos is not None:
                    move = random.choice([-1, 0, 1])
                    self.fly_pos = max(5, min(TRACK_LENGTH - 5, self.fly_pos + move))

    async def request_move(self, bot_id):
        async with self.lock:
            if self.fallen_flags[bot_id]:
                self.positions[bot_id] = 0
                self.fallen_flags[bot_id] = False
                return
            if self.positions[bot_id] < TRACK_LENGTH:
                self.positions[bot_id] += 1
                if (self.fly_active and self.fly_pos is not None and
                    self.fly_target == bot_id and
                    self.positions[bot_id] == self.fly_pos):
                    self.fallen_flags[bot_id] = True
                    self.fly_pos = None
                    self.fly_active = False
                if self.positions[bot_id] == TRACK_LENGTH:
                    self.finish_order.append(bot_id)

    def is_finished(self):
        return len(self.finish_order) == NUM_BOTS


async def run_bot(bot_id, server):
    while server.positions[bot_id] < TRACK_LENGTH:
        await asyncio.sleep(random.uniform(0.1, 0.4))
        await server.request_move(bot_id)


async def print_loop(server, round_number, scores):
    while not server.is_finished():
        sys.stdout.write("\033[H\033[J")
        print(f"RONDA {round_number + 1}/{NUM_RONDAS}".center(50))
        print(" MARCADOR: " + " | ".join([f"{BOT_NAMES[i]}: {scores[i]} pts" for i in range(NUM_BOTS)]))
        print()
        for i in range(NUM_BOTS):
            pos = min(server.positions[i], TRACK_LENGTH - 1)
            print("          ┌" + "─" * TRACK_LENGTH + "┐")
            for j in range(3):
                line = [" "] * TRACK_LENGTH
                art = FALLEN_ASCII[j] if server.fallen_flags[i] else BOT_ASCII[j]
                start = max(0, pos - len(art) + 1)
                for k, ch in enumerate(art):
                    if start + k < TRACK_LENGTH:
                        line[start + k] = ch
                if server.fly_active and server.fly_pos is not None and server.fly_target == i:
                    fly = FLY_ASCII[j]
                    fstart = max(0, server.fly_pos - len(fly) + 1)
                    for k, ch in enumerate(fly):
                        if fstart + k < TRACK_LENGTH:
                            line[fstart + k] = ch
                prefix = f"{BOT_NAMES[i]:>9}" if j == 1 else "         "
                print(f"{prefix} │{''.join(line)}│")
            print("          └" + "─" * TRACK_LENGTH + "┘\n")
        await asyncio.sleep(REFRESH_TIME)


async def show_final_animation(winner_id, duration=3, interval=0.4):
    start_time = asyncio.get_event_loop().time()
    pos = TRACK_LENGTH - 1
    while asyncio.get_event_loop().time() - start_time < duration:
        for frame_index in range(len(WINNER_ASCII_FRAMES)):
            sys.stdout.write("\033[H\033[J")
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
            await asyncio.sleep(interval)


async def run_race(round_number, scores):
    server = Server()
    await server.start_fly()
    bots = [run_bot(i, server) for i in range(NUM_BOTS)]
    printer = asyncio.create_task(print_loop(server, round_number, scores))
    await asyncio.gather(*bots)
    await printer

    for i, bot_id in enumerate(server.finish_order):
        if i == 0:
            scores[bot_id] += 3
        elif i == 1:
            scores[bot_id] += 1

    print()
    await show_final_animation(server.finish_order[0])
    return scores


async def main():
    scores = [0] * NUM_BOTS
    for round_number in range(NUM_RONDAS):
        scores = await run_race(round_number, scores)

    winner_id = max(range(NUM_BOTS), key=lambda i: scores[i])
    print("MARCADOR FINAL:")
    for i in range(NUM_BOTS):
        print(f"{BOT_NAMES[i]}: {scores[i]} puntos")
    print("\nGANADOR:")
    print(f"\033[95m{BOT_NAMES[winner_id]} <3<3<3\033[0m")


if __name__ == "__main__":
    asyncio.run(main())
