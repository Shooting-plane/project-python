import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, image_path, x, y):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 5

    def handle_input(self, keys):
        if "LEFT" in keys:
            self.rect.x -= self.speed
        if "RIGHT" in keys:
            self.rect.x += self.speed
        if "UP" in keys:
            self.rect.y -= self.speed
        if "DOWN" in keys:
            self.rect.y += self.speed

        # Giới hạn trong màn hình (nếu cần)
        self.rect.x = max(0, min(self.rect.x, 800 - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, 600 - self.rect.height))

    def update(self):
        pass  # Có thể thêm xử lý nâng cao ở đây

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def shoot(self):
        from bullet import Bullet
        return Bullet(self.rect.centerx, self.rect.top)
