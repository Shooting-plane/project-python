import pygame
from bullet import Bullet

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("game project/assets/player.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))  # resize nếu cần
        

        # Thiết lập vị trí bắt đầu
        self.rect = self.image.get_rect(center=(206, 850))  # Gần cuối màn hình
        self.speed = 5

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed

        # Giới hạn trong màn hình (cỡ Galaxy S20: 412x915)
        self.rect.x = max(0, min(self.rect.x, 412 - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, 915 - self.rect.height))

    def shoot(self):
        return Bullet(self.rect.centerx, self.rect.top, damage=10)
