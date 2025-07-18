import pygame
import sys
import importlib
from player import Player
from enemy import Enemy
from bullet import Bullet
from explosion import Explosion
from utils import draw_hud
import socket
from boss import Boss
# pyright: reportArgumentType=false

pygame.init()
pygame.mixer.init()

# Cấu hình màn hình
WIDTH, HEIGHT = 412, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bắn máy bay")
#icon = pygame.image.load("assets/icon.png") # cần file icon.png 
#icon = pygame.transform.scale(icon, (64, 64)) # Kích thước icon 
#pygame.display.set_icon(icon) 
clock = pygame.time.Clock()
FPS = 60

# Âm thanh
volume = 0.5
pygame.mixer.music.load("game project/assets/background.mp3")
pygame.mixer.music.set_volume(volume)
pygame.mixer.music.play(-1)

explode_sound = pygame.mixer.Sound("game project/assets/explode.wav")
explode_sound.set_volume(volume)

shoot_sound = pygame.mixer.Sound("game project/assets/shoot.wav")
shoot_sound.set_volume(volume)

# hiệu ứng nổ
explosion_images = []  

for i in range(1, 6):  
    image_path = f"game project/assets/explosion{i}.png"                    
    original_image = pygame.image.load(image_path).convert_alpha()
    resized_image = pygame.transform.scale(original_image, (80, 80)) 
    explosion_images.append(resized_image)                        


# Font
font = pygame.font.SysFont(" Segoe UI ", 24)
big_font = pygame.font.SysFont(" Segoe UI ", 48)

# Lấy IP address
try:
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
except:
    ip_address = "Unknown"

# Trạng thái game
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAMEOVER = "gameover"
STATE_SETTING = "setting"  # Thêm trạng thái setting
game_state = STATE_MENU

# Biến game
score = 0
player_health = 1000
max_health = 10
level = 1
last_shot_time = 0
frame_count = 0
health_flash_timer = 0
HEALTH_FLASH_DURATION = 15  # frame

# Nhóm đối tượng
player = Player()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
explosions = pygame.sprite.Group()

# Load level
loaded_background = None
loaded_level_number = None

# Thêm biến lưu âm lượng hiệu ứng riêng
music_volume = 0.5
sfx_volume = 0.5
music_muted = False
sfx_muted = False

# Thêm biến toàn cục cho vùng bánh răng
GEAR_RECT = pygame.Rect(WIDTH-54, 10, 44, 44)
GEAR_IMG = pygame.image.load("game project/assets/gear.png").convert_alpha()
GEAR_IMG = pygame.transform.smoothscale(GEAR_IMG, (44, 44))

# Thêm biến toàn cục
boss_group = pygame.sprite.Group()
boss_spawned = False

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
    screen.fill((255, 255, 255))  # Nền trắng

    # Font lớn cho tiêu đề
    gameover_font = pygame.font.SysFont("Segoe UI", 60)
    over_text = gameover_font.render("GAME OVER", True, (255, 0, 0))  # Đỏ đậm

    # Font bình thường cho nội dung
    info_font = pygame.font.SysFont("Segoe UI", 32)

    # Text điểm số
    score_text = info_font.render(f"Điểm: {score}", True, (255, 165, 0))  # Vàng cam
    level_text = info_font.render(f"Level đạt được: {level}", True, (0, 100, 255))  # Xanh dương đậm

    # Text hướng dẫn
    retry_text = info_font.render("SPACE để chơi lại", True, (0, 180, 0))  # Xanh lá đậm
    exit_text = info_font.render("ESC để thoát", True, (0, 0, 0))  # Đen

    # Tính toán vị trí hiển thị giữa màn hình
    spacing = 50
    center_x = WIDTH // 2
    y_start = HEIGHT // 5

    screen.blit(over_text, (center_x - over_text.get_width() // 2, y_start))
    screen.blit(score_text, (center_x - score_text.get_width() // 2, y_start + spacing * 1.5))
    screen.blit(level_text, (center_x - level_text.get_width() // 2, y_start + spacing * 2.5))
    screen.blit(retry_text, (center_x - retry_text.get_width() // 2, y_start + spacing * 5))
    screen.blit(exit_text, (center_x - exit_text.get_width() // 2, y_start + spacing * 6))




def draw_slider(surface, x, y, w, h, value, label, selected, mouse_on):
    # Màu nền box
    color_bg = (60, 60, 90) if not selected else (80, 120, 180)
    color_bg = (120, 180, 255) if mouse_on else color_bg
    pygame.draw.rect(surface, color_bg, (x, y, w, h), border_radius=16)
    slider_w = int(w * 0.7)
    slider_x = x + (w - slider_w)//2
    slider_y = y + 32
    slider_h = 14
    # Vẽ label căn giữa
    text = font.render(f"{label}", True, (255,255,255))
    text_x = slider_x + slider_w//2 - text.get_width()//2
    text_y = y + 8
    surface.blit(text, (text_x, text_y))

    # Vẽ icon loa nhỏ đầu thanh
    icon_center = (slider_x-24, slider_y+slider_h//2)
    pygame.draw.circle(surface, (200,200,200), icon_center, 10)
    pygame.draw.polygon(surface, (80,80,80), [ (slider_x-30,slider_y+slider_h//2-6), (slider_x-18,slider_y+slider_h//2), (slider_x-30,slider_y+slider_h//2+6) ])
    # Vẽ gradient cho thanh slider
    for i in range(slider_w):
        c = 180 + int(40*i/slider_w)
        pygame.draw.line(surface, (c,c,c), (slider_x+i, slider_y), (slider_x+i, slider_y+slider_h), 1)
    pygame.draw.rect(surface, (180,180,180), (slider_x, slider_y, slider_w, slider_h), 2, border_radius=7)
    # Nút kéo hình tròn
    knob_radius = 18 if (selected or mouse_on) else 14
    knob_x = slider_x + int(value * (slider_w-2*knob_radius)) + knob_radius
    knob_y = slider_y + slider_h//2
    pygame.draw.circle(surface, (255, 200, 0), (knob_x, knob_y), knob_radius)
    pygame.draw.circle(surface, (180, 140, 0), (knob_x, knob_y), knob_radius, 3)
    # Hiển thị giá trị phần trăm trên nút kéo
    percent_text = font.render(f"{int(value*100)}%", True, (60,60,60))
    surface.blit(percent_text, (knob_x-percent_text.get_width()//2, knob_y-percent_text.get_height()//2))

def draw_button(surface, x, y, w, h, label, selected, mouse_on):
    color_bg = (60, 60, 90) if not selected else (80, 120, 180)
    color_bg = (120, 180, 255) if mouse_on else color_bg
    pygame.draw.rect(surface, color_bg, (x, y, w, h), border_radius=10)
    text = font.render(label, True, (255,255,255))
    surface.blit(text, (x + w//2 - text.get_width()//2, y + h//2 - text.get_height()//2))

def show_setting(selected_idx=0, mouse_pos=None):
    screen.fill((30, 30, 50))
    title = big_font.render("CÀI ĐẶT", True, (255, 255, 0))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 5))
    # Layout
    box_w, box_h = 320, 56
    start_y = HEIGHT//3
    gap = 24
    slider_items = []
    button_items = []
    # Slider nhạc nền
    slider_items.append({'type':'slider', 'label':'Âm lượng nhạc nền', 'value':music_volume, 'rect':pygame.Rect(WIDTH//2-box_w//2, start_y, box_w, box_h)})
    # Slider hiệu ứng
    slider_items.append({'type':'slider', 'label':'Âm lượng hiệu ứng', 'value':sfx_volume, 'rect':pygame.Rect(WIDTH//2-box_w//2, start_y+box_h+gap, box_w, box_h)})
    # Button chơi lại
    button_items.append({'type':'button', 'label':'Chơi lại', 'rect':pygame.Rect(WIDTH//2-box_w//2, start_y+2*(box_h+gap), box_w, box_h)})
    # Button về menu
    button_items.append({'type':'button', 'label':'Về màn hình chính', 'rect':pygame.Rect(WIDTH//2-box_w//2, start_y+3*(box_h+gap), box_w, box_h)})
    # Vẽ slider
    for i, item in enumerate(slider_items):
        mouse_on = mouse_pos and item['rect'].collidepoint(mouse_pos)
        draw_slider(screen, item['rect'].x, item['rect'].y, item['rect'].w, item['rect'].h, item['value'], item['label'], selected_idx==i, mouse_on)
    # Vẽ button
    for j, item in enumerate(button_items):
        mouse_on = mouse_pos and item['rect'].collidepoint(mouse_pos)
        draw_button(screen, item['rect'].x, item['rect'].y, item['rect'].w, item['rect'].h, item['label'], selected_idx==j+len(slider_items), mouse_on)
    # Trả về danh sách item đã hợp nhất để xử lý sự kiện
    return slider_items + button_items

# Vòng lặp chính
running = True
selected_setting_idx = 0
slider_drag = None  # (index, offset_x)
while running:
    # Nếu đang ở level có boss (10, 20, 30) và boss còn sống, không tăng level
    boss_levels = [10, 20, 30]
    if loaded_level_number in boss_levels and len(boss_group) > 0:
        level = loaded_level_number
    else:
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

    mouse_pos = pygame.mouse.get_pos() if game_state == STATE_SETTING else None
    if game_state == STATE_SETTING:
        setting_items = show_setting(selected_setting_idx, mouse_pos)
    elif game_state == STATE_MENU:
        show_menu()
    elif game_state == STATE_GAMEOVER:
        show_gameover()
    elif game_state == STATE_PLAYING:
        flash_health = health_flash_timer > 0
        # Hiệu ứng rung màn hình
        shake_offset = [0, 0]
        if flash_health:
            import random
            shake_offset[0] = random.randint(-8, 8)
            shake_offset[1] = random.randint(-8, 8)
        # Vẽ background với offset
        if loaded_background:
            screen.blit(loaded_background, (shake_offset[0], shake_offset[1]))
        else:
            screen.fill(level_data.background_color)
        # Vẽ các đối tượng với offset
        player_rect_offset = player.rect.move(shake_offset)
        draw_hud(screen, score, player_health, max_health, level, font, player_rect=player_rect_offset, flash_health=flash_health)
        screen.blit(player.image, player_rect_offset)
        for sprite in bullets:
            screen.blit(sprite.image, sprite.rect.move(shake_offset))
        for sprite in enemies:
            screen.blit(sprite.image, sprite.rect.move(shake_offset))
        for sprite in explosions:
            screen.blit(sprite.image, sprite.rect.move(shake_offset))

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

        frame_count += 1
        # Sinh boss ở các level đặc biệt
        if level in boss_levels:
            if len(boss_group) == 0:
                if level == 10:
                    boss = Boss()
                elif level == 20:
                    boss = Boss(image_path="game project/assets/boss2.png", health=400, speed_x=3, speed_y=2, shot_cooldown=900, shoot_type="triple")
                elif level == 30:
                    boss = Boss(image_path="game project/assets/boss3.png", health=700, speed_x=4, speed_y=2, shot_cooldown=600, shoot_type="circle")
                boss_group.add(boss)
            boss_group.update()
            for b in boss_group:
                b.draw(screen)
                # Vẽ và cập nhật đạn boss
                b.bullets.update()
                b.bullets.draw(screen)
                # Va chạm đạn boss với player
                if pygame.sprite.spritecollideany(player, b.bullets):
                    player_health -= 1
                    health_flash_timer = HEALTH_FLASH_DURATION
                    for bullet in b.bullets:
                        if player.rect.colliderect(bullet.rect):
                            bullet.kill()
                    if player_health <= 0:
                        game_state = STATE_GAMEOVER
                # Boss triệu hồi enemy nhỏ
                if hasattr(b, 'spawn_enemy') and b.spawn_enemy and b.health > 0:
                    if len(enemies) < level_data.max_enemies:
                        enemies.add(Enemy(level_data.enemy_speed))
                    b.spawn_enemy = False
                # Xử lý va chạm boss với đạn (chỉ với đạn còn sống, chỉ xử lý 1 lần duy nhất)
                boss_hits = pygame.sprite.spritecollide(b, bullets, False)
                for bullet in boss_hits:
                    b.take_damage(bullet.damage)
                    bullet.kill()
                if b.health <= 0:
                    boss_group.remove(b)
        # Chỉ sinh enemy nhỏ khi không có boss
        if (level not in boss_levels or len(boss_group) == 0) and frame_count >= level_data.enemy_spawn_rate:
            if len(enemies) < level_data.max_enemies:
                enemies.add(Enemy(level_data.enemy_speed))
            frame_count = 0
        # Xử lý va chạm enemy với đạn (ưu tiên enemy trước)
        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        bullets_alive = [b for b in bullets]
        for hit in hits:
            score += 10
            explosions.add(Explosion(hit.rect.center, explosion_images))
            explode_sound.play()
        # Xử lý va chạm boss với đạn (chỉ với đạn còn sống)
        # (Đã xử lý ở trên, nên xóa đoạn này để tránh trừ máu 2 lần)
        if level == 2:
              for b in boss_group:
                  boss_hits = pygame.sprite.spritecollide(b, bullets, False)
                  for bullet in boss_hits:
                      if bullet in bullets_alive:
                          b.take_damage(10)
                          bullet.kill()
                  if b.health <= 0:
                     boss_group.remove(b)

        if pygame.sprite.spritecollideany(player, enemies):
            player_health -= 1
            health_flash_timer = HEALTH_FLASH_DURATION
            pygame.sprite.spritecollide(player, enemies, True)
            if player_health <= 0:
                game_state = STATE_GAMEOVER

        # Vẽ icon bánh răng góc trên phải bằng ảnh
        mouse_on_gear = GEAR_RECT.collidepoint(pygame.mouse.get_pos())
        gear_img = GEAR_IMG.copy()
        if mouse_on_gear:
            # Làm sáng ảnh khi hover
            arr = pygame.surfarray.pixels_alpha(gear_img)
            arr[:] = arr * 0.7 + 255 * 0.3
            del arr
        screen.blit(gear_img, GEAR_RECT.topleft)

    # Update health flash timer
    if health_flash_timer > 0:
        health_flash_timer -= 1

    if game_state == STATE_SETTING:
        setting_items = show_setting(selected_setting_idx, mouse_pos)
    else:
        setting_items = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Debug trạng thái game khi nhấn phím
        if event.type == pygame.KEYDOWN:
            print('DEBUG: game_state =', game_state, ', key =', event.key)

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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    selected_setting_idx = 0
                    slider_drag = None
                    game_state = STATE_SETTING
            keys = pygame.key.get_pressed()
            current_time = pygame.time.get_ticks()
            if keys[pygame.K_SPACE] and (current_time - last_shot_time >= level_data.shoot_cooldown):
                bullets.add(player.shoot())
                shoot_sound.play()
                last_shot_time = current_time
            # Thêm xử lý bấm chuột vào bánh răng
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if GEAR_RECT.collidepoint(event.pos):
                    selected_setting_idx = 0
                    slider_drag = None
                    game_state = STATE_SETTING

        if game_state == STATE_SETTING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    slider_drag = None
                    game_state = STATE_PLAYING
                elif event.key == pygame.K_UP:
                    selected_setting_idx = (selected_setting_idx - 1) % 4
                elif event.key == pygame.K_DOWN:
                    selected_setting_idx = (selected_setting_idx + 1) % 4
                elif selected_setting_idx == 0 and (event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT):
                    # Chỉnh âm lượng nhạc nền
                    delta = 0.05 if event.key == pygame.K_RIGHT else -0.05
                    music_volume = min(max(music_volume + delta, 0), 1)
                    pygame.mixer.music.set_volume(music_volume)
                elif selected_setting_idx == 1 and (event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT):
                    # Chỉnh âm lượng hiệu ứng
                    delta = 0.05 if event.key == pygame.K_RIGHT else -0.05
                    sfx_volume = min(max(sfx_volume + delta, 0), 1)
                    explode_sound.set_volume(sfx_volume)
                    shoot_sound.set_volume(sfx_volume)
                elif selected_setting_idx == 2 and event.key == pygame.K_RETURN:
                    # Chơi lại
                    reset_game()
                    game_state = STATE_PLAYING
                elif selected_setting_idx == 3 and event.key == pygame.K_RETURN:
                    # Về màn hình chính
                    reset_game()
                    game_state = STATE_MENU
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, item in enumerate(setting_items):
                    if item['rect'].collidepoint(event.pos):
                        selected_setting_idx = i
                        if item['type'] == 'slider':
                            slider_drag = (i, event.pos[0] - item['rect'].x)
                        elif i == 2:
                            reset_game()
                            game_state = STATE_PLAYING
                        elif i == 3:
                            reset_game()
                            game_state = STATE_MENU
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                slider_drag = None
            elif event.type == pygame.MOUSEMOTION and slider_drag:
                idx, offset_x = slider_drag
                item = setting_items[idx]
                rel_x = event.pos[0] - item['rect'].x
                slider_w = int(item['rect'].w * 0.7)
                slider_x = item['rect'].x + (item['rect'].w - slider_w)//2
                rel_slider = min(max(event.pos[0] - slider_x, 0), slider_w-20)
                value = rel_slider / (slider_w-20)
                if idx == 0:
                    music_volume = value
                    pygame.mixer.music.set_volume(music_volume)
                elif idx == 1:
                    sfx_volume = value
                    explode_sound.set_volume(sfx_volume)
                    shoot_sound.set_volume(sfx_volume)

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
sys.exit()
 
