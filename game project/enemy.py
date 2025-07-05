import pygame
import random
from main import HEIGHT
class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()

        self.image = pygame.image.load("assets/enemy.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect(center=(random.randint(20, 392), -40))
        self.speed = speed

        self.missed = False  

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT :
            self.missed = True   
            self.kill()
