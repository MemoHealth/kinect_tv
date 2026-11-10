from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True)
class Viewport:
    x: int
    y: int
    width: int
    height: int

    @classmethod
    def fit(cls, content: tuple[int, int], bounds: tuple[int, int]) -> Self:
        scale = min(bounds[0] / content[0], bounds[1] / content[1])
        width = max(1, round(content[0] * scale))
        height = max(1, round(content[1] * scale))
        return cls((bounds[0] - width) // 2, (bounds[1] - height) // 2, width, height)

    def normalized_point(
        self, point: tuple[float, float]
    ) -> tuple[float, float] | None:
        u = (point[0] - self.x) / self.width
        v = (point[1] - self.y) / self.height
        if 0 <= u < 1 and 0 <= v < 1:
            return u, v
        return None

    def point_at(self, uv: tuple[float, float]) -> tuple[float, float]:
        return self.x + uv[0] * self.width, self.y + uv[1] * self.height
