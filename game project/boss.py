import pygame
import random
from enemy import Enemy

class Boss(pygame.sprite.Sprite):
    def __init__(self, image_path="game project/assets/boss.png", health=200, speed_x=2, speed_y=1, shot_cooldown=1200, shoot_type="single"):
        super().__init__()
        self.image_path = image_path
        self.image = pygame.image.load(self.image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (120, 120))
        self.rect = self.image.get_rect(center=(206, 100))
        self.health = health
        self.max_health = health
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.direction_y = 1
        self.phase = 1
        self.last_shot_time = 0
        self.shot_cooldown = shot_cooldown  # ms
        self.last_spawn_time = 0
        self.spawn_cooldown = 3000  # ms
        self.hit_timer = 0
        self.hit_flash_duration = 150  # ms
        self.bullets = pygame.sprite.Group()
        self.shoot_type = shoot_type  # "single", "triple", "circle"
        self.shoot_angle = 0  # cho kiểu bắn tròn

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
        if self.health <= self.max_health * 0.3 and self.phase == 1:
            self.phase = 2
            self.speed_x += 1
            self.shot_cooldown = max(400, self.shot_cooldown - 400)
            self.spawn_cooldown = max(1000, self.spawn_cooldown - 1000)
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
                self.image = pygame.image.load(self.image_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (120, 120))
        self.bullets.update()

    def shoot(self):
        if self.shoot_type == "single":
            bullet = BossBullet(self.rect.centerx, self.rect.bottom)
            self.bullets.add(bullet)
        elif self.shoot_type == "triple":
            # Bắn 3 tia: thẳng, lệch trái, lệch phải
            for angle in [-20, 0, 20]:
                bullet = BossBullet(self.rect.centerx, self.rect.bottom, angle)
                self.bullets.add(bullet)
        elif self.shoot_type == "circle":
            # Bắn hình tròn: 12 viên, mỗi viên lệch nhau 30 độ
            for i in range(12):
                angle = self.shoot_angle + i * 30
                bullet = BossBullet(self.rect.centerx, self.rect.centery, angle, speed=6)
                self.bullets.add(bullet)
            self.shoot_angle = (self.shoot_angle + 10) % 360

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
    def __init__(self, x, y, angle=0, speed=6):
        super().__init__()
        self.image = pygame.Surface((10, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (255, 100, 0), [0, 0, 10, 20])
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.angle = angle
        import math
        self.vx = self.speed * math.sin(math.radians(self.angle))
        self.vy = self.speed * math.cos(math.radians(self.angle))
    def update(self):
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)
        if self.rect.top > 915 or self.rect.left < 0 or self.rect.right > 412 or self.rect.bottom < 0:
            self.kill() 