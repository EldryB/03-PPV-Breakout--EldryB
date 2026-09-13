"""
ISPPV1 2023
Study Case: Breakout

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class to define the Play state.
"""

import random

import pygame

from gale.factory import AbstractFactory
from gale.state import BaseState
from gale.input_handler import InputData
from gale.text import render_text

import settings
import src.powerups

from src.Projectile import Projectile
from src.Paddle import Paddle


class PlayState(BaseState):
    def enter(self, **params: dict):
        self.level = params["level"]
        self.score = params["score"]
        self.lives = params["lives"]
        self.paddle = params["paddle"]
        self.balls = params["balls"]
        self.brickset = params["brickset"]
        self.live_factor = params["live_factor"]
        self.points_to_next_live = params["points_to_next_live"]
        self.points_to_next_grow_up = (
            self.score
            + settings.PADDLE_GROW_UP_POINTS * (self.paddle.size + 1) * self.level
        )
        self.powerups = params.get("powerups", [])

        if not params.get("resume", False):
            self.balls[0].vx = random.randint(-80, 80)
            self.balls[0].vy = random.randint(-170, -100)
            settings.SOUNDS["paddle_hit"].play()

        self.powerups_abstract_factory = AbstractFactory("src.powerups")

        self.is_catching = False
        self.catch_timer:float = 0.0

        self.is_shooting = False
        self.shoot_timer:float = 0.0
        self.projectiles = []

        self.paddle2_is_active = False
        self.paddle2_timer:float = 0.0
        self.paddle2 = Paddle(
             self.paddle.x, self.paddle.y
        )


    def update(self, dt: float) -> None:
        self.paddle.update(dt)
        if self.paddle2_is_active:
            self.paddle2.update(dt)

        if self.paddle2_is_active:
            self.paddle2_timer -= dt
            if self.paddle2_timer <= 0:
                self.paddle2_is_active = False
                self.paddle2.vx = 0

        for proj in self.projectiles:
            proj.update(dt)

            brick = self.brickset.get_colliding_brick(proj.get_collision_rect())
            if brick is not None:
                brick.hit()
                self.score += brick.score()
                proj.active = False
                
        for ball in self.balls:

            if ball.is_caught:
                ball.x = ball.catching_paddle.x + ball.catch_offset
                ball.y = ball.catching_paddle.y - ball.height - 1
                continue 

            ball.update(dt)
            ball.solve_world_boundaries()

            # Check collision with the paddle
            if ball.collides(self.paddle):
                if self.paddle.is_catching: 
                    ball.is_caught = True
                    ball.catch_offset = ball.x - self.paddle.x
                    ball.vy = 0
                    ball.vx = 0
                    ball.catching_paddle = self.paddle 
                else:
                    ball.rebound(self.paddle)
                    ball.push(self.paddle)

            # Check collision with paddle 2
            if self.paddle2_is_active and ball.collides(self.paddle2):
                if self.paddle2.is_catching: 
                    ball.is_caught = True
                    ball.catch_offset = ball.x - self.paddle2.x
                    ball.vy = 0
                    ball.vx = 0
                    ball.catching_paddle = self.paddle2 
                else:
                    ball.rebound(self.paddle2)
                    ball.push(self.paddle2)

            if not ball.collides(self.brickset):
                continue

            brick = self.brickset.get_colliding_brick(ball.get_collision_rect())

            if brick is None:
                continue
            
            brick.hit()
            self.score += brick.score()
            ball.rebound(brick)

            # Check earn life
            if self.score >= self.points_to_next_live:
                settings.SOUNDS["life"].play()
                self.lives = min(3, self.lives + 1)
                self.live_factor += 0.5
                self.points_to_next_live += settings.LIVE_POINTS_BASE * self.live_factor

            # Check growing up of the paddle
            if self.score >= self.points_to_next_grow_up:
                settings.SOUNDS["grow_up"].play()
                self.points_to_next_grow_up += (
                    settings.PADDLE_GROW_UP_POINTS * (self.paddle.size + 1) * self.level
                )
                self.paddle.inc_size()

            if random.random() < 0.4:
                r = brick.get_collision_rect()
                powerType = random.choice(["TwoMoreBall", "CatchBall", "CanonBall", "TwoPaddle"])
                self.powerups.append(
                    self.powerups_abstract_factory.get_factory(powerType).create(
                        r.centerx - 8, r.centery - 8
                    )
                )

        # Removing all balls that are not in play
        self.balls = [ball for ball in self.balls if ball.active]
        self.projectiles = [proj for proj in self.projectiles if proj.active]

        self.brickset.update(dt)

        if not self.balls:
            self.lives -= 1
            if self.lives == 0:
                self.state_machine.change("game_over", score=self.score)
            else:
                self.paddle.dec_size()
                self.state_machine.change(
                    "serve",
                    level=self.level,
                    score=self.score,
                    lives=self.lives,
                    paddle=self.paddle,
                    brickset=self.brickset,
                    points_to_next_live=self.points_to_next_live,
                    live_factor=self.live_factor,
                )

        # Update powerups
        for powerup in self.powerups:
            powerup.update(dt)

            if powerup.collides(self.paddle):
                powerup.take(self, self.paddle)

            elif self.paddle2_is_active and powerup.collides(self.paddle2):
                powerup.take(self, self.paddle2)

        # Remove powerups that are not in play
        self.powerups = [p for p in self.powerups if p.active]

        # Check victory all bricks have been destroyed
        if self.brickset.size == 0:
            self.paddle.has_canon = False
            self.state_machine.change(
                "victory",
                lives=self.lives,
                level=self.level,
                score=self.score,
                paddle=self.paddle,
                balls=self.balls,
                points_to_next_live=self.points_to_next_live,
                live_factor=self.live_factor,
            )

    def render(self, surface: pygame.Surface) -> None:
        heart_x = settings.VIRTUAL_WIDTH - 120

        i = 0
        # Draw filled hearts
        while i < self.lives:
            surface.blit(
                settings.TEXTURES["hearts"], (heart_x, 5), settings.FRAMES["hearts"][0]
            )
            heart_x += 11
            i += 1

        # Draw empty hearts
        while i < 3:
            surface.blit(
                settings.TEXTURES["hearts"], (heart_x, 5), settings.FRAMES["hearts"][1]
            )
            heart_x += 11
            i += 1

        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["tiny"],
            settings.VIRTUAL_WIDTH - 80,
            5,
            (255, 255, 255),
        )

        self.brickset.render(surface)

        self.paddle.render(surface)

        if self.paddle2_is_active:
            self.paddle2.render(surface)

        for ball in self.balls:
            ball.render(surface)

        for powerup in self.powerups:
            powerup.render(surface)

        for proj in self.projectiles:
            proj.render(surface)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "move_left":
            if input_data.pressed:
                self.paddle.vx = -settings.PADDLE_SPEED
            elif input_data.released and self.paddle.vx < 0:
                self.paddle.vx = 0
        elif input_id == "move_right":
            if input_data.pressed:
                self.paddle.vx = settings.PADDLE_SPEED
            elif input_data.released and self.paddle.vx > 0:
                self.paddle.vx = 0

        if input_id == "paddle2_left" and self.paddle2_is_active:
            if input_data.pressed:
                self.paddle2.vx = -settings.PADDLE_SPEED
            elif input_data.released and self.paddle2.vx < 0:
                self.paddle2.vx = 0
        elif input_id == "paddle2_right" and self.paddle2_is_active:
            if input_data.pressed:
                self.paddle2.vx = settings.PADDLE_SPEED
            elif input_data.released and self.paddle2.vx > 0:
                self.paddle2.vx = 0

        elif input_id == "pause" and input_data.pressed:
            self.state_machine.change(
                "pause",
                level=self.level,
                score=self.score,
                lives=self.lives,
                paddle=self.paddle,
                balls=self.balls,
                brickset=self.brickset,
                points_to_next_live=self.points_to_next_live,
                live_factor=self.live_factor,
                powerups=self.powerups,
            )

        elif input_id == "launch" and input_data.pressed:
            launched = False
            for ball in self.balls:
                if ball.is_caught:
                    launched = True
                    ball.is_caught = False
                    ball.vy = random.randint(-160, -90)

                    if ball.catching_paddle is not None:
                        vx = ball.catching_paddle.vx
                        # Guarantee a minimum vx to avoid perfectly vertical shots (adds a bit of difficulty)
                        if vx == 0:
                            vx = random.choice([-1, 1]) * random.randint(10, 15)
                        ball.vx = vx
                        ball.catching_paddle = None

            # If no ball is caught, SPACE also pauses the game
            if not launched:
                self.state_machine.change(
                    "pause",
                    level=self.level,
                    score=self.score,
                    lives=self.lives,
                    paddle=self.paddle,
                    balls=self.balls,
                    brickset=self.brickset,
                    points_to_next_live=self.points_to_next_live,
                    live_factor=self.live_factor,
                    powerups=self.powerups,
                )

        elif input_id == "shoot" and input_data.pressed:
            if len(self.projectiles) == 0:
                if self.paddle.has_canon:
                    self.projectiles.extend([
                        Projectile(self.paddle.lcanonx, self.paddle.lcanony),
                        Projectile(self.paddle.rcanonx, self.paddle.rcanony)
                    ])

                if self.paddle2_is_active and self.paddle2.has_canon:
                    self.projectiles.extend([
                        Projectile(self.paddle2.lcanonx, self.paddle2.lcanony),
                        Projectile(self.paddle2.rcanonx, self.paddle2.rcanony)
                    ])


