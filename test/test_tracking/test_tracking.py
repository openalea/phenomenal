import os
import numpy as np
import pytest
from vtkmodules.util.numpy_support import vtk_to_numpy

import openalea.phenomenal.object.voxelSegmentation as phm_seg
from openalea.phenomenal.display import Scene
from openalea.phenomenal.tracking.display import plot_polylines

from openalea.phenomenal.tracking.phenomenal_coupling import phm_to_phenotrack_input
from openalea.phenomenal.tracking.trackedPlant import TrackedPlant

from pathlib import Path
test_subdir = Path(__file__).parent if '__file__' in globals() else Path(".").resolve()
data_dir = test_subdir.parent / "data" / "tracking"

@pytest.fixture
def time_series():
    fd = data_dir / "time_series"
    phm_segs, timestamps = [], []
    for filename in os.listdir(fd):
        timestamps.append(int(filename.split(".gz")[0]))
        phm_segs.append(
            phm_seg.VoxelSegmentation.read_from_json_gz(os.path.join(fd, filename))
        )

    return phm_segs, timestamps


def test_time_continuity(time_series):
    phm_segs, timestamps = time_series
    phenotrack_segs, checks_stem = phm_to_phenotrack_input(phm_segs, timestamps)

    assert all(checks_stem)

    for k in [2, 3, 4]:
        phenotrack_segs[k]["time"] *= 2
    trackedplant = TrackedPlant.load(phenotrack_segs)

    assert [s.check_continuity for s in trackedplant.snapshots] == [
        True,
        True,
        False,
        False,
        False,
    ]


def test_convert_phenomenal_to_tracking_format(time_series):
    phm_segs, timestamps = time_series
    phenotrack_segs, checks_stem = phm_to_phenotrack_input(phm_segs, timestamps)

    for seg in phenotrack_segs:
        assert set(seg.keys()) == {"time", "polylines_sequence", "features_sequence"}
        for polyline, features in zip(
            seg["polylines_sequence"], seg["features_sequence"]
        ):
            assert set(features.keys()) == {"mature", "azimuth", "height", "length"}
            assert len(polyline.shape) == 2 and polyline.shape[1] == 3


def test_tracking_mature(time_series):
    phm_segs, timestamps = time_series
    phenotrack_segs, checks_stem = phm_to_phenotrack_input(phm_segs, timestamps)

    trackedplant = TrackedPlant.load(phenotrack_segs)

    assert all([s.check_continuity for s in trackedplant.snapshots])
    assert all([s.sequence == [] for s in trackedplant.snapshots])

    trackedplant.mature_leaf_tracking()

    for snapshot in trackedplant.snapshots:
        sq = snapshot.sequence
        assert len(sq) == len(trackedplant.snapshots[0].sequence)
        assert len([i for i in sq if i != -1]) == len(
            set([i for i in sq if i != -1])
        )  # no redundancy

    output, _, _ = trackedplant.output()

    assert [len(o) == len(s.leaves) for o, s in zip(output, trackedplant.snapshots)]

    trackedplant.mature_leaf_tracking(gap=12.0)
    l1 = len(trackedplant.snapshots[0].sequence)
    trackedplant.mature_leaf_tracking(gap=5.0)
    l2 = len(trackedplant.snapshots[0].sequence)
    trackedplant.mature_leaf_tracking(gap=1.0)
    l3 = len(trackedplant.snapshots[0].sequence)

    assert l1 <= l2
    assert l2 <= l3


def test_tracking_growing(time_series):
    phm_segs, timestamps = time_series
    phenotrack_segs, checks_stem = phm_to_phenotrack_input(phm_segs, timestamps)
    trackedplant = TrackedPlant.load(phenotrack_segs)
    trackedplant.mature_leaf_tracking()

    trackedplant.growing_leaf_tracking()

    output, _, _ = trackedplant.output()

    assert [len(o) == len(s.leaves) for o, s in zip(output, trackedplant.snapshots)]


def displayed_colors(monkeypatch, polylines, ranks):
    """Plot without opening a window, and return the actor and its RGB colors."""
    actors = []
    monkeypatch.setattr(Scene, "show", lambda self, **kwargs: None)
    monkeypatch.setattr(Scene, "add_actor", lambda self, actor: actors.append(actor))
    plot_polylines(polylines, ranks)

    output = actors[0].GetMapper().GetInput()
    return output, vtk_to_numpy(output.GetCellData().GetScalars())


def test_display(time_series, monkeypatch):
    phm_segs, timestamps = time_series
    phenotrack_segs, checks_stem = phm_to_phenotrack_input(phm_segs, timestamps)
    for seg in phenotrack_segs:
        polylines = seg["polylines_sequence"]
        output, colors = displayed_colors(monkeypatch, polylines, [0] * len(polylines))
        assert output.GetNumberOfPoints() > 0
        np.testing.assert_array_equal(np.unique(colors, axis=0), [[90, 90, 90]])


def test_display_colors_by_rank(monkeypatch):
    polylines = [[(0, 0, 0), (10, 0, 0)], [(0, 10, 0), (10, 10, 0)], [(0, 20, 0), (10, 20, 0)]]
    _, colors = displayed_colors(monkeypatch, polylines, [1, 2, -1])
    np.testing.assert_array_equal(
        np.unique(colors, axis=0), [[0, 255, 0], [90, 90, 90], [255, 0, 0]]
    )
