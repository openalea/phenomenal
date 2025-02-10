import os
import pytest

import openalea.phenomenal.object.voxelSegmentation as phm_seg
from openalea.phenomenal.tracking.display import plot_polylines

from openalea.phenomenal.tracking.phenomenal_coupling import phm_to_phenotrack_input
from openalea.phenomenal.tracking.trackedPlant import TrackedPlant


datadir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../data/tracking")


@pytest.fixture
def time_series():
    fd = datadir + "/time_series"
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


def test_display(time_series):
    phm_segs, timestamps = time_series
    phenotrack_segs, checks_stem = phm_to_phenotrack_input(phm_segs, timestamps)
    for seg in phenotrack_segs:
        print(seg)
        print(seg["polylines_sequence"])
        plot_polylines(seg["polylines_sequence"], ranks=[0])
