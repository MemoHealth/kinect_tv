"""Gather, travel and bloom; fixed arrays, no score or identity inference."""

import numpy as np
from numpy.typing import NDArray


class CoralGarden:
    def __init__(self) -> None:
        self.corals = np.array(((320, 615), (640, 615), (960, 615)), dtype=float)
        self.energy = np.zeros(3)
        self.bloom = np.zeros(3)
        self.arrivals = np.zeros(3, dtype=int)
        self.destination = np.full(24, -1, dtype=int)
        self.launch = np.zeros((24, 2))
        self._trip_age = np.zeros(24)
        self.lures = np.zeros((3, 2))
        self.active = np.zeros(3, dtype=bool)
        self.gather = np.zeros(3)
        self._rest = np.zeros(3)

    def update(
        self, positions: NDArray, targets: NDArray, owners: NDArray, dt: float,
    ) -> None:
        dt = min(0.05, max(0, dt))
        self.energy *= np.exp(-dt / 80)
        self.bloom += (self.energy - self.bloom) * (1 - np.exp(-dt / 0.85))
        self._rest = np.maximum(0, self._rest - dt)
        self._trip_age[self.destination >= 0] += dt
        expired = self._trip_age > 14
        self.destination[expired] = -1
        self._trip_age[expired] = 0
        for school in range(3):
            ids = np.arange(school * 8, school * 8 + 8)
            candidates = targets[(owners & (1 << school)) != 0]
            if not candidates.size:
                candidates = targets
            if not candidates.size:
                self.active[school] = False
                self.gather[school] = 0
                continue
            centre = (self.lures[school] if self.active[school]
                      else positions[ids].mean(axis=0))
            chosen = candidates[np.linalg.norm(candidates - centre, axis=1).argmin()]
            if not self.active[school]:
                self.lures[school] = chosen
            else:
                self.lures[school] += (chosen - self.lures[school]) * (
                    1 - np.exp(-dt / 0.18)
                )
            self.active[school] = True
            distance = np.linalg.norm(positions[ids] - self.lures[school], axis=1)
            nearby = ids[(distance < 100) & (self.destination[ids] < 0)]
            coral = int(np.abs(self.corals[:, 0] - self.lures[school, 0]).argmin())
            in_flight = np.count_nonzero(self.destination == coral)
            ready = (len(nearby) >= 2 and self._rest[school] == 0
                     and self.energy[coral] < 0.75 and in_flight < 3)
            self.gather[school] = (
                self.gather[school] + dt if ready
                else max(0, self.gather[school] - dt * 2)
            )
            if self.gather[school] >= 0.7:
                order = np.argsort(np.linalg.norm(
                    positions[nearby] - self.lures[school], axis=1
                ))
                couriers = nearby[order[:min(3 - in_flight, 3)]]
                if len(couriers) >= 2:
                    self.destination[couriers] = coral
                    self.launch[couriers] = self.lures[school]
                    self._trip_age[couriers] = 0
                    self._rest[school] = 8
                    self.gather[school] = 0

    def arrive(self, positions: NDArray) -> None:
        ids = np.flatnonzero(self.destination >= 0)
        if not ids.size:
            return
        corals = self.destination[ids]
        arrived = (np.linalg.norm(positions[ids] - self.corals[corals], axis=1) < 32)
        arrived &= self._trip_age[ids] >= 0.6
        for fish in ids[arrived]:
            coral = self.destination[fish]
            self.energy[coral] = min(1, self.energy[coral] + 0.4)
            self.arrivals[coral] += 1
            self.destination[fish] = -1
            self._trip_age[fish] = 0
