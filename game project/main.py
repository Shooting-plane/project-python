import pygame
import sys
import importlib  # Thêm để load level động
from player import Player
from enemy import Enemy
from bullet import Bullet
from utils import draw_hud 
# pyright: reportArgumentType=false

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((412, 915)) # Đang sử dụng kích thước của galaxy s20
pygame.display.set_caption("Bắn máy bay") # Tiêu đề của cửa sổ game
#icon = pygame.image.load("assets/icon.png") # cần file icon.png 
#icon = pygame.transform.scale(icon, (64, 64)) # Kích thước icon 
#pygame.display.set_icon(icon) 
clock = pygame.time.Clock() # đồng hồ fps

# Âm thanh
volume = 0.5  # Giá trị từ 0.0 (tắt tiếng) đến 1.0 (to nhất)

explode_sound = pygame.mixer.Sound("assets/explode.wav")  # tiếng địch nổ
shoot_sound = pygame.mixer.Sound("assets/shoot.wav")      # tiếng bắn
pygame.mixer.music.load("assets/background.mp3")          # nhạc nền

explode_sound.set_volume(volume)
shoot_sound.set_volume(volume)
pygame.mixer.music.set_volume(volume)

pygame.mixer.music.play(-1)  # lặp vô hạn

# Font, điểm, máu
font = pygame.font.SysFont("Arial", 24) #
score = 0
player_health = 10

player = Player()
player_group = pygame.sprite.GroupSingle(player)
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()

frame_count = 0
running = True
shoot_cooldown = 300  # Thời gian hồi chiêu (ms)
last_shot_time = 0    # Thời điểm bắn lần cuối

def load_level(level_num):
    try:
        return importlib.import_module(f'level.level{level_num}') # lưu ý tên file là level 
    except ModuleNotFoundError:
        return importlib.import_module('level.level1')

def reset_game():
    global score, player_health, bullets, enemies, player, player_group, frame_count, last_shot_time
    score = 0
    player_health = 10
    bullets.empty()
    enemies.empty()
    player = Player()
    player_group = pygame.sprite.GroupSingle(player)
    frame_count = 0
    last_shot_time = 0

while running:
    # Tính toán level hiện tại và nạp dữ liệu
    level = score // 100 + 1
    level_data = load_level(level)

    screen.fill(level_data.background_color)
    keys = pygame.key.get_pressed()
    current_time = pygame.time.get_ticks()  # Thời gian hiện tại (ms)

    for event in pygame.event.get(): # xu ly sự kiện
        if event.type == pygame.QUIT: # Nếu người dùng đóng cửa sổ
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if current_time - last_shot_time >= level_data.shoot_cooldown:
                bullet = player.shoot()
                bullets.add(bullet)
                shoot_sound.play()
                last_shot_time = current_time
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: # Điều kiện thoát game 2
            running = False

    # Cập nhật
    player.update(keys)
    bullets.update()
    enemies.update()

    # Sinh enemy
    frame_count += 1
    if frame_count >= level_data.enemy_spawn_rate:
        if len(enemies) < level_data.max_enemies:  # Giới hạn số lượng enemy
            enemies.add(Enemy(level_data.enemy_speed))
        frame_count = 0

    # Va chạm
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    for hit in hits:
        score += 10
        explode_sound.play()

    if pygame.sprite.spritecollideany(player, enemies):
        player_health -= 1
        pygame.sprite.spritecollide(player, enemies, True)
        if player_health <= 0:
            game_over = True
            while game_over:
                screen.fill((0, 0, 0))
                game_over_text = font.render("Game Over", True, (255, 0, 0)) #hiển thị chữ Game Over màu đỏ
                screen.blit(game_over_text, (20, 400)) #vị trí hiển thị chữ Game Over
                restart_text = font.render("Press R to Restart", True, (255, 255, 255)) #hiển thị chữ Press R to Restart màu trắng
                screen.blit(restart_text, (20, 440)) #vị trí hiển thị chữ Press R to Restart
                exit_text = font.render("Press ESC to Exit", True, (255, 255, 255)) #hiển thị chữ Press ESC to Exit màu trắng
                screen.blit(exit_text, (20, 480)) #vị trí hiển thị chữ Press ESC to Exit
                pygame.display.update()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN: # chờ sự kiện nhấn phím
                        if event.key == pygame.K_r:
                            reset_game()
                            game_over = False
                            break  # thoát vòng lặp game over
                        elif event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
            continue  # bỏ qua các bước cập nhật và vẽ tiếp theo nếu game over

    player_group.draw(screen)
    bullets.draw(screen)
    enemies.draw(screen)

    draw_hud(screen, score, player_health, level, font) # vẽ HUD trong file utils.py

    pygame.display.update()
    clock.tick(60) #60 fps

pygame.quit()
sys.exit()