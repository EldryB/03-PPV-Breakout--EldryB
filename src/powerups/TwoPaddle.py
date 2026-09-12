from typing import TypeVar, Optional

import settings
from src.Paddle import Paddle
from src.powerups.PowerUp import PowerUp


class TwoPaddle(PowerUp):
    
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, 1)

    def take(self, play_state: TypeVar("PlayState"), paddle: Optional[Paddle] = None) -> None:
        play_state.paddle2.x = play_state.paddle.x
        play_state.paddle2.y = play_state.paddle.y
        play_state.paddle2_is_active = True
        play_state.paddle2_timer = 10.0 # El efecto durará 10 segundos
        self.active = False
