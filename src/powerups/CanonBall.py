from typing import TypeVar, Optional

import settings
from src.Paddle import Paddle
from src.powerups.PowerUp import PowerUp


class CanonBall(PowerUp):

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 6)

    def take(self, play_state: TypeVar("PlayState"), paddle: Optional[Paddle] = None) -> None:
        if paddle is not None:
            paddle.has_canon = True
            paddle.shoot_timer = 10.0
        self.active = False
