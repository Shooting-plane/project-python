import pygame

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # Dùng ảnh
        #     self.image = pygame.image.load("assets/bullet.png").convert_alpha()
        #     self.image = pygame.transform.scale(self.image, (5, 10))  # resize nếu cần
        
        # dùng tạm khối vàng 
        self.image = pygame.Surface((5, 10))
        self.image.fill((255, 255, 0))  

        # Tạo vị trí ban đầu
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -10  # Bay lên (trục Y giảm)

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()
