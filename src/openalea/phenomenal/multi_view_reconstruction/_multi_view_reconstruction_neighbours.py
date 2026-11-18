# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================


import math
import collections
import numpy
import sklearn.neighbors

from .multi_view_reconstruction import Voxels, integral_image, check_each, project_voxels, get_bounding_box_voxel_projected, split_voxels_in_eight, voxels_is_visible_in_image, project_voxel_centers_on_image
from ..object import VoxelGrid

# ==============================================================================
# Class

VoxelsStage = collections.namedtuple("VoxelsStage", ["consistent", "inconsistent"])


def kept_visible_voxel(
    voxels_position, voxels_size, image_views, error_tolerance=0):
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


    Returns
    -------
    out : VoxelsStage
    """

    photo_consistent = numpy.zeros((len(voxels_position),), dtype=int)
    no_kept = None

    for i, image_view in enumerate(image_views):
        photo_consistent += voxels_is_visible_in_image(
            voxels_position=voxels_position,
            voxels_size=voxels_size,
            image=image_view.image,
            projection=image_view.projection,
            inclusive=image_view.inclusive,
            image_int=image_view.integral,
        )

        cond = photo_consistent >= i + 1 - error_tolerance

        if no_kept is None:
            no_kept = voxels_position[numpy.logical_not(cond)]
        else:
            no_kept = numpy.insert(
                no_kept, 0, voxels_position[numpy.logical_not(cond)], axis=0
            )

        voxels_position = voxels_position[cond]
        photo_consistent = photo_consistent[cond]

    consistent = Voxels(voxels_position, voxels_size)
    inconsistent = Voxels(no_kept, voxels_size)

    return VoxelsStage(consistent, inconsistent)


# ==============================================================================


def have_image_ref(image_views):
    """
    Returns whether an array of ImageView has a reference image or not.

    Parameters
    ----------
    image_views: array[ImageView]
        The array of ImageView to test

    Returns
    -------
    True if the array has a reference image else False.
    """
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
            voxel_projections = project_voxels(inconsistent.position, inconsistent.size, iv.projection)
            min_xy_max_xy = get_bounding_box_voxel_projected(voxel_projections)

            # add each voxel to a visual cones
            for i, (x_min, y_min, x_max, y_max) in enumerate(min_xy_max_xy):
                if x_max < 0 or x_min >= length or y_max < 0 or y_min >= height:
                    continue

                x_min = int(min(max(math.floor(x_min), 0), length - 1))
                y_min = int(min(max(math.floor(y_min), 0), height - 1))
                x_max = int(min(max(math.floor(x_max), 0), length - 1))
                y_max = int(min(max(math.floor(y_max), 0), height - 1))

                img = iv.image_ref[y_min : y_max + 1, x_min : x_max + 1]
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

    positions = []
    for index in groups.values():
        index = numpy.array(index)

        distance, _ = neigh.kneighbors(inconsistent.position[index])
        distance = distance.min(axis=1)
        xx = distance.argsort()[:nb_distance]
        positions.append(inconsistent.position[index[xx]])

    position = numpy.unique(numpy.concatenate(positions, axis=0), axis=0)

    return Voxels(position, inconsistent.size)


def reconstruction_inconsistent(image_views, stages, attractor=None):
    for iv in image_views:
        if iv.image_ref is not None:
            im = project_voxel_centers_on_image(
                stages[-1].consistent.position,
                stages[-1].consistent.size,
                iv.image.shape,
                iv.projection,
            )
            iv.il = iv.image_ref - im
            iv.yy, iv.xx = numpy.where(iv.il > 0)

    consistent_neighbors = sklearn.neighbors.NearestNeighbors(
        n_neighbors=1, metric="euclidean"
    )

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
                (inconsistent.position, voxels.position), axis=0
            )
            position = numpy.unique(position, axis=0)
            inconsistent = Voxels(position, inconsistent.size)

        groups = create_groups(image_views, inconsistent)
        nb_distance = max(20 - int((20 / len(stages)) * i), 2)
        consistents[i] = check_groups(
            consistent_neighbors, inconsistent, groups, nb_distance
        )

    consistent_stages = [None] * len(stages)
    for i, (stage, consistent) in enumerate(zip(stages, consistents)):
        consistent_stages[i] = stage.consistent
        if consistent is not None:
            voxels_position = numpy.concatenate(
                (consistent_stages[i].position, consistent.position), axis=0
            )

            voxels_position = numpy.unique(voxels_position, axis=0)

            consistent_stages[i] = Voxels(voxels_position, consistent.size)

    return consistent_stages


def reconstruction_3d_neighbours(
    image_views,
    voxels_size=4,
    error_tolerance=0,
    voxel_center_origin=(0.0, 0.0, 0.0),
    start_voxel_size=4096,
    voxels_position=None,
    attractor=None,
    clear_outside=True,
    reference_views=None
):
    """
    Construct a list of voxel represented object with positive value on binary
    image in images of images_projections.

    Parameters
    ----------

    image_views : {name: ImageView, ...}
        Dict of phenomenal.object.ImageView objects gathering image, projection, where image is a binary image
        (numpy.ndarray) and projection a function projecting (x, y, z) ->  (u, v) coordinate on image


    voxels_size : float, optional
        Diameter size of the voxels

    error_tolerance : int, optional
        the number of inconsistent views tolerated per voxel

    voxel_center_origin : (x, y, z), optional
        Center position of the first original voxel, who will be split.

    start_voxel_size: int, optional
        Minimum size that the origin voxel size must include at beginning

    voxels_position : numpy.ndarray, optional
        List of first original voxel who will be split. If None, a list is
        created with the voxel_center_origin value.

    attractor: optional, the attractor given to sklearn.nearest_neighbours function

    clear_outside: bool | str | [str,...], optional
        Should voxels projected outside image_views be kept ? True (default) or False set a unique rule for all views.
        if a list of name is provided, only image_views whose key starts with names are used to clear voxels

    reference_views: bool | str | [str,...], optional
        List the views to be considered as reference ones for colonisation by neighbours during reconstruction
        If None (default) simple reconstruction is done, without neighbours colonisation


    Returns
    -------
    out : VoxelGrid
    """

    if len(image_views) == 0:
        raise ValueError("Len images view have not length")

    if voxels_position is None:
        voxels_position = numpy.array([voxel_center_origin])

    list_voxels_size = [
        voxels_size * 2**i
        for i in range(20, -1, -1)
        if voxels_size * 2 ** (i - 1) < start_voxel_size
    ]

    # Pre-processing (optimization): Compute integral image for speed
    # computation
    clear_view = check_each(image_views, clear_outside)
    is_image_ref = check_each(image_views, reference_views)
    for k, image_view in image_views.items():
        if image_view.integral is None:
            image_view.integral = integral_image(image_view.image)
        image_view.inclusive = not clear_view[k]
        image_view.image_ref = None if not is_image_ref[k] else image_view.image

    stage = VoxelsStage(Voxels(voxels_position, list_voxels_size[0]), None)
    stages = [stage]

    while stage.consistent.size != voxels_size:
        if len(stage.consistent.position) == 0:
            break

        voxels = split_voxels_in_eight(stage.consistent)

        # print(voxels.size)

        if voxels.size < 512:
            stage = kept_visible_voxel(
                voxels.position,
                voxels.size,
                image_views.values(),
                error_tolerance=error_tolerance
            )
        else:
            stage = VoxelsStage(voxels, None)

        stages.append(stage)

    consistent_stages = [stage.consistent for stage in stages]
    if have_image_ref(image_views.values()):
        consistent_stages = reconstruction_inconsistent(
            image_views.values(), stages, attractor=attractor
        )

    return VoxelGrid(consistent_stages[-1].position, consistent_stages[-1].size)
