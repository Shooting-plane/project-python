import pygame

def draw_hud(screen, score, health, max_health, level, font, player_rect=None, flash_health=False):
    # Score và Level gần nhau
    score_text = font.render(f"Score: {score}", True, (0, 120, 255))
    level_text = font.render(f"Level: {level}", True, (0, 120, 255))
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 10 + score_text.get_height() + 2))

    # Health Bar dưới player
    if player_rect:
        bar_width, bar_height = 60, 10
        bar_x = player_rect.centerx - bar_width // 2
        bar_y = player_rect.bottom + 8
        health_ratio = max(0, min(health / max_health, 1))
        fill_width = int(bar_width * health_ratio)
        border_color = (0, 0, 0)
        fill_color = (255, 0, 0) if flash_health else (0, 200, 0)
        bg_color = (180, 180, 180)
        pygame.draw.rect(screen, bg_color, (bar_x, bar_y, bar_width, bar_height), border_radius=4)
        pygame.draw.rect(screen, fill_color, (bar_x, bar_y, fill_width, bar_height), border_radius=4)
        pygame.draw.rect(screen, border_color, (bar_x, bar_y, bar_width, bar_height), 1, border_radius=4)