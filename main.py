import pygame

# Thêm ở đầu file (sau các biến toàn cục)
GEAR_IMG = pygame.image.load("assets/gear.png").convert_alpha()
GEAR_IMG = pygame.transform.smoothscale(GEAR_IMG, (44, 44))

# ...
    elif game_state == STATE_PLAYING:
        # ...
        # Vẽ icon bánh răng góc trên phải bằng ảnh
        mouse_on_gear = GEAR_RECT.collidepoint(pygame.mouse.get_pos())
        gear_img = GEAR_IMG.copy()
        if mouse_on_gear:
            # Làm sáng ảnh khi hover
            arr = pygame.surfarray.pixels_alpha(gear_img)
            arr[:] = arr * 0.7 + 255 * 0.3
            del arr
        screen.blit(gear_img, GEAR_RECT.topleft) 