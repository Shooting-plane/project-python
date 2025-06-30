import pygame

def draw_hud(screen, score, health, level, font):
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    health_text = font.render(f"Health: {health}", True, (255, 0, 0))
    level_text = font.render(f"Level: {level}", True, (0, 255, 0))

    screen.blit(score_text, (10, 10))
    screen.blit(health_text, (10, 40))
    screen.blit(level_text, (10, 70))