# -*- python -*-
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
from __future__ import division, print_function

import scipy.spatial
import collections
import numpy
import sklearn.neighbors

from openalea.phenomenal.object import VoxelGrid
# ==============================================================================


def get_voxels_corners(voxels_position, voxels_size):
    """
    According center voxel position and this size, return a list of 8 corners
    of this voxel.

    Parameters
    ----------
    voxel_center : (x, y, z)
        Center position of voxel

    voxel_size : float
        Size of side geometry of voxel

    Returns
    -------
    [(x, y, z), ...] : numpy.ndarray
         List of 8 tuple position

    """

    r = voxels_size / 2.0

    x_minus = voxels_position[:, 0] - r
    x_plus = voxels_position[:, 0] + r
    y_minus = voxels_position[:, 1] - r
    y_plus = voxels_position[:, 1] + r
    z_minus = voxels_position[:, 2] - r
    z_plus = voxels_position[:, 2] + r

    a1 = numpy.column_stack((x_minus, y_minus, z_minus))
    a2 = numpy.column_stack((x_plus, y_minus, z_minus))
    a3 = numpy.column_stack((x_minus, y_plus, z_minus))
    a4 = numpy.column_stack((x_minus, y_minus, z_plus))
    a5 = numpy.column_stack((x_plus, y_plus, z_minus))
    a6 = numpy.column_stack((x_plus, y_minus, z_plus))
    a7 = numpy.column_stack((x_minus, y_plus, z_plus))
    a8 = numpy.column_stack((x_plus, y_plus, z_plus))

    a = numpy.concatenate((a1, a2, a3, a4, a5, a6, a7, a8), axis=1)
    a = numpy.reshape(a, (a.shape[0] * 8, 3))

    return a


def get_bounding_box_voxel_projected(voxels_position,
                                     voxels_size,
                                     projection):
    """
    Compute the bounding box value according the radius, angle and calibration
    parameters of point_3d projection

    Parameters
    ----------
    voxel_center : (x, y, z)
        Center position of voxel

    voxel_size : float
        Size of side geometry of voxel

    projection : function ((x, y, z)) -> (x, y)
        Function of projection who take 1 argument (tuple of position (x, y, z))
         and return this position 2D (x, y)

    Returns
    -------
    out : (x_min, x_max, y_min, y_max)
        Containing min and max value of point_3d projection in x and y axes.
    """

    voxels_corners = get_voxels_corners(voxels_position, voxels_size)

    pt = projection(voxels_corners)

    pt = numpy.reshape(pt, (pt.shape[0] // 8, 8, 2))

    bbox = numpy.column_stack((pt.min(axis=1), pt.max(axis=1)))

    return bbox

# ==============================================================================


def split_voxel_centers_in_eight(voxels_position, voxel_size):
    """
    Split each voxel in the collections.deque in 8 en return a collections.deque
    of this new center position of voxel splited::

          _ _ _ _ _ _ _ _ _                              _ _ _ _ _ _ _ _ _
        /                  /|                          /        /         /|
       /                  / |                         /--------/---------/ |
      /_ _ _ _ _ _ _ _ _ /  |                        /_ _ _ _ / _ _ _ _ /| |
     |                  |   |                       |        |         | |/|
     |                  |   |       =======>        |        |         | / |
     |                  |   |                       |_ _ _ _ | _ _ _ _ |/| |
     |                  |  /                        |        |         | |/
     |                  | /                         |        |         | /
     | _ _ _ _ _ _ _ _ _|/                          |_ _ _ _ | _ _ _ _ |/



    Parameters
    ----------
    voxel_centers : [(x, y, z)]
        collections.deque of center position of voxel

    voxel_size : float
        Size of side geometry of the voxels

    Returns
    -------
    [(x, y, z), ...] : collections.deque
         New collections.deque of new tuple position splited of each
         voxel_center in voxel_centers

    """
    if len(voxels_position) == 0:
        return voxels_position

    r = voxel_size / 4.0

    x_minus = voxels_position[:, 0] - r
    x_plus = voxels_position[:, 0] + r
    y_minus = voxels_position[:, 1] - r
    y_plus = voxels_position[:, 1] + r
    z_minus = voxels_position[:, 2] - r
    z_plus = voxels_position[:, 2] + r

    a1 = numpy.column_stack((x_minus, y_minus, z_minus))
    a2 = numpy.column_stack((x_plus, y_minus, z_minus))
    a3 = numpy.column_stack((x_minus, y_plus, z_minus))
    a4 = numpy.column_stack((x_minus, y_minus, z_plus))
    a5 = numpy.column_stack((x_plus, y_plus, z_minus))
    a6 = numpy.column_stack((x_plus, y_minus, z_plus))
    a7 = numpy.column_stack((x_minus, y_plus, z_plus))
    a8 = numpy.column_stack((x_plus, y_plus, z_plus))

    return numpy.concatenate((a1, a2, a3, a4, a5, a6, a7, a8), axis=0)


# ==============================================================================

def voxels_is_visible_in_image(voxels_position,
                               voxels_size,
                               image,
                               projection,
                               inclusive):
    """
    Return True or False if the voxel projected on image with the function
    projection (projection) have positive value on image.

    **Algorithm**

    1. Project the center voxel position on image if the position projected
       (x, y) is positive on image return True

    |

    2. Project the bounding box of voxel in image, if one of the 4 corners
       position of the bounding box projected have positive value on image
       return True

    |

    3. Check if one pixel containing in the bounding box projected on image
       have positive value, if yes return True else return False

    Parameters
    ----------
    voxel_center : (x, y, z)
        Center position of voxel

    voxel_size : float
        Size of side geometry of voxel

    image: numpy.ndarray
        binary image

    projection : function ((x, y, z)) -> (x, y)
        Function of projection who take 1 argument (tuple of position (x, y, z))
         and return this position 2D (x, y)

    Returns
    -------
    out : bool
        True if voxel have a positive correspondence on image otherwise return
        False
    """

    height, length = image.shape
    ori_result = numpy.zeros((len(voxels_position, )), dtype=int)

    r = projection(voxels_position)

    cond = ((r[:, 0] >= 0) &
            (r[:, 1] >= 0) &
            (r[:, 0] < length) &
            (r[:,  1] < height))

    rr = r[cond]
    rr = rr.astype(int)

    (ori_result[cond])[image[rr[:, 1], rr[:, 0]] > 0] = 1

    cond = ori_result > 0
    not_cond = numpy.logical_not(cond)

    result = ori_result[not_cond]
    voxels_position = voxels_position[not_cond]

    # ==========================================================================

    min_xy_max_xy = get_bounding_box_voxel_projected(
        voxels_position, voxels_size, projection)

    vv = ((min_xy_max_xy[:, 2] < 0) | (min_xy_max_xy[:, 0] >= length) |
          (min_xy_max_xy[:, 3] < 0) | (min_xy_max_xy[:, 1] >= height))

    not_vv = numpy.logical_not(vv)
    result[vv] = 1 if inclusive else 0

    min_xy_max_xy = min_xy_max_xy[not_vv]
    bb = result[not_vv]

    min_xy_max_xy = numpy.floor(min_xy_max_xy)

    min_xy_max_xy[min_xy_max_xy < 0] = 0
    (min_xy_max_xy[:, 0])[min_xy_max_xy[:, 0] >= length] = length - 1
    (min_xy_max_xy[:, 1])[min_xy_max_xy[:, 1] >= height] = height - 1
    (min_xy_max_xy[:, 2])[min_xy_max_xy[:, 2] >= length] = length - 1
    (min_xy_max_xy[:, 3])[min_xy_max_xy[:, 3] >= height] = height - 1
    min_xy_max_xy = min_xy_max_xy.astype(int)

    for i, (x_min, y_min, x_max, y_max) in enumerate(min_xy_max_xy):
        if numpy.any(image[y_min:y_max + 1, x_min:x_max + 1] > 0):
            bb[i] = 1

    result[not_vv] = bb
    ori_result[not_cond] = result

    return ori_result


# ==============================================================================


def kept_visible_voxel(voxels_position,
                       voxels_size,
                       image_views,
                       error_tolerance=0):
    """
    Kept in a new collections.deque the voxel who is visible on each image of
    images_projections according the error_tolerance

    Parameters
    ----------
    voxel_centers : [(x, y, z)]
        cList (collections.deque) of center position of voxel

    voxel_size : float
        Size of side geometry of voxel

    images_projections : [(image, projection), ...]
        List of tuple (image, projection) where image is a binary image
        (numpy.ndarray) and function projection (function (x, y, z) -> (x, y))
        who take (x, y, z) position on return (x, y) position according space
        representation of this image

    error_tolerance : int, optional
        Number of image will be ignored if the projected voxel is not visible.

    Returns
    -------
    out : collections.deque
        List of visible voxel projected on each image according
        the error_tolerance

    """

    photo_consistent = numpy.zeros((len(voxels_position), ),  dtype=int)
    no_kept = None

    for i, image_view in enumerate(image_views):
        photo_consistent += voxels_is_visible_in_image(
            voxels_position,
            voxels_size,
            image_view.image,
            image_view.projection,
            image_view.inclusive)

        cond = photo_consistent >= i + 1 - error_tolerance

        if no_kept is None:
            no_kept = voxels_position[numpy.logical_not(cond)]
        else:
            no_kept = numpy.insert(no_kept,
                                   0,
                                   voxels_position[numpy.logical_not(cond)],
                                   axis=0)

        voxels_position = voxels_position[cond]
        photo_consistent = photo_consistent[cond]

    return voxels_position, no_kept


def create_groups(image_views, kept, no_kept, voxels_size):

    groups = collections.defaultdict(list)
    kept_groups = collections.defaultdict(list)

    group_id = 0
    for iv in image_views:
        if iv.ref is True:
            height, length = iv.image.shape

            res = get_bounding_box_voxel_projected(
                no_kept, voxels_size, iv.projection)

            vv = ((res[:, 2] < 0) | (res[:, 0] >= length) |
                  (res[:, 3] < 0) | (res[:, 1] >= height))

            not_vv = numpy.logical_not(vv)
            res = res[not_vv]
            no_kept = no_kept[not_vv]

            res = numpy.floor(res)
            res[res < 0] = 0

            (res[:, 0])[res[:, 0] >= length] = length - 1
            (res[:, 1])[res[:, 1] >= height] = height - 1
            (res[:, 2])[res[:, 2] >= length] = length - 1
            (res[:, 3])[res[:, 3] >= height] = height - 1
            res = res.astype(int)

            for i, (x_min, y_min, x_max, y_max) in enumerate(res):
                img = iv.image[y_min:y_max + 1, x_min:x_max + 1]
                xx, yy = numpy.where(img > 0)

                xx += y_min
                yy += x_min

                for x, y in zip(xx, yy):
                    groups[(group_id, x, y)].append(i)

            im = project_voxel_centers_on_image(kept, voxels_size,
                                                iv.image.shape,
                                                iv.projection)

            il = iv.image - im
            xx, yy = numpy.where(il > 0)

            for x, y in zip(xx, yy):
                if len(groups[(group_id, x, y)]) > 0:
                    kept_groups[(group_id, x, y)] = groups[(group_id, x, y)]

        group_id += 1

    return kept_groups, no_kept


def kept_groups(kept, no_kept, groups):

    l_index = groups.values()
    if l_index:
        l_index = [numpy.array(index) for index in l_index]

        for index in l_index:
            pts = no_kept[index]
            if len(kept) == 0:
                kept = pts
            else:
                kept = numpy.insert(kept, 0, pts, axis=0)

    # kept = numpy.unique(kept, axis=0)
    kept = numpy.vstack(set(tuple(row) for row in kept))

    return kept


def check_groups(kept, no_kept, groups):

    l_index = groups.values()
    if l_index:
        l_index = [numpy.array(index) for index in l_index]

        neigh = sklearn.neighbors.NearestNeighbors(
            n_neighbors=1, metric='euclidean')

        neigh.fit(kept)
        distance, index_nodes = neigh.kneighbors(no_kept)

        # Ordered by min distance from kept voxel
        min_dist = [numpy.min(distance[index]) for index in l_index]
        l_index = [y for (x, y) in sorted(zip(min_dist, l_index),
                                          key=lambda k: k[0])]

        kk = set()
        for index in l_index:

            if len(kk.intersection(set(index))) > 0:
                continue

            distance, index_nodes = neigh.kneighbors(no_kept[index])

            if len(list(kk)) > 0:

                dist = scipy.spatial.distance.cdist(no_kept[index],
                                                    no_kept[numpy.array(list(kk))],
                                                    'euclidean')

                a = numpy.insert(dist, [0], distance, axis=1)
                distance = a.min(axis=1)

            else:
                distance = distance[:, 0]

            m = numpy.min(distance)
            xx = numpy.unique(numpy.where(distance == m))
            pts = no_kept[index[xx]]
            kk = kk.union(set(list(index[xx])))

            if len(kept) == 0:
                kept = pts.copy()
            else:
                kept = numpy.insert(kept, 0, pts.copy(), axis=0)

            # kept = numpy.insert(kept, 0, pts, axis=0)

    return kept


# ==============================================================================

from openalea.phenomenal.display import show_images

def reconstruction_3d(image_views,
                      voxels_size=4,
                      error_tolerance=0,
                      voxel_center_origin=(0.0, 0.0, 0.0),
                      world_size=4096,
                      voxels_position=None,
                      verbose=False):
    """
    Construct a list of voxel represented object with positive value on binary
    image in images of images_projections.

    Parameters
    ----------
    
    images_projections : [(image, projection), ...]
        List of tuple (image, projection) where image is a binary image
        (numpy.ndarray) and function projection (function (x, y, z) -> (x, y))
        who take (x, y, z) position on return (x, y) position according space
        representation of this image

    voxels_size : float, optional
        Size of side geometry of voxel that each voxel will have

    error_tolerance : int, optional

    voxel_center_origin : (x, y, z), optional
        Center position of the first original voxel, who will be split.

    world_size: int, optional
        Minimum size that the origin voxel size must include at beginning

    voxels_position : collections.deque, optional
        List of first original voxel who will be split. If None, a list is
        create with the voxel_center_origin value.

    verbose : bool, optional
        If True, print for each iteration of split, number of voxel before and
        after projection on images

    Returns
    -------
    out : collections.deque
        List of visible voxel projected on each image according
        the error_tolerance
    """

    if len(image_views) == 0:
        raise ValueError("Len images view have not length")

    if voxels_position is None:
        voxels_position = collections.deque()
        voxels_position.append(voxel_center_origin)

    nb_iteration = 0
    while voxels_size < world_size:
        voxels_size *= 2.0
        nb_iteration += 1

    voxels_position = numpy.array(voxels_position)

    for i in range(nb_iteration):

        if len(voxels_position) == 0:
            break

        voxels_position = split_voxel_centers_in_eight(
            voxels_position, voxels_size)

        voxels_size /= 2.0

        if verbose is True:
            print("Iteration {} / {} : {}".format(
                i + 1, nb_iteration, len(voxels_position)))

        if voxels_size >= 512:
            continue

        voxels_position, no_kept = kept_visible_voxel(
            voxels_position, voxels_size, image_views,
            error_tolerance=error_tolerance)

        groups, no_kept = create_groups(
            image_views, voxels_position, no_kept, voxels_size)

        if i + 1 < nb_iteration or len(voxels_position) == 0:
            voxels_position = kept_groups(voxels_position, no_kept, groups)
        else:
            voxels_position = check_groups(voxels_position, no_kept, groups)

    # voxels_position = numpy.unique(voxels_position, axis=0)

    return VoxelGrid(voxels_position, voxels_size)

# ==============================================================================


def project_voxel_centers_on_image(voxels_position,
                                   voxels_size,
                                   shape_image,
                                   projection):
    """
    Create a image with same shape that shape_image and project each voxel on
    image and write positive value (255) on it.

    Parameters
    ----------
    voxels_position : [(x, y, z)]
        cList (collections.deque) of center position of voxel

    voxels_size : float
        Size of side geometry of voxel

    shape_image: Tuple
        size height and length of the image target projected

    projection : function ((x, y, z)) -> (x, y)
        Function of projection who take 1 argument (tuple of position (x, y, z))
         and return this position 2D (x, y)

    Returns
    -------
    out : numpy.ndarray
        Binary image
    """

    voxels_position = numpy.array(voxels_position)
    height, length = shape_image
    img = numpy.zeros((height, length), dtype=numpy.uint8)

    res = get_bounding_box_voxel_projected(
        voxels_position, voxels_size, projection)

    vv = ((res[:, 2] < 0) | (res[:, 0] >= length) |
          (res[:, 3] < 0) | (res[:, 1] >= height))

    not_vv = numpy.logical_not(vv)
    res = res[not_vv]

    # res = res[(res[:, 2] >= 0) & (res[:, 0] < length) &
    #           (res[:, 3] >= 0) & (res[:, 1] < height)]

    res = numpy.floor(res)
    res[res < 0] = 0
    (res[:, 0])[res[:, 0] >= length] = length - 1
    (res[:, 1])[res[:, 1] >= height] = height - 1
    (res[:, 2])[res[:, 2] >= length] = length - 1
    (res[:, 3])[res[:, 3] >= height] = height - 1
    res = res.astype(int)

    for x_min, y_min, x_max, y_max in res:
        img[y_min:y_max + 1, x_min:x_max + 1] = 255

    return img


def image_error(img_ref, img_src, precision=2):
    """
    Return false position and true negative result from the comparaison on 
    two binaries images
    """

    img_ref = img_ref.astype(numpy.int32)
    nb_ref = max(numpy.count_nonzero(img_ref), 1)
    img_src = img_src.astype(numpy.int32)
    img = numpy.subtract(img_ref, img_src)
    false_positive = round(len(img[img < 0]) * 100.0 / nb_ref, precision)
    true_negative = round(len(img[img > 0]) * 100.0 / nb_ref, precision)

    return false_positive, true_negative


def reconstruction_error(vpc, image_views):
    """
    Compute the reconstruction error (false positive and true negative) of 
    the 3d reconstruction from the image view.

    Parameters
    ----------
    img_ref: numpy.ndarray
        binary image reference

    projection : function ((x, y, z)) -> (x, y)
        Function of projection who take 1 argument (tuple of position (x, y, z))
         and return this position 2D (x, y)

    voxels_position : [(x, y, z)]
        cList (collections.deque) of center position of voxel

    voxels_size : float
        Size of side geometry of voxel

    Returns
    -------
    out : int
        Error value
    """

    sum_false_positive = 0
    sum_true_negative = 0
    for image_view in image_views:

        img_src = project_voxel_centers_on_image(
            vpc.voxels_position,
            vpc.voxels_size,
            image_view.image.shape,
            image_view.projection)

        false_positive, true_negative = image_error(
            image_view.image, img_src)

        sum_false_positive += false_positive
        sum_true_negative += true_negative

    mean_false_positive = sum_false_positive / len(image_views)
    mean_true_negative = sum_true_negative / len(image_views)

    return mean_false_positive, mean_true_negative
