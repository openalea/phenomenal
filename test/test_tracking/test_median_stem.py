import numpy as np

from openalea.phenomenal.tracking.median_stem import normal_stem_shape


def test_stem_shape():
    polylines = [
        np.array([[np.random.random(), np.random.random(), k] for k in range(30)])
        for _ in range(5)
    ]

    polylines[2][15][[0, 1]] = 10  # abnormally distant point in 2nd polyline

    res1 = normal_stem_shape(polylines, dist_threshold=1e-5)
    res2 = normal_stem_shape(polylines, dist_threshold=5)
    res3 = normal_stem_shape(polylines, dist_threshold=1e5)

    assert res1 == [False, False, False, False, False]
    assert res2 == [True, True, False, True, True]
    assert res3 == [True, True, True, True, True]
