from dataclasses import dataclass

from .kinect_v1 import TILT_MAX, TILT_MIN

TILT_STEP = 5
TILT_SETTLE_S = 1.5
TILT_INTERVAL_S = 2.5
TILT_REST_S = 20
TILT_MOVES_BEFORE_REST = 12


@dataclass
class Tilt:
    """State accessed under the depth worker's lock."""

    angle: int | None = None
    target: int | None = None
    settled_at: float = 0.0
    next_move: float = 0.0
    moves: int = 0
    warning: str = ""

    def busy(self, now: float) -> bool:
        return self.target is not None or now < self.settled_at

    def request(self, direction: int, now: float) -> str:
        if self.angle is None:
            return "Kameravinkeln är inte tillgänglig."
        if self.busy(now) or now < self.next_move:
            return "Vänta innan du ändrar vinkeln igen."
        step = TILT_STEP if direction > 0 else -TILT_STEP
        target = min(TILT_MAX, max(TILT_MIN, self.angle + step))
        if target == self.angle:
            return "Kameran är vid sitt ändläge."
        self.target = target
        self.warning = ""
        return ""

    def finish(self, now: float, *, success: bool) -> None:
        if success:
            self.angle = self.target
        else:
            self.warning = "Kinect kunde inte ändra vinkeln."
        self.target = None
        self.settled_at = now + TILT_SETTLE_S
        self.moves += 1
        if self.moves >= TILT_MOVES_BEFORE_REST:
            self.next_move = now + TILT_REST_S
            self.moves = 0
        else:
            self.next_move = now + TILT_INTERVAL_S
