# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
"""
    This module is actually deprecated
"""
# ==============================================================================
from __future__ import division, print_function, absolute_import

import networkx
import numpy

from .graph import graph_from_voxel_grid
from .skeleton_phenomenal import skeletonize
# ==============================================================================


def find_base_stem_position_octree(octree, voxel_size, neighbor_size=50):
    k = neighbor_size * voxel_size

    def func_if_true_add_node(node):
        if node.size == voxel_size and node.data is True:
            x, y, z = node.position
            if -k <= x <= k:
                if -k <= y <= k:
                    return True
        return False

    def func_get(node):
        return node.position

    l = octree.root.get_nodes(func_if_true_add_node=func_if_true_add_node,
                              func_get=func_get)

    index = numpy.argmin(numpy.array(l)[:, 2])

    return numpy.array(l)[index]


def skeletonize_octree(voxel_octree,
                       voxels_size_to_skeletonize=4,
                       distance_planes=1,
                       voxels_size_output=4):

    # ==========================================================================

    vpc = voxel_octree.get_voxel_point_cloud(voxels_size_to_skeletonize)
    voxel_graph = graph_from_voxel_grid(vpc)
    voxel_skeleton = skeletonize(voxel_graph, graph,
                                 distance_plane=distance_planes)

    # return voxel_skeleton, voxel_graph

    # ==========================================================================

    if voxels_size_to_skeletonize == voxels_size_output:
        return voxel_skeleton, voxel_graph

    # ==========================================================================

    x_stem, y_stem, z_stem = find_base_stem_position_octree(
        voxel_octree, voxels_size_output)

    vpc = voxel_octree.get_voxel_point_cloud(voxels_size_output)
    voxel_graph = voxel_graph_from_voxel_grid(vpc)
    all_shorted_path_to_stem_base = networkx.single_source_dijkstra_path(
        voxel_graph.graph, (x_stem, y_stem, z_stem), weight="weight")

    for voxel_segment in voxel_skeleton.segments:

        voxels_position = list()
        for position in voxel_segment.voxels_position:
            node = voxel_octree.get_node_position(position)
            positions = node.get_sons_voxels_position_with_size(
                voxels_size_output)
            voxels_position.extend(positions)

        voxel_segment.voxels_position = voxels_position
        voxel_segment.voxels_size = voxels_size_output

        # ======================================================================
        # Get the longest shorted path of voxels

        voxels_position = list()
        for position in voxel_segment.polylines[0]:
            node = voxel_octree.get_node_position(position)
            positions = node.get_sons_voxels_position_with_size(
                voxels_size_output)
            voxels_position.extend(positions)

        polyline = None
        longest_length = 0
        for position in voxels_position:
            p = all_shorted_path_to_stem_base[position]

            if len(p) > longest_length:
                longest_length = len(p)
                polyline = p

        voxel_segment.polylines[0] = polyline

    return voxel_skeleton, voxel_graph
