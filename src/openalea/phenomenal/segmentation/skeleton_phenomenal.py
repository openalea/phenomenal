# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
from __future__ import division, print_function, absolute_import

import numpy
import networkx

from ..multi_view_reconstruction import project_voxel_centers_on_image
from .plane_interception import (
    intercept_points_along_path_with_planes,
    intercept_points_along_polyline_with_ball)
from ..object import (VoxelSkeleton, VoxelGrid, VoxelSegment)

# import openalea.phenomenal.segmentation._c_skeleton as c_skeleton
from . import _c_skeleton as c_skeleton
# ==============================================================================


def segment_reduction(voxel_skeleton,
                      image_projection,
                      required_visible=4,
                      nb_min_pixel=100):
    """
    Reduce the number of segments in a VoxelSkeleton object, according to
    their projection results. Each segments are kept if their projection on
    the images are not cover by the projection of the other segments in
    number required_visible. Segments are not cover if their remaining
    projected pixel are superio to nb_min_pixel.

    Parameters
    ----------
    voxel_skeleton : VoxelSkeleton
    image_projection : list of tuple (image, projection)
    required_visible : int, optional
        Number of required  not_covered segment to kept it.
    nb_min_pixel : int, optional
        Number of remaining pixel required to consider segment not covered
    Returns
    -------

    """
    # ==========================================================================


    # Ordonner
    orderer_voxel_segments = sorted(voxel_skeleton.segments,
                                    key=lambda vs: len(vs.polyline))

    # ==========================================================================
    # import time
    # start = time.time()

    # ==========================================================================

    # tips = dict()
    len_segments = len(orderer_voxel_segments)
    len_images = len(image_projection)
    list_array = [None] * len_segments * len_images
    for i, vs in enumerate(orderer_voxel_segments):
        for j, (image, projection) in enumerate(image_projection):

            vp = numpy.array(list(vs.voxels_position))
            list_array[i * len_images + j] = project_voxel_centers_on_image(
                vp,
                voxel_skeleton.voxels_size,
                image.shape,
                projection,
                dtype=numpy.int32,
                value=1)

            # vp = numpy.array([vs.polyline[-1]])
            # tips[(i, j)] = openalea.phenomenal.multi_view_reconstruction. \
            #     project_voxel_centers_on_image(
            #     vp,
            #     voxel_skeleton.voxels_size,
            #     iv.image.shape,
            #     iv.projection)

    # print("time processing , project_voxel_centers_on_image : {}".format(
    #     time.time() - start))
    # ==========================================================================
    # start = time.time()

    list_negative_image = list()
    for j, (image, projection) in enumerate(image_projection):

        negative_image = image.copy().astype(numpy.int32)
        negative_image[negative_image > 0] = 2
        negative_image[negative_image == 0] = 1
        negative_image[negative_image == 2] = 0
        list_negative_image.append(negative_image)

        list_array.append(negative_image)

    # print("time processing , negative_image : {}".format(time.time() - start))
    # ==========================================================================
    # start = time.time()

    is_removed = numpy.zeros(len_segments, dtype=numpy.uint8)

    c_skeleton.skeletonize(list_array, is_removed, len_segments, len_images,
                           nb_min_pixel, required_visible)

    segments = [orderer_voxel_segments[i] for i in range(len_segments) if
                is_removed[i] == 0]
    # print("time processing , C code covered : {}".format(time.time() - start))
    return VoxelSkeleton(segments, voxel_skeleton.voxels_size)

    # ==========================================================================
    # is_removed = numpy.zeros(len_segments, dtype=numpy.uint8)
    #
    # for i in range(len_segments):
    #     weight = 0
    #     for j in range(len(image_projection)):
    #         im = list_array[i * len_images + j] - list_negative_image[j]
    #         for k in range(len_segments):
    #             if k != i and not is_removed[k]:
    #                 im -= list_array[k * len_images + j]
    #
    #         if numpy.count_nonzero(im > 0) >= nb_min_pixel:
    #             weight += 1
    #
    #         if weight >= required_visible:
    #             break
    #
    #     if weight < required_visible:
    #         is_removed[i] = True
    #
    # print("time processing , covered : {}".format(time.time() - start))
    # segments = [orderer_voxel_segments[i] for i in range(len_segments) if
    #             not is_removed[i]]
    # return VoxelSkeleton(segments, voxel_skeleton.voxels_size)

# ==============================================================================


def _get_longest_shortest_path_in_nodes(nodes, paths):
    leaf_skeleton_path = None
    longest_length = 0
    for node in nodes:
        p = paths[node]

        if len(p) > longest_length:
            longest_length = len(p)
            leaf_skeleton_path = p

    return leaf_skeleton_path


def _segment_path(voxels,
                  array_voxels,
                  skeleton_path,
                  graph,
                  voxels_size=4,
                  mode="plane",
                  plane_width=4,
                  ball_radius=10):

    # ==========================================================================
    # Get the longest shorted path of voxels
    polyline = _get_longest_shortest_path_in_nodes(
        voxels, skeleton_path)

    # ==========================================================================

    if polyline:
        if mode == "ball":
            intercept_points = intercept_points_along_polyline_with_ball(
                array_voxels,
                graph,
                polyline,
                ball_radius=ball_radius)
        else:
            intercept_points, _ = intercept_points_along_path_with_planes(
                array_voxels,
                polyline,
                distance_from_plane=plane_width,
                points_graph=graph,
                voxels_size=voxels_size)

        voxels_position = set().union(*intercept_points)

        segment = VoxelSegment(polyline,
                               voxels_position,
                               intercept_points)

        remain = set(voxels).difference(segment.voxels_position)

        return segment, remain


def find_base_stem_position(voxels_position, voxels_size, neighbor_size=45):
    """ Function to find the base stem position of the plant from the voxels
    center positions list.

    Voxels position are converted in 3d image to find arround the x and y
    axis the points with the minimum value in a range of neighbor_side.

    Parameters
    ----------
    voxels_position : ndarray
        3d voxels center positions [(x, y, z), ...]

    voxels_size : int
        Voxel size diameter

    neighbor_size : int, optional
        Radius size in mm to search the base stem position

    Returns
    -------
    base_stem_position : 3-tuple
    """
    image_3d = VoxelGrid(voxels_position, voxels_size).to_image_3d()

    x = int(round(0 - image_3d.world_coordinate[0] / image_3d.voxels_size))
    y = int(round(0 - image_3d.world_coordinate[1] / image_3d.voxels_size))

    k = neighbor_size / voxels_size

    x_len, y_len, z_len = image_3d.shape

    roi = image_3d[int(max(x - k, 0)):int(min(x + k, x_len)),
                   int(max(y - k, 0)):int(min(y + k, y_len)),
                   :]

    xx, yy, zz = numpy.where(roi == 1)

    min_z_value = numpy.min(zz)
    index_min_z_value = numpy.where(zz == min_z_value)
    mean_float_point = numpy.array([numpy.mean(xx[index_min_z_value]),
                                    numpy.mean(yy[index_min_z_value]),
                                    numpy.mean(zz[index_min_z_value])])

    mean_point = None
    min_dist = float('inf')
    for xxx, yyy, zzz in zip(xx, yy, zz):
        pt = numpy.array([xxx, yyy, zzz])
        dist = numpy.linalg.norm(mean_float_point - pt)
        if dist < min_dist:
            min_dist = dist
            mean_point = pt

    stem_base_position = (int(max(x - k, 0)) + mean_point[0],
                          int(max(y - k, 0)) + mean_point[1],
                          mean_point[2])

    base_stem_position = (numpy.array(stem_base_position) * voxels_size +
                          image_3d.world_coordinate)

    return base_stem_position


def compute_all_shorted_path(graph, voxels_size, neighbor_size=45):
    """ Compute all the shorted path from the base position of the graph
    position.

    Parameters
    ----------
    graph : networkx.Graph
        Graph of 3d voxel center point position

    voxels_size : int
        Voxels diameter size

    Returns
    -------
    all_shorted_path_to_stem_base : dict
        List of all the shorted path of the graph from the base
    """
    # ==========================================================================
    # Get the high points in the matrix and the supposed base plant points
    x_stem, y_stem, z_stem = find_base_stem_position(
        graph.nodes(),
        voxels_size,
        neighbor_size=neighbor_size)

    # ==========================================================================
    # Compute the shorted path

    all_shorted_path_to_stem_base = networkx.single_source_dijkstra_path(
        graph, (x_stem, y_stem, z_stem), weight="weight")

    return all_shorted_path_to_stem_base


def skeletonize(voxel_grid,
                graph,
                subgraph=None,
                voxels_position_remain=None,
                mode="plane",
                plane_width=None,
                ball_radius=None,
                neighbor_size=45):
    """ Compute phenomenal skeletonization on the voxel_grid based on the graph.

    Parameters
    ----------
    voxel_grid : VoxelGrid

    graph : networkx.Graph

    subgraph: networkx.graph, optional
        If not None, perfom the computation of the shorted paths on the
        subgraph and remove voxels

    mode : str, optional
        Mode for intercept point along the paths. Two mode available, "ball"
        or "plane". By default "plane" mode.

    plane_width : int, optional
        Size in mm of the width of the plane. By default or if None is equal
        to the voxel_size of the voxel_grid

    ball_radius : int, optional
        Size in mm of the radius of the ball. By default or if None is equal
        to the voxel_size * 4 of the voxel_grid

    Returns
    -------
    voxel_skeleton : VoxelSkeleton
    """
    if plane_width is None:
        plane_width = voxel_grid.voxels_size * 2

    if ball_radius is None:
        ball_radius = voxel_grid.voxels_size * 4

    if subgraph is None:
        subgraph = graph

    voxels_size = voxel_grid.voxels_size
    all_shorted_path_to_stem_base = compute_all_shorted_path(
        subgraph, voxels_size, neighbor_size=neighbor_size)

    # ==========================================================================
    if voxels_position_remain is None:
        voxels_position_remain = subgraph.nodes()

    np_arr_all_graph_voxels_plant = numpy.array(graph.nodes())
    # ==========================================================================

    segments = list()
    while len(voxels_position_remain) != 0:

        (voxel_segment, voxels_position_remain) = _segment_path(
            voxels_position_remain,
            np_arr_all_graph_voxels_plant,
            all_shorted_path_to_stem_base,
            graph,
            voxels_size=voxels_size,
            mode=mode,
            plane_width=plane_width,
            ball_radius=ball_radius)

        segments.append(voxel_segment)

    return VoxelSkeleton(segments, voxels_size)
