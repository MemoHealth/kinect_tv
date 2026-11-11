import numpy as np

from magic_rain.render.coverage import soften


def test_display_filter_softens_steps_without_bridging_a_three_pixel_gap():
    mask = np.zeros((20, 28), dtype=bool)
    for y in range(3, 16):
        mask[y, 3:y // 2 + 7] = True
    mask[4:16, 20:22] = True
    original = mask.copy()
    coverage = soften(mask)
    assert np.array_equal(mask, original)
    assert ((coverage > 0) & (coverage < 1)).any()
    assert coverage.max() == 1
    assert coverage[8, 21] >= 0.5
    assert not coverage[:, 17:19].any()
    narrow = np.zeros((12, 16), dtype=bool)
    narrow[2:10, 4:6] = True
    narrow[2:10, 9:11] = True
    filtered = soften(narrow)
    assert filtered[6, 5] >= 0.5 and filtered[6, 9] >= 0.5
    assert filtered[6, 7] == 0  # Columns 6, 7 and 8 form the exact gap.
