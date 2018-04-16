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
from .plane_interception import intercept_points_along_path_with_planes
from ..object import (VoxelSkeleton, VoxelGrid, VoxelSegment)
# ==============================================================================


def segment_reduction(voxel_skeleton, image_views, tolerance=4,
                      nb_min_pixel=1):

    # Ordonner
    orderer_voxel_segments = sorted(voxel_skeleton.voxel_segments,
                                    key=lambda vs: len(vs.polyline))

    d = dict()
    tips = dict()
    for i, vs in enumerate(orderer_voxel_segments):
        for j, iv in enumerate(image_views):

            vp = numpy.array(list(vs.voxels_position))

            d[(i, j)] = project_voxel_centers_on_image(
                vp,
                voxel_skeleton.voxels_size,
                iv.image.shape,
                iv.projection)

            # vp = numpy.array([vs.polyline[-1]])
            # tips[(i, j)] = openalea.phenomenal.multi_view_reconstruction. \
            #     project_voxel_centers_on_image(
            #     vp,
            #     voxel_skeleton.voxels_size,
            #     iv.image.shape,
            #     iv.projection)

    list_negative_image = list()
    for iv in image_views:

        negative_image = iv.image.copy()
        negative_image[negative_image > 0] = 125
        negative_image[negative_image == 0] = 255
        negative_image[negative_image == 125] = 0
        list_negative_image.append(negative_image)

    index_removed = list()
    new_voxel_segments = list()
    for i, vs in enumerate(orderer_voxel_segments):

        # print i, index_removed
        weight = 0
        for j, iv in enumerate(image_views):
            im1 = d[(i, j)]
            # im1 = tips[(i, j)]

            im2 = numpy.zeros(iv.image.shape, dtype=numpy.int16)
            for k, _ in enumerate(orderer_voxel_segments):
                if k != i and k not in index_removed:
                    im2 += d[(k, j)]

            im1 = im1.astype(numpy.int16)
            im2[im2 > 0] = 255

            im = im1 - im2
            im = im - list_negative_image[j]
            im[im < 0] = 0
            if numpy.count_nonzero(im) >= nb_min_pixel:
                weight += 1

            if weight >= tolerance:
                break

        if weight >= tolerance:
            new_voxel_segments.append(vs)
        else:
            index_removed.append(i)

    vs = VoxelSkeleton(voxel_skeleton.voxels_size)
    vs.voxel_segments = new_voxel_segments

    return vs

# ==============================================================================


def find_base_stem_position(voxels_position, voxels_size, neighbor_size=45):
    """
    Function to find the base stem position of the plant from the voxels
    center positions list.

    Voxels position are converted in 3d image to find arround the x and y
    axis the points with the minimum value in a range of neighbor_side.

    :param voxels_position: 3d voxels center positions [(x, y, z), ...]
    :param voxels_size: diameter size of each voxels (mm)
    :param neighbor_size:
    :return:
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

    pos = numpy.array(stem_base_position)
    pos = pos * voxels_size + image_3d.world_coordinate

    return pos


def segment_path(voxels,
                 array_voxels,
                 skeleton_path,
                 graph,
                 voxels_size=4,
                 distance_plane=1.0,
                 windows_size=8):

    # ==========================================================================
    # Get the longest shorted path of voxels

    leaf_skeleton_path = None
    longest_length = 0
    for node in voxels:
        p = skeleton_path[node]

        if len(p) > longest_length:
            longest_length = len(p)
            leaf_skeleton_path = p

    # ==========================================================================

    if leaf_skeleton_path:

        closest_nodes, _ = intercept_points_along_path_with_planes(
            array_voxels,
            leaf_skeleton_path,
            windows_size=windows_size,
            distance_from_plane=distance_plane * voxels_size,
            points_graph=graph,
            voxels_size=voxels_size)

        # closest_nodes = compute_closest_nodes_with_ball(
        #     array_voxels,
        #     leaf_skeleton_path,
        #     ball_radius=ball_radius,
        #     graph=graph)

        voxels_position = set().union(*closest_nodes)
        vs = VoxelSegment(leaf_skeleton_path, voxels_position, closest_nodes)
        remain = set(voxels).difference(vs.voxels_position)

        # leaf, leaf_neighbors, connected_components_remain = merge(
        #     graph, leaf, remain, percentage=50)
        # remain = set().union(*connected_components_remain)

        return vs, remain


def compute_all_shorted_path(graph, voxels_size):
    """
    Compute all the shorted path from the base position of the graph
    position.
    :param graph: networkx voxel graph of 3d center point position
    :param voxels_size: voxels size of the graph voxels positions
    :return: list of all the shorted path of the graph from the base
    """
    # ==========================================================================
    # Get the high points in the matrix and the supposed base plant points
    x_stem, y_stem, z_stem = find_base_stem_position(graph.nodes(), voxels_size)

    # ==========================================================================
    # Compute the shorted path

    all_shorted_path_to_stem_base = networkx.single_source_dijkstra_path(
        graph, (x_stem, y_stem, z_stem), weight="weight")

    return all_shorted_path_to_stem_base


def skeletonize(graph, voxels_size, subgraph=None):

    if subgraph is None:
        subgraph = graph

    all_shorted_path_to_stem_base = compute_all_shorted_path(subgraph,
                                                             voxels_size)

    # ==========================================================================
    voxels_position_remain = subgraph.nodes()
    np_arr_all_graph_voxels_plant = numpy.array(graph.nodes())
    # ==========================================================================

    voxel_skeleton = VoxelSkeleton(voxels_size)
    while len(voxels_position_remain) != 0:

        (voxel_segment, voxels_position_remain) = segment_path(
            voxels_position_remain,
            np_arr_all_graph_voxels_plant,
            all_shorted_path_to_stem_base,
            graph,
            voxels_size=voxels_size)

        voxel_skeleton.add_voxel_segment(voxel_segment)

    return voxel_skeleton


