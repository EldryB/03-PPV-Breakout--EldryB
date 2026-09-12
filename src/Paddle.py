"""
ISPPV1 2023
Study Case: Breakout

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Paddle.
"""

import pygame

import settings


class Paddle:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.width = 64
        self.height = 16

        # By default, the blue paddle
        self.skin = 0

        # By default, the 64-pixels-width paddle.
        self.size = 1

        self.texture = settings.TEXTURES["spritesheet"]
        self.frames = settings.FRAMES["paddles"]

        # The paddle only move horizontally
        self.vx = 0

        self.has_canon = False
        self.shoot_timer = 0.0
        self.lcanonx = self.x
        self.rcanonx = self.x + self.width - settings.CANON_WIDTH
        self.rcanony = self.lcanony =  self.y 

        self.is_catching = False
        self.catch_timer = 0.0

        

    def resize(self, size: int) -> None:
        self.size = size
        self.width = (self.size + 1) * 32
        self.rcanonx = self.x + self.width - settings.CANON_WIDTH

    def dec_size(self):
        self.resize(max(0, self.size - 1))

    def inc_size(self):
        self.resize(min(3, self.size + 1))

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, dt: float) -> None:
        next_x = self.x + self.vx * dt

        if self.vx < 0:
            self.x = max(0, next_x)
        else:
            self.x = min(settings.VIRTUAL_WIDTH - self.width, next_x)

        self.lcanonx = self.x
        self.rcanonx = self.x + self.width - settings.CANON_WIDTH
        self.rcanony = self.lcanony =  self.y

        if self.is_catching:
            self.catch_timer -= dt
            if self.catch_timer <= 0:
                self.is_catching = False

        if self.has_canon:
            self.shoot_timer -= dt
            if self.shoot_timer <= 0:
                self.has_canon = False

    def get_canon_left_rect(self) -> pygame.Rect: # Cambia None por pygame.Rect
        return pygame.Rect(round(self.lcanonx), round(self.lcanony), settings.CANON_WIDTH, settings.CANON_HEIGHT)

    def get_canon_right_rect(self) -> pygame.Rect: # Cambia None por pygame.Rect
        return pygame.Rect(round(self.rcanonx), round(self.rcanony), settings.CANON_WIDTH, settings.CANON_HEIGHT)

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self.texture, (self.x, self.y), self.frames[self.skin][self.size])

        if self.has_canon:
            surface.blit(settings.TEXTURES["canon"], self.get_canon_left_rect())
            surface.blit(settings.TEXTURES["canon_inv"], self.get_canon_right_rect())

        
