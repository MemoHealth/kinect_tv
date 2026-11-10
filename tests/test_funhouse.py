import numpy as np

from magic_rain.interaction.funhouse import Funhouse, source_indices


def test_convex_and_concave_have_opposite_effect_on_center_silhouette():
    mask = np.zeros((240, 320), dtype=bool)
    mask[88:152, 134:186] = True
    mirror = Funhouse()
    assert mirror.warp(mask, 0) is mask
    convex = mirror.warp(mask, -0.37)
    concave = mirror.warp(mask, 0.44)
    assert convex.sum() > mask.sum() > concave.sum()
    assert convex[120, 160] and concave[120, 160]


def test_mapping_stays_inside_frame_without_reversing_horizontal_order():
    for strength in (-0.37, 0.44):
        rows, cols = source_indices((240, 320), strength)
        assert rows.min() == 0 and rows.max() == 239
        assert cols.min() == 0 and cols.max() == 319
        assert (np.diff(cols, axis=1) >= 0).all()
        mask = np.zeros((240, 320), dtype=bool)
        for center in (35, 160, 284):
            mask[65:180, center - 13:center + 14] = True
        row = Funhouse().warp(mask, strength)[120]
        assert np.count_nonzero(row[1:] & ~row[:-1]) == 3
