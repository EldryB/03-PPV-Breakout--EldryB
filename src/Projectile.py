"""
ISPPV1 2023
Study Case: Breakout

This file contains the class Projectile for the CanonBall power-up.
"""

import pygame

import settings

class Projectile:
    def __init__(self, x: float, y: float) -> None:
        self.width = 4
        self.height = 12
        self.x = x + (settings.CANON_WIDTH // 2) - (self.width // 2)
        self.y = y
        self.vy = settings.PROJECTILE_SPEED 
        
        self.active = True

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, dt: float) -> None:
        self.y -= self.vy * dt

        if self.y < 0:
            self.active = False

    def render(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(
            surface,
            (255, 200, 50),  
            (self.x, self.y, self.width, self.height)
        )