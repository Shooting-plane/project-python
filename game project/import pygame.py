import pygame
import sys
import importlib
from player import Player
from enemy import Enemy
from bullet import Bullet
from explosion import Explosion
from utils import draw_hud

pygame.init()
pygame.mixer.init()

# Cấu hình màn hình
WIDTH, HEIGHT = 412, 915
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bắn máy bay")
clock = pygame.time.Clock()
FPS = 60

# Âm thanh
volume = 0.5
pygame.mixer.music.load("assets/background.mp3")
pygame.mixer.music.set_volume(volume)
pygame.mixer.music.play(-1)

explode_sound = pygame.mixer.Sound("assets/explode.wav")
explode_sound.set_volume(volume)

shoot_sound = pygame.mixer.Sound("assets/shoot.wav")
shoot_sound.set_volume(volume)

# Explosion images
explosion_images = [
    pygame.image.load(f"assets/explosion{i}.png").convert_alpha()
    for i in range(1, 6)
]

# Font
font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 48)

# Trạng thái game
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAMEOVER = "gameover"
game_state = STATE_MENU

# Biến game
score = 0
player_health = 10
level = 1
last_shot_time = 0
frame_count = 0

# Nhóm sprite
player = Player()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
explosions = pygame.sprite.Group()

# Load level
loaded_background = None
loaded_level_number = None

def load_level(level_num):
    try:
        return importlib.import_module(f'level.level{level_num}')
    except ModuleNotFoundError:
        return importlib.import_module('level.level1')

def reset_game():
    global score, player_health, player, bullets, enemies, explosions
    global frame_count, last_shot_time, loaded_background, loaded_level_number
    score = 0
    player_health = 10
    frame_count = 0
    last_shot_time = 0
    loaded_background = None
    loaded_level_number = None
    player = Player()
    bullets.empty()
    enemies.empty()
    explosions.empty()

def show_menu():
    screen.fill((20, 20, 20))
    title = big_font.render("BẮN MÁY BAY", True, (255, 255, 0))
    start = font.render("Nhấn SPACE để chơi", True, (255, 255, 255))
    exit_text = font.render("ESC để thoát", True, (255, 0, 0))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
    screen.blit(start, (WIDTH // 2 - start.get_width() // 2, HEIGHT // 2))
    screen.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, HEIGHT // 2 + 40))

def show_gameover():
    screen.fill((0, 0, 0))
    over = big_font.render("GAME OVER", True, (255, 0, 0))
    retry = font.render("SPACE để chơi lại", True, (0, 255, 0))
    esc = font.render("ESC để thoát", True, (255, 255, 255))
    screen.blit(over, (WIDTH // 2 - over.get_width() // 2, HEIGHT // 3))
    screen.blit(retry, (WIDTH // 2 - retry.get_width() // 2, HEIGHT // 2))
    screen.blit(esc, (WIDTH // 2 - esc.get_width() // 2, HEIGHT // 2 + 40))

# Vòng lặp chính
running = True
while running:
    level = score // 100 + 1
    level_data = load_level(level)

    if loaded_level_number != level:
        loaded_background = None
        if hasattr(level_data, "background_image_path") and level_data.background_image_path:
            loaded_background = pygame.image.load(level_data.background_image_path).convert()
            loaded_background = pygame.transform.scale(loaded_background, screen.get_size())
        loaded_level_number = level

    if loaded_background:
        screen.blit(loaded_background, (0, 0))
    else:
        screen.fill(level_data.background_color)

    if game_state == STATE_MENU:
        show_menu()
    elif game_state == STATE_GAMEOVER:
        show_gameover()
    elif game_state == STATE_PLAYING:
        draw_hud(screen, score, player_health, level, font)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.rect.x -= player.speed
        if keys[pygame.K_RIGHT]:
            player.rect.x += player.speed
        if keys[pygame.K_UP]:
            player.rect.y -= player.speed
        if keys[pygame.K_DOWN]:
            player.rect.y += player.speed

        player.rect.x = max(0, min(player.rect.x, WIDTH - player.rect.width))
        player.rect.y = max(0, min(player.rect.y, HEIGHT - player.rect.height))

        bullets.update()
        enemies.update()
        explosions.update()

        screen.blit(player.image, player.rect)
        bullets.draw(screen)
        enemies.draw(screen)
        explosions.draw(screen)

        frame_count += 1
        if frame_count >= level_data.enemy_spawn_rate:
            if len(enemies) < level_data.max_enemies:
                enemies.add(Enemy(level_data.enemy_speed))
            frame_count = 0

        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for hit in hits:
            score += 10
            explosions.add(Explosion(hit.rect.center, explosion_images))
            explode_sound.play()

        if pygame.sprite.spritecollideany(player, enemies):
            player_health -= 1
            pygame.sprite.spritecollide(player, enemies, True)
            if player_health <= 0:
                game_state = STATE_GAMEOVER

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == STATE_MENU and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                reset_game()
                game_state = STATE_PLAYING
            elif event.key == pygame.K_ESCAPE:
                running = False

        if game_state == STATE_GAMEOVER and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                reset_game()
                game_state = STATE_PLAYING
            elif event.key == pygame.K_ESCAPE:
                running = False

    if game_state == STATE_PLAYING:
        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()
        if keys[pygame.K_SPACE] and (current_time - last_shot_time >= level_data.shoot_cooldown):
            player.shoot(bullets)
            shoot_sound.play()
            last_shot_time = current_time

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
sys.exit()
 