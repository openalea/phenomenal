import os
import cv2
import numpy as np

from openalea.phenomenal.tracking.leaf_extension import skeleton_branches, compute_extension, leaf_extension

import openalea.phenomenal.object.voxelSegmentation as phm_seg
from openalea.phenomenal.calibration import Calibration

datadir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../data/tracking/")


def test_skan_skeleton():

    binary = cv2.imread(datadir + '/binaries/90.png', 0)

    sk1 = skeleton_branches(image=binary, min_length=0.)
    sk2 = skeleton_branches(image=binary, min_length=30)
    sk3 = skeleton_branches(image=binary, min_length=120)

    assert len(sk1) > 0
    assert 3 < len(sk2) < 15
    assert len(sk1) >= len(sk2)
    assert len(sk2) >= len(sk3)


def test_extension():

    polylines = [np.random.random((n, 2)) for n in np.random.randint(30, 300, 12)]

    polylines2 = [np.random.random((n, 2)) for n in np.random.randint(30, 300, 8)]

    ext_factors, _ = compute_extension(polylines_phm=polylines2, polylines_sk=polylines,
                            seg_length=50., dist_threshold=30)

    assert set(ext_factors.keys()) == set(range(len(polylines2)))
    assert all([v >= 1. for v in [v for v in ext_factors.values() if v is not None]])


def test_full_leaf_extension_phenomenal():

    angles = [a * 30 for a in range(12)]

    binaries = {angle: cv2.imread(datadir + '/binaries/{}.png'.format(angle), 0)
                for angle in angles}

    seg = phm_seg.VoxelSegmentation.read_from_json_gz(datadir + '/segmentation.gz')

    assert all(['pm_length_extended' not in l.info for l in seg.get_leafs()])

    calibration = Calibration.load(datadir + '/calibration.json')
    projections = {angle: calibration.get_projection(id_camera='side', rotation=angle, world_frame='pot')
                   for angle in angles}

    new_seg = leaf_extension(phm_seg=seg, binaries=binaries, projections=projections)

    assert all(['pm_length_extended' in l.info for l in seg.get_leafs()])

    old_lengths = [l.info['pm_length_with_speudo_stem'] if l.info['pm_label'] == 'growing_leaf'
                   else l.info['pm_length'] for l in new_seg.get_leafs()]
    new_lengths = [l.info['pm_length_extended'] for l in new_seg.get_leafs()]

    assert all(np.array(old_lengths) <= np.array(new_lengths))



