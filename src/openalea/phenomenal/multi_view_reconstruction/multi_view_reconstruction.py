# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
from __future__ import division, print_function

import math
import numba
import cv2
import scipy.spatial
import collections
import numpy
import sklearn.neighbors

from ..object import VoxelGrid
# ==============================================================================
# Class

Voxels = collections.namedtuple("Voxels", ['position', 'size'])
VoxelsStage = collections.namedtuple(
    "VoxelsStage", ['consistent', 'inconsistent'])


# ==============================================================================

def get_voxels_corners(voxels_position, voxels_size):
    """ According the voxels position and their size, return a numpy array
    containing for each input voxels the position of the 8 corners.

    Parameters
    ----------
    voxels_position : numpy.ndarray
        Center position of the voxels

    voxels_size : float
        Diameter size of the voxels

    Returns
    -------
    a : numpy.array
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

    """ Compute the bounding box value according the radius, angle and
    calibration parameters of point_3d projection

    Parameters
    ----------
    voxels_position : numpy.ndarray
        Center position of voxel

    voxels_size : float
        Size of side geometry of voxel

    projection : function ((x, y, z)) -> (x, y)
        Function of projection who take 1 argument (tuple of position (x, y, z))
        and return this position 2D (x, y)

    Returns
    -------
    bbox : numpy.ndarray
        [[x_min, x_max, y_min, y_max], ...]
        Containing min and max value of point_3d projection in x and y axes.
    """

    voxels_corners = get_voxels_corners(voxels_position, voxels_size)

    pt = projection(voxels_corners)

    pt = numpy.reshape(pt, (pt.shape[0] // 8, 8, 2))

    bbox = numpy.column_stack((pt.min(axis=1), pt.max(axis=1)))

    return bbox

# ==============================================================================


def split_voxels_in_eight(voxels):
    """ Split each voxel in 8 en return the numpy.array position

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
    voxels : Voxels
        Where position is a numpy.array([[x, y, z], ...] containing the center
        position of each voxels and size the diameter size value (float) of each
        voxels.

    Returns
    -------
    voxels : Voxels
    """
    if len(voxels.position) == 0:
        return Voxels(voxels.position, voxels.size / 2.0)

    r = voxels.size / 4.0

    x_minus = voxels.position[:, 0] - r
    x_plus = voxels.position[:, 0] + r
    y_minus = voxels.position[:, 1] - r
    y_plus = voxels.position[:, 1] + r
    z_minus = voxels.position[:, 2] - r
    z_plus = voxels.position[:, 2] + r

    a1 = numpy.column_stack((x_minus, y_minus, z_minus))
    a2 = numpy.column_stack((x_plus, y_minus, z_minus))
    a3 = numpy.column_stack((x_minus, y_plus, z_minus))
    a4 = numpy.column_stack((x_minus, y_minus, z_plus))
    a5 = numpy.column_stack((x_plus, y_plus, z_minus))
    a6 = numpy.column_stack((x_plus, y_minus, z_plus))
    a7 = numpy.column_stack((x_minus, y_plus, z_plus))
    a8 = numpy.column_stack((x_plus, y_plus, z_plus))

    return Voxels(numpy.concatenate((a1, a2, a3, a4, a5, a6, a7, a8), axis=0),
                  voxels.size / 2.0)


# ==============================================================================

def voxels_is_visible_in_image(voxels_position,
                               voxels_size,
                               image,
                               projection,
                               inclusive,
                               image_int=None):
    """
    Return a numpy array containing True if the voxel are
        projected is photo-consistent on image else False

    **Algorithm**

    1. Project each voxel center position on the image, if the position
    projected (x, y) is positive on image return True

    |

    2. If the bouding box of the voxel projected have positive value on
    the image the voxel are True

    |

    3. Check if one pixel containing in the bounding box projected on image
       have positive value, if yes return True else return False

    Parameters
    ----------
    voxels_position : numpy.array([[x, y, z], ...]
        Center position of the voxels

    voxels_size : float
        diameter size of the voxels

    image: numpy.array
        Binary image where the voxels are projected.

    projection : function (numpy.array([[x, y, z], ...]) -> numpy.array([[x, y], ...])
        Function of projection who take 1 argument (numpy.array([[x, y, z],
        ...] of voxels positions) and return the projected 2D position
        numpy.array([[x, y], ...])

    inclusive: Describe if the voxels projection are out of the image,
    their are considering like still visible

    image_int: Integrale image of the binary image (optimization)


    Returns
    -------
    out : numpy.array([True, False, ...])
        Numpy array containing True if the voxel are
        projected is photo-consistent on image else False
    """

    height, length = image.shape
    ori_result = numpy.zeros((len(voxels_position, )), dtype=int)

    r = projection(voxels_position)

    cond = ((r[:, 0] >= 0) &
            (r[:, 1] >= 0) &
            (r[:, 0] < length) &
            (r[:,  1] < height))

    rr = r[cond].astype(int)

    (ori_result[cond])[image[rr[:, 1], rr[:, 0]] > 0] = 1
    not_cond = numpy.logical_not(ori_result > 0)

    result = ori_result[not_cond]
    voxels_position = voxels_position[not_cond]

    # ==========================================================================

    # voxels_corners = get_voxels_corners(voxels_position, voxels_size)
    # pt = projection(voxels_corners)
    # pt = numpy.reshape(pt, (pt.shape[0] // 8, 8, 2))
    # tim = image.astype(int)
    # im = numpy.zeros_like(tim, dtype=int)
    # conds = list()
    #
    # for points in pt:
    #
    #     if (numpy.all(points[:, 0] < 0) == True or
    #         numpy.all(points[:, 0] >= length) == True or
    #         numpy.all(points[:, 1] < 0) == True or
    #         numpy.all(points[:, 1] >= height) == True):
    #         conds.append(False)
    #         continue
    #
    #     points[points < 0] = 0
    #     (points[:, 0])[points[:, 0] >= length] = length - 1
    #     (points[:, 1])[points[:, 1] >= height] = height - 1
    #     points = numpy.floor(points).astype(int)
    #
    #     if numpy.all(points[:, 0] == points[0, 0]) == True:
    #         x = points[0, 0]
    #         y_min = numpy.min(points[:, 1])
    #         y_max = numpy.max(points[:, 1])
    #
    #         if numpy.count_nonzero(image[y_min:y_max, x]) > 0:
    #             conds.append(True)
    #         else:
    #             conds.append(False)
    #         continue
    #
    #     if numpy.all(points[:, 1] == points[0, 1]) == True:
    #         y = points[0, 1]
    #         x_min = numpy.min(points[:, 0])
    #         x_max = numpy.max(points[:, 0])
    #
    #         if numpy.count_nonzero(image[y, x_min:x_max]) > 0:
    #             conds.append(True)
    #         else:
    #             conds.append(False)
    #         continue
    #
    #     hull = scipy.spatial.ConvexHull(points)
    #     im[:] = 0
    #     cv2.fillConvexPoly(im, points[hull.vertices], 1)
    #     if numpy.any(tim[im == 1] > 0) == True:
    #         conds.append(True)
    #     else:
    #         conds.append(False)
    #
    # result[conds] = 1
    # ori_result[not_cond] = result
    #
    # return ori_result

    # ==========================================================================

    min_xy_max_xy = get_bounding_box_voxel_projected(
        voxels_position, voxels_size, projection)

    # result = numba_optimize_voxels_is_visible_in_image(
    #     min_xy_max_xy, image_int, result, length, height, inclusive)
    #
    # ori_result[not_cond] = result
    #
    # return ori_result

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

    # ==========================================================================

    min_xy_max_xy[:, 0:2] -= 1
    for i, (x_min, y_min, x_max, y_max) in enumerate(min_xy_max_xy):

        r1 = image_int[y_max, x_max]
        if y_min > 0:
            r1 -= image_int[y_min, x_max]
        if x_min > 0:
            r1 -= image_int[y_max, x_min]
        if y_min > 0 and x_min > 0:
            r1 += image_int[y_min, x_min]

        if r1 > 0:
            bb[i] = 1

    # for i, (x_min, y_min, x_max, y_max) in enumerate(min_xy_max_xy):
    #     if numpy.count_nonzero(image[y_min:y_max + 1, x_min:x_max + 1]) > 0:
    #         bb[i] = 1

    result[not_vv] = bb
    ori_result[not_cond] = result

    return ori_result


# ==============================================================================

def kept_visible_voxel(voxels_position,
                       voxels_size,
                       image_views,
                       error_tolerance=0,
                       int_images=None):
    """
    Kept in a new collections.deque the voxel who is visible on each image of
    images_projections according the error_tolerance

    Parameters
    ----------
    voxels_position : numpy.array([[x, y, z], ...]
        Center position of the voxels

    voxels_size : float
        Diameter size of the voxels

    image_views : [(image, projection), ...]
        List of tuple (image, projection) where image is a binary image
        (numpy.ndarray) and function projection (function (x, y, z) -> (x, y))
        who take (x, y, z) position on return (x, y) position according space
        representation of this image

    error_tolerance : int, optional
        Number of image will be ignored if the projected voxel is not visible.

    int_images: Integral image of the binary image (optimization)

    Returns
    -------
    out : VoxelsStage
    """

    photo_consistent = numpy.zeros((len(voxels_position), ),  dtype=int)
    no_kept = None

    for i, image_view in enumerate(image_views):
        photo_consistent += voxels_is_visible_in_image(
            voxels_position,
            voxels_size,
            image_view.image,
            image_view.projection,
            image_view.inclusive,
            image_int=int_images[i])

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

    consistent = Voxels(voxels_position, voxels_size)
    inconsistent = Voxels(no_kept, voxels_size)

    return VoxelsStage(consistent, inconsistent)

# ==============================================================================


def have_image_ref(image_views):
    for iv in image_views:
        if iv.image_ref is not None:
            return True
    return False


def create_groups(image_views, inconsistent):

    groups = collections.defaultdict(list)
    kept_groups = collections.defaultdict(list)

    group_id = 0
    for iv in image_views:
        if iv.image_ref is not None:
            height, length = iv.image.shape

            min_xy_max_xy = get_bounding_box_voxel_projected(
                inconsistent.position, inconsistent.size, iv.projection)

            # add each voxels to a visual cones
            for i, (x_min, y_min, x_max, y_max) in enumerate(min_xy_max_xy):

                if x_max < 0 or x_min >= length or y_max < 0 or y_min >= height:
                    continue

                x_min = int(min(max(math.floor(x_min), 0), length - 1))
                y_min = int(min(max(math.floor(y_min), 0), height - 1))
                x_max = int(min(max(math.floor(x_max), 0), length - 1))
                y_max = int(min(max(math.floor(y_max), 0), height - 1))

                img = iv.image_ref[y_min:y_max + 1, x_min:x_max + 1]
                yy, xx = numpy.where(img > 0)
                yy += y_min
                xx += x_min
                for y, x in zip(yy, xx):
                    groups[(group_id, y, x)].append(i)

            for y, x in zip(iv.yy, iv.xx):
                if len(groups[(group_id, y, x)]) > 0:
                    kept_groups[(group_id, y, x)] = groups[(group_id, y, x)]

        group_id += 1

    return kept_groups


def check_groups(neigh, inconsistent, groups, nb_distance):

    if len(groups.values()) == 0:
        return None

    positions = list()
    for index in groups.values():
        index = numpy.array(index)

        distance, _ = neigh.kneighbors(inconsistent.position[index])
        distance = distance.min(axis=1)
        xx = distance.argsort()[:nb_distance]
        positions.append(inconsistent.position[index[xx]])

    position = numpy.concatenate(positions, axis=0)
    position = numpy.vstack(set(tuple(row) for row in position))

    return Voxels(position, inconsistent.size)


def reconstruction_inconsistent(image_views, stages, attractor=None):

    for iv in image_views:
        if iv.image_ref is not None:
            im = project_voxel_centers_on_image(stages[-1].consistent.position,
                                                stages[-1].consistent.size,
                                                iv.image.shape,
                                                iv.projection)
            iv.il = iv.image_ref - im
            iv.yy, iv.xx = numpy.where(iv.il > 0)

    consistent_neighbors = sklearn.neighbors.NearestNeighbors(
        n_neighbors=1, metric='euclidean')

    if numpy.size(stages[-1].consistent.position) == 0:
        consistent_neighbors.fit(numpy.array([[0, 0, 0]]))
    else:
        if attractor is not None:
            consistent_neighbors.fit(attractor)
        else:
            consistent_neighbors.fit(stages[-1].consistent.position)

    consistents = [None] * len(stages)
    for i, stage in enumerate(stages):

        if stage.inconsistent is None:
            continue

        inconsistent = stage.inconsistent
        if consistents[i - 1] is not None:
            voxels = split_voxels_in_eight(consistents[i - 1])
            position = numpy.concatenate(
                (inconsistent.position, voxels.position), axis=0)
            position = numpy.vstack(set(tuple(row) for row in position))
            inconsistent = Voxels(position, inconsistent.size)

        groups = create_groups(image_views, inconsistent)
        nb_distance = max(20 - int((20 / len(stages)) * i), 2)
        consistents[i] = check_groups(
            consistent_neighbors, inconsistent, groups, nb_distance)

    consistent_stages = [None] * len(stages)
    for i, (stage, consistent) in enumerate(zip(stages, consistents)):

        consistent_stages[i] = stage.consistent
        if consistent is not None:
            voxels_position = numpy.concatenate(
                (consistent_stages[i].position, consistent.position), axis=0)

            voxels_position = numpy.vstack(
                set(tuple(row) for row in voxels_position))

            consistent_stages[i] = Voxels(voxels_position, consistent.size)

    return consistent_stages


# ==============================================================================

@numba.jit()
def get_integrale_image(img):
    a = numpy.zeros_like(img, dtype=int)
    for y, x in numpy.ndindex(a.shape):
            r = 0
            if img[y, x] > 0:
                r += 1
            if x - 1 >= 0:
                r += a[y, x - 1]
            if y - 1 >= 0:
                r += a[y - 1, x]
            if x - 1 >= 0 and y - 1 >= 0:
                r -= a[y - 1, x - 1]
            a[y, x] = r
    return a

# ==============================================================================


def reconstruction_3d(image_views,
                      voxels_size=4,
                      error_tolerance=0,
                      voxel_center_origin=(0.0, 0.0, 0.0),
                      start_voxel_size=4096,
                      voxels_position=None,
                      attractor=None):
    """
    Construct a list of voxel represented object with positive value on binary
    image in images of images_projections.

    Parameters
    ----------
    
    image_views : [(image, projection), ...]
        List of tuple (image, projection) where image is a binary image
        (numpy.ndarray) and function projection (function (x, y, z) -> (x, y))
        who take (x, y, z) position on return (x, y) position according space
        representation of this image

    voxels_size : float, optional
        Diameter size of the voxels

    error_tolerance : int, optional

    voxel_center_origin : (x, y, z), optional
        Center position of the first original voxel, who will be split.

    start_voxel_size: int, optional
        Minimum size that the origin voxel size must include at beginning

    voxels_position : numpy.ndarray, optional
        List of first original voxel who will be split. If None, a list is
        create with the voxel_center_origin value.

    Returns
    -------
    out : VoxelGrid
    """

    if len(image_views) == 0:
        raise ValueError("Len images view have not length")

    if voxels_position is None:
        voxels_position = numpy.array([voxel_center_origin])

    list_voxels_size = [voxels_size * 2 ** i for i in range(20, -1, -1) if
                        voxels_size * 2 ** (i - 1) < start_voxel_size]

    # Pre-processing (optimization): Compute integral image for speed
    # computation
    int_images = list()
    for i, image_view in enumerate(image_views):
        a = get_integrale_image(image_view.image)
        int_images.append(a)

    stage = VoxelsStage(Voxels(voxels_position, list_voxels_size[0]), None)
    stages = [stage]

    while stage.consistent.size != voxels_size:
        if len(stage.consistent.position) == 0:
            break

        voxels = split_voxels_in_eight(stage.consistent)

        if voxels.size < 512:
            stage = kept_visible_voxel(
                voxels.position, voxels.size, image_views,
                error_tolerance=error_tolerance,
                int_images=int_images)
        else:
            stage = VoxelsStage(voxels, None)

        stages.append(stage)

    consistent_stages = [stage.consistent for stage in stages]
    if have_image_ref(image_views):
        consistent_stages = reconstruction_inconsistent(image_views, stages,
                                                        attractor=attractor)

    return VoxelGrid(consistent_stages[-1].position, consistent_stages[-1].size)

# ==============================================================================


def project_voxel_centers_on_image(voxels_position,
                                   voxels_size,
                                   shape_image,
                                   projection,
                                   value=255,
                                   dtype=numpy.uint8):
    """
    Create a image with same shape that shape_image and project each voxel on
    image and write positive value (255) on it.

    Parameters
    ----------
    voxels_position : numpy.ndarray
        Voxels center position [[x, y, z], ...]
    voxels_size : float
        Diameter size of the voxels
    shape_image: 2-tuple
        Size height and length of the image target projected
    projection : function ((x, y, z)) -> (x, y)
        Function of projection who take 1 argument (tuple of position (x, y, z))
         and return this position 2D (x, y)
    value : int
        value between 0 and 255 of positive pixel. By default 255.
    dtype : type
        numpy type of the returned image. By default numpy.uint8.

    Returns
    -------
    out : numpy.ndarray
        Binary image
    """
    height, length = shape_image
    img = numpy.zeros((height, length), dtype=dtype)

    min_xy_max_xy = get_bounding_box_voxel_projected(
        voxels_position, voxels_size, projection)

    vv = ((min_xy_max_xy[:, 2] < 0) |
          (min_xy_max_xy[:, 0] >= length) |
          (min_xy_max_xy[:, 3] < 0) |
          (min_xy_max_xy[:, 1] >= height))

    not_vv = numpy.logical_not(vv)
    min_xy_max_xy = min_xy_max_xy[not_vv]

    min_xy_max_xy = numpy.floor(min_xy_max_xy)
    min_xy_max_xy[min_xy_max_xy < 0] = 0
    (min_xy_max_xy[:, 0])[min_xy_max_xy[:, 0] >= length] = length - 1
    (min_xy_max_xy[:, 1])[min_xy_max_xy[:, 1] >= height] = height - 1
    (min_xy_max_xy[:, 2])[min_xy_max_xy[:, 2] >= length] = length - 1
    (min_xy_max_xy[:, 3])[min_xy_max_xy[:, 3] >= height] = height - 1
    min_xy_max_xy = min_xy_max_xy.astype(int)

    for x_min, y_min, x_max, y_max in min_xy_max_xy:
        img[y_min:y_max + 1, x_min:x_max + 1] = value

    return img


def project_voxels_position_on_image(voxels_position,
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

    voxels_corners = get_voxels_corners(voxels_position, voxels_size)
    pt = projection(voxels_corners)
    pt = numpy.reshape(pt, (pt.shape[0] // 8, 8, 2))

    pt[pt < 0] = 0
    (pt[:, :, 0])[pt[:, :, 0] >= length] = length - 1
    (pt[:, :, 1])[pt[:, :, 1] >= height] = height - 1
    pt = numpy.floor(pt).astype(int)
    for points in pt:
        hull = scipy.spatial.ConvexHull(points)
        cv2.fillConvexPoly(img, points[hull.vertices], 255)

    return img

# ==============================================================================


def image_error(img_ref, img_src, precision=2):
    """
    Return false position and true negative result from the comparaison on 
    two binaries images
    """

    img_ref = img_ref.astype(numpy.int32)
    nb_ref = max(numpy.count_nonzero(img_ref), 1)
    nb_ref2 = max(numpy.count_nonzero(img_ref == 0), 1)
    img_src = img_src.astype(numpy.int32)
    img = numpy.subtract(img_ref, img_src)
    true_negative = numpy.bitwise_and(img_ref == 0, img_src == 0)
    true_negative = round(numpy.count_nonzero(true_negative) * 100.0 / nb_ref2,
                          precision)
    # true_negative = numpy.bitwise_and(img_ref == 0, img_src == 0)


    false_positive = round(numpy.count_nonzero(img[img < 0]) * 100.0 / nb_ref2,
                           precision)
    false_negative = round(numpy.count_nonzero(img[img > 0]) * 100.0 / nb_ref,
                           precision)
    print(true_negative, false_positive, false_negative)
    return false_positive, false_negative


def reconstruction_error(voxels_grid, image_views):
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
    sum_false_negative = 0
    for image_view in image_views:

        img_src = project_voxel_centers_on_image(
            voxels_grid.voxels_position,
            voxels_grid.voxels_size,
            image_view.image.shape,
            image_view.projection)

        false_positive, false_negative = image_error(
            image_view.image, img_src)

        sum_false_positive += false_positive
        sum_false_negative += false_negative

    mean_false_positive = sum_false_positive / len(image_views)
    mean_false_negative = sum_false_negative / len(image_views)

    return mean_false_positive, mean_false_negative
