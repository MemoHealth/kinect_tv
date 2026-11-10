from dataclasses import dataclass

SCENE_SIZE = (1280, 720)
WINDOW_SIZE = (960, 540)
DEMO_FPS = 60


@dataclass(frozen=True)
class DemoConfig:
    particle_count: int = 760
    seed: int = 42

    def __post_init__(self) -> None:
        if type(self.particle_count) is not int or not 1 <= self.particle_count <= 3000:
            raise ValueError("particle_count must be an integer from 1 to 3000")
        if type(self.seed) is not int or self.seed < 0:
            raise ValueError("seed must be a nonnegative integer")
