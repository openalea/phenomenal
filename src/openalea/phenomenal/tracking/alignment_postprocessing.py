"""
Functions used in the following post-processing steps after the alignment of
sequences of ligulated leaves :

- Remove abnormal columns in the alignment matrix (i.e. ranks corresponding to
artefacts, not to real leaves).
(detect_abnormal_ranks)

- Backwards tracking of each leaf in its growth phase until its emergence.
(leaf_polylines_distance)
"""

import numpy as np
from openalea.phenomenal.tracking.polyline_utils import (
    polyline_quantile_coordinate,
    polyline_length,
)


def detect_abnormal_ranks(alignment_matrix):
    """
    Specific to plant alignment.
    Detect abnormal columns in 'alignment_matrix' object resulting from multi
    alignment based on the following criteria:
    - A column is abnormal if it contains 2 times less aligned vectors in
    average (value != -1 in 'alignment_matrix') than the surrounding columns.
    - first and last columns can't be abnormal

    Parameters
    ----------
    alignment_matrix : 2D array
        result of multi_alignment() function

    Returns
    -------

    """

    alignment_matrix = np.array(alignment_matrix)
    counts = [
        len([k for k in alignment_matrix[:, i] if k != -1])
        for i in range(alignment_matrix.shape[1])
    ]
    abnormal_ranks = []
    for i, value in enumerate(counts):
        if 0 < i < len(counts) - 1 and value < 0.5 * np.mean(
            [counts[i - 1], counts[i + 1]]
        ):
            abnormal_ranks.append(i)

    return abnormal_ranks


def leaf_polylines_distance(polyline_ref, polyline_candidate, n=20):
    """
    Computes the distance between two leaf polylines.

    Parameters
    ----------
    polyline_ref : array
    polyline_candidate : array
    n : int

    Returns
    -------
    """

    # computing distance
    dist = 0
    for q in np.linspace(0, 1, n):
        pos1 = polyline_quantile_coordinate(polyline_ref, q)
        pos2 = polyline_quantile_coordinate(polyline_candidate, q)
        dist += np.sqrt(np.sum((pos1 - pos2) ** 2))

    # scale standardization
    dist_rescaled = dist / np.max((polyline_length(polyline_ref), 1e-6))

    return dist_rescaled
