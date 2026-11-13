import numpy as np
import pygame

from magic_rain.config import SCENE_SIZE
from magic_rain.coordinates import Viewport
from magic_rain.render.aquarium import LivingAquarium
from magic_rain.simulation.coral_garden import CoralGarden


def gathered():
    targets = np.array(((320, 300), (640, 300), (960, 300)), dtype=float)
    positions = np.repeat(targets, 8, axis=0)
    positions += np.tile(np.arange(8)[:, None], (3, 2))
    return positions, targets, np.array((1, 2, 4), dtype=np.uint8)


def test_gather_travel_and_actual_arrival_bloom_three_corals():
    garden = CoralGarden()
    positions, targets, owners = gathered()
    for _ in range(25):
        garden.update(positions, targets, owners, 1 / 30)
        garden.arrive(positions)
    couriers = np.flatnonzero(garden.destination >= 0)
    assert len(couriers) == 9
    assert set(garden.destination[couriers]) == {0, 1, 2}
    assert not garden.energy.any()  # Sending a school is not an arrival.
    destinations = garden.destination[couriers].copy()
    for _ in range(30):
        garden.update(positions, targets, owners, 1 / 30)
    positions[couriers] = garden.corals[destinations] - (0, 100)
    garden.arrive(positions)
    assert not garden.energy.any()  # Passing above the visible branches is not arrival.
    positions[couriers] = garden.corals[destinations]
    garden.arrive(positions)
    assert (garden.arrivals == 3).all()
    assert (garden.energy > 0.99).all()
    assert not (garden.destination >= 0).any()
    empty = np.empty((0, 2))
    for _ in range(90):
        garden.update(positions, empty, np.empty(0, dtype=np.uint8), 1 / 30)
    assert (garden.bloom > 0.9).all()
    assert not garden.active.any()


def test_lateral_choice_locks_trip_and_blocked_fish_do_not_awaken_coral():
    garden = CoralGarden()
    positions = np.tile((1000.0, 300.0), (24, 1))
    target = np.array(((1000.0, 300.0),))
    owner = np.array((1,), dtype=np.uint8)
    for _ in range(25):
        garden.update(positions, target, owner, 1 / 30)
    ids = np.flatnonzero(garden.destination >= 0)
    assert len(ids) == 3 and (garden.destination[ids] == 2).all()
    garden.update(positions, np.array(((300.0, 300.0),)), owner, 1 / 30)
    assert (garden.destination[ids] == 2).all()
    for _ in range(450):
        garden.update(positions, np.empty((0, 2)), np.empty(0, dtype=np.uint8), 1 / 30)
        garden.arrive(positions)
    assert not (garden.destination >= 0).any()
    assert not garden.energy.any() and not garden.arrivals.any()


def test_no_target_or_single_fish_cannot_auto_complete_the_garden():
    garden = CoralGarden()
    positions, targets, owners = gathered()
    positions[:] = (30, 30)
    for index in (0, 8, 16):
        positions[index] = targets[index // 8]
    for _ in range(120):
        garden.update(positions, targets, owners, 1 / 30)
        garden.arrive(positions)
    assert not (garden.destination >= 0).any()
    assert not garden.energy.any()


def test_full_aquarium_loop_keeps_storage_bounded_and_avoids_portal_lures():
    field = Viewport.fit((320, 240), SCENE_SIZE)
    world = LivingAquarium(field, (240, 320))
    mask = np.zeros((240, 320), dtype=bool)
    for x in (40, 140, 240):
        mask[65:195, x:x + 25] = True
        mask[100:107, x - 15:x + 40] = True
    world.update(mask, 0)
    for school in range(3):
        hand = world.targets[school * 2]
        world.position[school * 8:school * 8 + 8] = hand - (70, 0)
    for _ in range(600):
        world.update(mask, 1 / 30)
        assert len(world._food) <= 36
        assert world.position.shape == world.velocity.shape == (29, 2)
        assert world.garden.destination.shape == (24,)
    assert world.garden.arrivals.sum() >= 2
    assert world.garden.bloom.max() > 0.5
    assert np.isfinite(world.position).all()
    world.draw(pygame.Surface(SCENE_SIZE))
    # An upper tip placed in the world-switch portal cannot become a food lure.
    world.targets = np.array(((field.x + field.width * 0.16, field.height * 0.32),))
    world._target_owners = np.array((1,), dtype=np.uint8)
    world._previous = mask
    world.update(mask, 1 / 30)
    assert not world.garden.active.any()
    world.configure('Milt')
    assert world._motion < 1 and world._pearl_limit == 18
    assert world.position.shape == (29, 2)  # Changing comfort doesn't reset schools.


def test_nearby_fish_keep_space_instead_of_stacking_on_a_lure():
    field = Viewport.fit((320, 240), SCENE_SIZE)
    world = LivingAquarium(field, (240, 320))
    world.position[:24] = np.column_stack((np.linspace(50, 1200, 24), np.full(24, 600)))
    world.position[:2] = ((600, 300), (620, 300))
    world._home[:] = world.position
    world.velocity[:] = 0
    world.update(np.zeros((240, 320), dtype=bool), 0.05)
    assert world.velocity[0, 0] < 0 < world.velocity[1, 0]
    assert world.position[1, 0] - world.position[0, 0] > 20
