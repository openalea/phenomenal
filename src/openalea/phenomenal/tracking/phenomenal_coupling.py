"""
Convert segmentation objets from Phenomenal to the input format required for TrackedPlant.
"""

import warnings
import numpy as np

from openalea.phenomenal.tracking.median_stem import normal_stem_shape
from openalea.phenomenal.tracking.polyline_utils import polyline_simplification


def phm_leaf_features(phm_leaf):
    features = {
        "mature": None,  # (bool) whether the leaf is mature (True) or growing (False).
        "azimuth": None,  # (float) leaf azimuth in degrees. in [0, 360].
        "height": None,  # (float) leaf insertion height. For a growing leaf, it corresponds to the height of
        # highest mature leaf.
        "length": None,  # (float) leaf length, starting from its insertion point.
    }

    if phm_leaf.info["pm_label"] == "mature_leaf":
        features["mature"] = True
        features["azimuth"] = phm_leaf.info["pm_azimuth_angle"]
        if "pm_length_extended" in phm_leaf.info:
            features["length"] = phm_leaf.info["pm_length_extended"]
        else:
            features["length"] = phm_leaf.info["pm_length"]
            warnings.warn(
                "Extented leaf length is not available, using polyline length instead"
            )

        if "pm_z_base_voxel" in phm_leaf.info:
            features["height"] = phm_leaf.info["pm_z_base_voxel"]
        else:
            features["height"] = phm_leaf.info["pm_z_base"]
            warnings.warn(
                "Insertion height computed from voxels is not available, using polyline base instead"
            )

    elif phm_leaf.info["pm_label"] == "growing_leaf":
        features["mature"] = False

    return features


def phm_to_phenotrack_input(phm_seg_list, timestamps):
    # check if the segmented stem has a normal shape at each time step
    stem_polylines = [
        np.array(phm_seg.get_stem().get_highest_polyline().polyline)
        for phm_seg in phm_seg_list
    ]
    checks_stem = np.array(normal_stem_shape(stem_polylines))

    # _____ create the TrackedPlant input ____________________________________________________________________________

    res = []

    for check, phm_seg, timestamp in zip(checks_stem, phm_seg_list, timestamps):
        if check:
            phm_ordered_leaves = [
                phm_seg.get_leaf_order(k)
                for k in range(1, 1 + phm_seg.get_number_of_leaf())
            ]

            # polylines are slightly simplified to manipulate smaller objects and gain time
            polylines_sq = [
                polyline_simplification(phm_leaf.real_longest_polyline(), 30)
                for phm_leaf in phm_ordered_leaves
            ]

            features_sq = [
                phm_leaf_features(phm_leaf) for phm_leaf in phm_ordered_leaves
            ]

            res.append(
                {
                    "time": timestamp,
                    "polylines_sequence": polylines_sq,
                    "features_sequence": features_sq,
                }
            )

    return res, checks_stem
