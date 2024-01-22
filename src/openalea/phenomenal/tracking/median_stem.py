import numpy as np
from scipy.spatial.distance import directed_hausdorff


def z_to_xy(polyline, z):
    """
    For all the points (x', y', z') in a polyline, this function returns the coordinates (x', y') whose corresponding
    z' height is the closest to z.

    Parameters
    ----------
    polyline : 2D array
        a 3D polyline
    z : int
        z coordinate in 3D space

    Returns
    -------
    float
        (x', y') coordinates
    """

    i = np.argmin(abs(np.array(polyline)[:, 2] - z))
    x, y = polyline[i][:2]
    return x, y


def get_median_polyline(polylines, n_stem_min=0, dz=2):
    """
    Returns a median polyline on the z axis

    Parameters
    ----------
    polylines : list
        list of 3D polylines
    n_stem_min : int
        This parameters determines the maximum height of the median polyline : median polyline is only computed at
        height z if at least n_stem_min polyline have a max height  > z.
    dz : float
        space between two successive points of the median polyline on z axis.

    Returns
    -------
    2D array
        3D median polyline

    """

    z = np.median([pl[0][2] for pl in polylines])
    median_polyline = []

    while len(polylines) > n_stem_min:

        xy = np.array([z_to_xy(pl, z) for pl in polylines])
        xy_median = list(np.median(xy, axis=0))
        median_polyline.append(xy_median + [z])

        polylines = [pl for pl in polylines if pl[-1][2] > z]
        z += dz

    return np.array(median_polyline)


def normal_stem_shape(polylines, dist_threshold=100):
    """
    From a list of polylines representing stem shapes: check if each polyline has a normal shape compared to the rest.

    Parameters
    ----------
    polylines : list
        list of 3D polylines
    dist_threshold : float
        a polyline whose hausdorff distance with the median polyline is above this threshold is considered as abnormal

    Returns
    -------
    list of bool
        True (= normal) or False (= abnormal) for each polyline
    """

    median_stem = get_median_polyline(polylines=polylines)

    is_normal = []
    for i, polyline in enumerate(polylines):
        d = directed_hausdorff(polyline, median_stem)[0]
        is_normal.append(d < dist_threshold)

    return is_normal
