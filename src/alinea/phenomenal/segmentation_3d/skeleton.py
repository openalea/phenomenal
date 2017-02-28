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
import numpy
import networkx

from alinea.phenomenal.segmentation_3d.algorithm import (
    merge)

from alinea.phenomenal.segmentation_3d.plane_interception import (
    compute_closest_nodes_with_planes,
    compute_closest_nodes_with_ball)

from alinea.phenomenal.data_structure import (VoxelSkeleton,
                                              VoxelSegment,
                                              VoxelPointCloud)
# ==============================================================================


def find_base_stem_position(voxels_position, voxels_size, neighbor_size=50):

    image_3d = VoxelPointCloud(voxels_position, voxels_size).to_image_3d()

    x = int(round(0 - image_3d.world_coordinate[0] / image_3d.voxels_size))
    y = int(round(0 - image_3d.world_coordinate[1] / image_3d.voxels_size))

    k = neighbor_size / voxels_size
    x_len, y_len, z_len = image_3d.shape

    roi = image_3d[max(x - k, 0): min(x + k, x_len),
                   max(y - k, 0): min(y + k, y_len),
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

    stem_base_position = (max(x - k, 0) + mean_point[0],
                          max(y - k, 0) + mean_point[1],
                          mean_point[2])

    pos = numpy.array(stem_base_position)
    pos = pos * voxels_size + image_3d.world_coordinate

    return pos


def segment_path(voxels,
                 array_voxels,
                 skeleton_path,
                 graph,
                 distance_plane=0.75):

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

        # closest_nodes = compute_closest_nodes_with_planes(
        #     array_voxels,
        #     leaf_skeleton_path,
        #     radius=8,
        #     dist=distance_plane,
        #     graph=graph)

        closest_nodes = compute_closest_nodes_with_ball(
            array_voxels,
            leaf_skeleton_path)

        leaf = set().union(*closest_nodes)
        remain = set(voxels).difference(leaf)

        leaf, leaf_neighbors, connected_components_remain = merge(
            graph, leaf, remain)

        remain = set().union(*connected_components_remain)

        return leaf, remain, leaf_skeleton_path


def compute_all_shorted_path(graph, voxels_size):

    # ==========================================================================
    # Get the high points in the matrix and the supposed base plant points
    x_stem, y_stem, z_stem = find_base_stem_position(graph.nodes(), voxels_size)

    # ==========================================================================
    # Compute the shorted path

    all_shorted_path_to_stem_base = networkx.single_source_dijkstra_path(
        graph, (x_stem, y_stem, z_stem), weight="weight")

    return all_shorted_path_to_stem_base


def skeletonize(graph, voxels_size, distance_plane=1):

    all_shorted_path_to_stem_base = compute_all_shorted_path(graph, voxels_size)

    # ==========================================================================
    voxels_position_remain = graph.nodes()
    np_arr_all_graph_voxels_plant = numpy.array(graph.nodes())
    # ==========================================================================

    voxel_segments = list()
    while len(voxels_position_remain) != 0:

        (voxels_position_segment,
         voxels_position_remain,
         voxels_segments_polyline) = segment_path(
            voxels_position_remain,
            np_arr_all_graph_voxels_plant,
            all_shorted_path_to_stem_base,
            graph,
            distance_plane=distance_plane * voxels_size)

        voxel_segment = VoxelSegment(voxels_position_segment,
                                     voxels_size,
                                     [voxels_segments_polyline])

        voxel_segments.append(voxel_segment)

    voxel_skeleton = VoxelSkeleton(voxel_segments)

    return voxel_skeleton


