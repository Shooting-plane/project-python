import pygame

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, damage=10):
        super().__init__()

        # Dùng ảnh
        self.image = pygame.image.load("game project/assets/bullet.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (20, 40))  # resize nếu cần
        

        # Tạo vị trí ban đầu
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -10  # Bay lên (trục Y giảm)
        self.damage = damage    
    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()
