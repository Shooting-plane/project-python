
import socket
import threading
import json
import pygame
from player import Player

# Config
SERVER_IP = '127.0.0.1'  
PORT = 8182
WIDTH, HEIGHT = 800, 600
FPS = 60

# Pygame init
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Nhận ID từ server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, PORT))
player_id = client.recv(1024).decode()
print(f"🔵 Tôi là Player {player_id}")

# Tạo đối tượng player điều khiển chính
img_path = "assets/player.png"
my_player = Player(img_path, 100, HEIGHT // 2)

game_state = {}

# Nhận dữ liệu trạng thái từ server
def listen_thread():
    buffer = ""
    while True:
        try:
            buffer += client.recv(1024).decode()
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                game_state.update(json.loads(line))
        except:
            break

threading.Thread(target=listen_thread, daemon=True).start()

# Gửi phím bấm mỗi frame
def get_input():
    keys = pygame.key.get_pressed()
    cmds = []
    if keys[pygame.K_LEFT]: cmds.append("LEFT")
    if keys[pygame.K_RIGHT]: cmds.append("RIGHT")
    if keys[pygame.K_UP]: cmds.append("UP")
    if keys[pygame.K_DOWN]: cmds.append("DOWN")
    return cmds

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    cmds = get_input()
    try:
        client.sendall(json.dumps(cmds).encode())
    except:
        break

    screen.fill((30, 30, 60))

    # Vẽ tất cả người chơi từ server
    for pid, pos in game_state.items():
        if pid == player_id:
            my_player.rect.x, my_player.rect.y = pos["x"], pos["y"]
            my_player.draw(screen)
        else:
            temp_img = pygame.image.load("assets/player.png").convert_alpha()
            temp_img = pygame.transform.scale(temp_img, (50, 50))
            screen.blit(temp_img, (pos["x"], pos["y"]))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
client.close()
