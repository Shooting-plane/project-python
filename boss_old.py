import pygame
import random
from enemy import Enemy

class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets/boss.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (120, 120))
        self.rect = self.image.get_rect(center=(206, 100))
        self.health = 100
        self.max_health = 100
        self.speed_x = 2
        self.speed_y = 1
        self.direction_y = 1
        self.phase = 1
        self.last_shot_time = 0
        self.shot_cooldown = 1200  # ms
        self.last_spawn_time = 0
        self.spawn_cooldown = 3000  # ms
        self.hit_timer = 0
        self.hit_flash_duration = 150  # ms
        self.bullets = pygame.sprite.Group()
        self.spawn_enemy = False

    def update(self):
        # Di chuyển X
        self.rect.x += self.speed_x
        if self.rect.left < 0 or self.rect.right > 412:
            self.speed_x = -self.speed_x
        # Di chuyển Y
        self.rect.y += self.speed_y * self.direction_y
        if self.rect.top < 0 or self.rect.bottom > 200:
            self.direction_y *= -1
        # Phase
        if self.health <= 60 and self.phase == 1:
            self.phase = 2
            self.speed_x = 3
            self.shot_cooldown = 800
            self.spawn_cooldown = 2000
        if self.health <= 30 and self.phase == 2:
            self.phase = 3
            self.speed_x = 4
            self.shot_cooldown = 500
            self.spawn_cooldown = 1200
        # Bắn đạn
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > self.shot_cooldown:
            self.shoot()
            self.last_shot_time = now
        # Triệu hồi enemy nhỏ
        if now - self.last_spawn_time > self.spawn_cooldown:
            self.spawn_enemy = True
            self.last_spawn_time = now
        # Hiệu ứng bị bắn
        if self.hit_timer > 0:
            self.hit_timer -= pygame.time.get_ticks() - self.last_hit_tick
            self.last_hit_tick = pygame.time.get_ticks()
            if self.hit_timer <= 0:
                self.image = pygame.image.load("assets/boss.png").convert_alpha()
                self.image = pygame.transform.scale(self.image, (120, 120))
        self.bullets.update()

    def shoot(self):
        bullet = BossBullet(self.rect.centerx, self.rect.bottom)
        self.bullets.add(bullet)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        self.bullets.draw(surface)
        self.draw_health_bar(surface)

    def draw_health_bar(self, surface):
        bar_width = 120
        bar_height = 12
        x = self.rect.centerx - bar_width // 2
        y = self.rect.top - bar_height - 8
        # Viền
        pygame.draw.rect(surface, (0,0,0), (x-2, y-2, bar_width+4, bar_height+4), border_radius=6)
        # Nền
        pygame.draw.rect(surface, (120, 0, 0), (x, y, bar_width, bar_height), border_radius=5)
        # Máu còn lại
        health_ratio = max(self.health, 0) / self.max_health
        pygame.draw.rect(surface, (0, 220, 0), (x, y, int(bar_width * health_ratio), bar_height), border_radius=5)

    def take_damage(self, amount):
        self.health -= amount
        # Hiệu ứng flash đỏ khi bị bắn
        self.image.fill((255, 0, 0, 100), special_flags=pygame.BLEND_RGBA_ADD)
        self.hit_timer = self.hit_flash_duration
        self.last_hit_tick = pygame.time.get_ticks()

class BossBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (255, 100, 0), [0, 0, 10, 20])
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 6
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > 915:
            self.kill() 