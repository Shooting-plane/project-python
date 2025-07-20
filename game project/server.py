# server.py
import socket
import threading
import json
import pygame
from player import Player

# Config
HOST = '127.0.0.1'
PORT = 8182
WIDTH, HEIGHT = 800, 600
FPS = 60

# Game init
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Players
players = {
    "A": Player("assets/player.png", 100, HEIGHT // 2),
    "B": Player("assets/player.png", 600, HEIGHT // 2)
}

inputs = {"A": [], "B": []}

# Networking
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(2)
print(f"🟢 Server listening on {HOST}:{PORT}")

conns = {}
addrs = {}

# Gửi trạng thái game tới client
def broadcast_state():
    state = {
        pid: {"x": p.rect.x, "y": p.rect.y}
        for pid, p in players.items()
    }
    msg = json.dumps(state).encode()
    for conn in conns.values():
        try:
            conn.sendall(msg + b'\n')
        except:
            continue

# Nhận input từ client
def handle_client(pid, conn):
    while True:
        try:
            data = conn.recv(1024).decode().strip()
            if not data:
                break
            inputs[pid] = json.loads(data)
        except:
            break
    conn.close()
    print(f"❌ Mất kết nối từ {pid}")

# Chấp nhận client
for pid in ["A", "B"]:
    conn, addr = server.accept()
    conns[pid] = conn
    addrs[pid] = addr
    print(f"✅ {pid} kết nối từ {addr}")
    conn.sendall(pid.encode())
    threading.Thread(target=handle_client, args=(pid, conn), daemon=True).start()

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Xử lý input
    for pid, cmd in inputs.items():
        players[pid].handle_input(cmd)

    # Update
    screen.fill((30, 30, 60))
    for p in players.values():
        p.update()
        p.draw(screen)

    broadcast_state()
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()