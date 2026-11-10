from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

BOWL_LEFT = 501
BOWL_RIGHT = 779
BOWL_RIM = 599
BOWL_BOTTOM = 690
BOWL_CAPACITY = 420


@dataclass
class Bowl:
    amount: int = 0

    @property
    def level(self) -> float:
        return self.amount / BOWL_CAPACITY

    def catch(
        self,
        x: NDArray[np.float64],
        y: NDArray[np.float64],
        next_x: NDArray[np.float64],
        next_y: NDArray[np.float64],
        guided: NDArray[np.bool_],
    ) -> NDArray[np.bool_]:
        crossing = (y < BOWL_RIM) & (next_y >= BOWL_RIM) & guided
        indices = np.flatnonzero(crossing)
        portion = (BOWL_RIM - y[indices]) / (next_y[indices] - y[indices])
        rim_x = x[indices] + portion * (next_x[indices] - x[indices])
        crossing[indices] = (rim_x >= BOWL_LEFT) & (rim_x <= BOWL_RIGHT)
        self.amount = min(BOWL_CAPACITY, self.amount + np.count_nonzero(crossing))
        return crossing
