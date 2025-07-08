import pygame

class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets/boss.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (120, 120))
        self.rect = self.image.get_rect(center=(206, 100))
        self.health = 100
        self.speed = 2

    def update(self):
        self.rect.x += self.speed
        if self.rect.left < 0 or self.rect.right > 412:
            self.speed = -self.speed 