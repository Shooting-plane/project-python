import pygame
import random

class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
            # Load ảnh nếu có
        #self.image = pygame.image.load("assets/enemy.png").convert_alpha()
        #self.image = pygame.transform.scale(self.image, (40, 40))
            # Nếu không có ảnh, tạo hình chữ nhật màu đỏ
        self.image = pygame.Surface((40, 40))
        self.image.fill((255, 0, 0))

        self.rect = self.image.get_rect(center=(random.randint(20, 392), -40))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > 915:  # nếu vượt qua màn hình thì xóa enemy
            self.kill()
