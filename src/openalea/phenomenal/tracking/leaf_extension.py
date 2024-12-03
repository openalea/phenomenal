"""
Use binary images to extend the length of each phenomenal phm_leaf.

Method : A 2d skeleton is computed for the binary image at a given angle. Then,
the algorithm searches correspondences between phenomenal polylines
(reprojected in 2D) and skeleton polylines. For each match, an
extension factor e >= 1 is computed this way :
    e = (skeleton 2D polyline length) / (phenomenal 2D polyline length).
This is done for each side angle. Then, results are merged : for each
phenomenal phm_leaf, the final extension factor is equal to the median of
all extension values found for this phm_leaf, or 1 if no extension value
was found.
"""

import warnings
import cv2
import numpy as np

from skimage.morphology import skeletonize
from scipy.spatial.distance import directed_hausdorff
from skan.csr import skeleton_to_csgraph, Skeleton, summarize
from openalea.phenomenal.tracking.polyline_utils import polyline_length


def skeleton_branches(image, n_kernel=15, min_length=30):
    """

    Args:
        image: 2D array
            binary image
        n_kernel: int
            parameter for image dilatation
        min_length: float
            minimum length of skeleton branches (px)

    Returns: list
        list of 2D polylines with an endpoint
    """

    binary = image.copy()
    if round(np.max(binary)) == 255:
        binary = binary / 255.0

    # dilate image
    kernel = np.ones((n_kernel, n_kernel))
    binary_dilated = cv2.dilate(binary, kernel, iterations=1)

    # 2d skeleton image
    skeleton = skeletonize(binary_dilated)

    # skeleton analysis : get branches
    skan_skeleton = Skeleton(skeleton)
    branches = summarize(skan_skeleton, separator="-")

    # select branches having an endpoint, and a sufficient length
    branches_endpoint = branches[branches["branch-type"] == 1]
    branches_endpoint = branches_endpoint[
        branches_endpoint["branch-distance"] > min_length
    ]

    # converting branches to polylines
    _, coordinates = skeleton_to_csgraph(skeleton)
    node_ids = list(branches["node-id-src"]) + list(branches["node-id-dst"])
    polylines = []
    for irow, row in branches_endpoint.iterrows():
        polyline = np.array(
            [[coordinates[0][i], coordinates[1][i]] for i in skan_skeleton.path(irow)]
        )

        polyline = polyline[:, ::-1]  # same (x, y) order as phenomenal

        # verify that all phm_leaf polylines are oriented the same way (phm_leaf insertion --> phm_leaf tip)
        i = row["node-id-dst"]
        if node_ids.count(i) > 1:
            polyline = polyline[::-1]

        polylines.append(polyline)

    return polylines


def compute_extension(
    polylines_phm, polylines_sk, seg_length=50.0, dist_threshold=30.0
):
    """

    Args:
        polylines_phm: list
            list of 2D projections of 3D leaf polylines.
        polylines_sk: list
            list of 2D skeleton polylines.
        seg_length: float
            length (px) of the end segment of a phenomenal phm_leaf polyline that is compared with skeleton.
        dist_threshold: float
             hausdorff distance threshold (px) between polylines of both types to associate them.

    Returns:

    """

    res = dict.fromkeys(range(len(polylines_phm)), [])

    for pl_sk in polylines_sk:
        b_selected = 0
        dist_min = float("inf")
        selected_rank = -1

        for rank, pl_phm in enumerate(polylines_phm):
            # end segment of phenomenal polyline
            dists_to_end = np.linalg.norm(pl_phm - pl_phm[-1], axis=1)
            start = np.argmin(abs(dists_to_end - seg_length))
            pl_phm_segment = pl_phm[start:]

            # corresponding sk segment
            d_a = np.linalg.norm(pl_sk - pl_phm_segment[0], axis=1)
            a = np.argmin(d_a)
            d_b = np.linalg.norm(pl_sk - pl_phm_segment[-1], axis=1)
            b = np.argmin(d_b)
            pl_sk_segment = pl_sk[a : (b + 1)]

            # distance between phm and sk segments
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                d1 = directed_hausdorff(pl_sk_segment, pl_phm_segment)[0]
                d2 = directed_hausdorff(pl_phm_segment, pl_sk_segment)[0]
                dist = max(d1, d2)

            if dist < dist_threshold and b > b_selected:
                b_selected = b
                dist_min = dist
                selected_rank = rank

        if b_selected != 0:
            l1 = polyline_length(polylines_phm[selected_rank])
            l2 = polyline_length(pl_sk[b_selected:])
            extension_factor = (l2 + l1) / l1

            res[selected_rank] = res[selected_rank] + [
                (round(dist_min, 4), extension_factor, pl_sk[b_selected:])
            ]

    # verify that a phenomenal polyline has no more than 1 corresponding skeleton polyline.
    # And keep extension polylines in a list for optional display
    extension_polylines = []
    for k, resi in res.items():
        # 1 skeleton branch candidate
        if len(resi) == 1:
            _, extension_factor, extension_pl = resi[0]
            res[k] = extension_factor
            extension_polylines.append(extension_pl)
        # several skeleton branch candidates
        elif len(resi) > 1:
            d_min = float("inf")
            selected_pl = None
            for d, extension_factor, extension_pl in resi:
                if d < d_min:
                    d_min = d
                    res[k] = extension_factor
                    selected_pl = extension_pl
            extension_polylines.append(selected_pl)
        # no candidate
        else:
            res[k] = None

    return res, extension_polylines


def leaf_extension(phm_seg, binaries, projections):
    """

    Args:
        phm_seg: openalea.phenomenal.object.voxelSegmentation.VoxelSegmentation
            3D segmentation of a maize plant
        binaries: dict
            {side angle : binary image}. each image pixel equals 0 (background) or 255 (plant).
        projections: dict
            {side angle: 3D->2D projection function}

    Returns: openalea.phenomenal.object.voxelSegmentation.VoxelSegmentation
        phm_seg object with a new 'pm_length_extended' key in the .info attribute of each leaf.

    """

    # _____________________________________________________________________________________________________________

    # compute extension for each phenomenal phm_leaf and each camera angle. Regroup results in a dictionary.

    polylines_phm = [
        phm_seg.get_leaf_order(k).real_longest_polyline()
        for k in range(1, 1 + phm_seg.get_number_of_leaf())
    ]
    angles = binaries.keys()

    res = {}
    for angle in angles:
        # 2D skeleton polylines
        polylines_sk = skeleton_branches(binaries[angle])

        # phenomenal polylines projected in 2D
        polylines_phm_2d = [projections[angle](pl) for pl in polylines_phm]

        # compute phm_leaf extension factor for each phenomenal phm_leaf (if a result is found)
        extension_factors, _ = compute_extension(polylines_phm_2d, polylines_sk)

        res[angle] = extension_factors

    # _____________________________________________________________________________________________________________

    # merge results to have a single extension factor (median value) for each phenomenal phm_leaf.
    # (if no skeleton segment was found for a given phenomenal phm_leaf, extension factor have a default value of 1.)

    for k in range(1, 1 + phm_seg.get_number_of_leaf()):
        leaf_ext = [res[a][k - 1] for a in angles if res[a][k - 1] is not None]

        if phm_seg.get_leaf_order(k).info["pm_label"] == "growing_leaf":
            leaf_length = phm_seg.get_leaf_order(k).info["pm_length_with_speudo_stem"]
        else:
            leaf_length = phm_seg.get_leaf_order(k).info["pm_length"]

        if not leaf_ext:
            extension_factor = 1.0
        else:
            extension_factor = np.median(leaf_ext)

        phm_seg.get_leaf_order(k).info["pm_length_extended"] = (
            leaf_length * extension_factor
        )

    return phm_seg
