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

from alinea.phenomenal.segmentation_3d.algorithm import (
    graph_skeletonize,
    merge)

from alinea.phenomenal.segmentation_3d.plane_interception import (
    compute_closest_nodes)

# ==============================================================================


def segment_path(voxels, array_voxels,
                 skeleton_path,
                 graph,
                 distance_plane=0.75,
                 verbose=False):

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

        planes, closest_nodes = compute_closest_nodes(
            array_voxels,
            leaf_skeleton_path,
            radius=8,
            dist=distance_plane,
            verbose=True,
            graph=graph)

        leaf = set().union(*closest_nodes)
        remain = set(voxels).difference(leaf)

        leaf, leaf_neighbors, connected_components_remain = merge(
            graph, leaf, remain)

        remain = set().union(*connected_components_remain)

        return leaf, remain, leaf_skeleton_path


def skeletonize(voxels_plant, voxel_size, distance_plane=1.0, verbose=False):

    # ==========================================================================
    # Build skeleton of plant with graph of shorted path

    graph, biggest_connected_voxels_plant, skeleton_path = \
        graph_skeletonize(voxels_plant, voxel_size)

    voxel_plant_not_connected = set(graph.nodes()).difference(set(voxels_plant))

    # ==========================================================================
    voxels_plant = biggest_connected_voxels_plant
    arr_voxels_plant = numpy.array(biggest_connected_voxels_plant)
    # ==========================================================================

    remain = voxels_plant
    segment = list()
    while len(remain) != 0:

        segment_voxel, remain, segment_ske_path = segment_path(
            remain, arr_voxels_plant, skeleton_path, graph,
            distance_plane=distance_plane * voxel_size)

        segment.append((segment_voxel, segment_ske_path))

    return segment, graph

