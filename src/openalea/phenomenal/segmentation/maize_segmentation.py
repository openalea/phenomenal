# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
from __future__ import print_function, division, absolute_import

import numpy
import networkx

from .maize_stem_detection import stem_detection
from ..object import VoxelOrgan, VoxelSegment, VoxelSegmentation
# ==============================================================================


def _maize_base_stem_position_octree(octree, voxel_size, neighbor_size=5):
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


def _merge(graph, voxels, remaining_voxels, percentage=50):

    voxels_neighbors = list()
    for node in voxels:
        voxels_neighbors += graph[node].keys()
    voxels_neighbors = set(voxels_neighbors) - voxels

    subgraph = graph.subgraph(remaining_voxels)

    connected_components = list()
    for voxel_group in networkx.connected_components(subgraph):
        nb = len(voxel_group.intersection(voxels_neighbors))

        if nb * 100 / len(voxel_group) >= percentage:
            voxels = voxels.union(voxel_group)
        else:
            connected_components.append(voxel_group)

    return voxels, voxels_neighbors, connected_components

# ==============================================================================


def get_highest_segment(segments):
    """ Return the segments with the highest polyline point according to z axis

    Parameters
    ----------
    segments : list
        list of VoxelSegment
    Returns
    -------
    highest_voxel_segment : VoxelSegment
    """
    z_max = float("-inf")
    highest_voxel_segment = None
    for segment in segments:
        z = numpy.max(numpy.array(segment.polyline)[-1, 2])

        if z > z_max:
            z_max = z
            highest_voxel_segment = segment

    return highest_voxel_segment


def maize_segmentation(voxel_skeleton, graph):
    """ Labeling segments in voxel_skeleton into 4 label.
    The label are "stem", "growing leaf", "mature_leaf", "unknown".
    Parameters
    ----------
    voxel_skeleton : openalea.phenomenal.object.VoxelSkeleton
    graph : networkx.Graph

    Returns
    -------
    vms : VoxelSegmentation
    """

    # ==========================================================================
    # Select the more highest segment on the skeleton
    voxels_size = voxel_skeleton.voxels_size

    highest_voxel_segment = get_highest_segment(voxel_skeleton.segments)

    stem_segment_voxel = highest_voxel_segment.voxels_position
    stem_segment_path = highest_voxel_segment.polyline

    # ==========================================================================
    # Compute Stem detection
    stem_voxel, not_stem_voxel, stem_path, stem_top = stem_detection(
        stem_segment_voxel, stem_segment_path, voxels_size, graph)

    # ==========================================================================
    # Remove stem voxels from segment voxels
    vs_to_remove = list()
    for vs in voxel_skeleton.segments:

        leaf_voxel = None
        subgraph = graph.subgraph(vs.voxels_position - stem_voxel)
        for voxel_group in networkx.connected_components(subgraph):
            if vs.polyline[-1] in voxel_group:
                leaf_voxel = voxel_group
        vs.leaf_voxel = leaf_voxel

        if leaf_voxel is None:
            vs_to_remove.append(vs)
            continue

        # ======================================================================

        index_position_tip = -1
        index_position_base = len(vs.polyline) - 1
        for i in range(len(vs.polyline) - 1, -1, -1):
            if vs.polyline[i] not in set(vs.leaf_voxel):
                index_position_base = i
                break

        vs.real_polyline = vs.polyline[index_position_base:index_position_tip]

    for vs in vs_to_remove:
        voxel_skeleton.segments.remove(vs)

    # ==========================================================================
    # Merge remains voxels of the not stem
    for vs in voxel_skeleton.segments:
        not_stem_voxel -= vs.leaf_voxel

    voxels_remain = not_stem_voxel

    # ==========================================================================
    # Define mature & cornet leaf

    organ_unknown = VoxelOrgan("unknown")
    organ_unknown.add_voxel_segment(voxels_remain, list())

    mature_organs, growing_organs = list(), list()
    for vs in voxel_skeleton.segments:

        if len(vs.real_polyline) == 0:
            organ_unknown.voxel_segments.append(vs.copy())
            continue

        vs = VoxelSegment(vs.polyline, vs.leaf_voxel, vs.closest_nodes)

        if len(stem_top.intersection(vs.polyline)) > 0:
            vo = VoxelOrgan("growing_leaf")
            vo.voxel_segments.append(vs)
            growing_organs.append(vo)
        else:
            vo = VoxelOrgan("mature_leaf")
            vo.voxel_segments.append(vs)
            mature_organs.append(vo)

    # ==========================================================================
    # MERGE MATURE LEAFS
    # ==========================================================================
    percentage = 50
    ltmp = list()
    while mature_organs:
        vo_1 = mature_organs.pop()
        again = True
        while again:

            voxels_1 = vo_1.voxels_position()
            real_polyline_1 = set(vo_1.real_longest_polyline())

            again = False
            for i, vo_2 in enumerate(mature_organs):
                voxels_2 = vo_2.voxels_position()
                real_polyline_2 = set(vo_2.real_longest_polyline())

                val_1 = len(real_polyline_1.intersection(voxels_2))
                val_1 = val_1 * 100 / len(real_polyline_1)

                val_2 = len(real_polyline_2.intersection(voxels_1))
                val_2 = val_2 * 100 / len(real_polyline_2)

                if (val_1 >= percentage) or (val_2 >= percentage):
                    vo_1.voxel_segments += vo_2.voxel_segments
                    mature_organs.pop(i)
                    again = True
                    break

        ltmp.append(vo_1)
    mature_organs = ltmp

    # ==========================================================================
    # DETECT CONNECTED LEAFS
    # ==========================================================================
    for i, vo_1 in enumerate(mature_organs):
        for j, vo_2 in enumerate(mature_organs):
            if i == j:
                continue

            nodes = vo_1.voxels_position().intersection(vo_2.voxels_position())
            v = networkx.number_connected_components(graph.subgraph(nodes))
            if v > 1:
                vo_1.sub_label = "connected"


    # ==========================================================================
    # MERGE GROWING LEAFS
    # ==========================================================================
    percentage = 85
    ltmp = list()
    while growing_organs:
        vo_1 = growing_organs.pop()
        again = True
        while again:

            voxels_1 = vo_1.voxels_position()
            real_polyline_1 = set(vo_1.real_longest_polyline())

            again = False
            for i, vo_2 in enumerate(growing_organs):
                voxels_2 = vo_2.voxels_position()
                real_polyline_2 = set(vo_2.real_longest_polyline())

                val_1 = len(real_polyline_1.intersection(voxels_2))
                val_1 = val_1 * 100 / len(real_polyline_1)

                val_2 = len(real_polyline_2.intersection(voxels_1))
                val_2 = val_2 * 100 / len(real_polyline_2)

                nb = len(voxels_1.intersection(voxels_2))
                val_3 = nb * 100 / len(voxels_2)
                val_4 = nb * 100 / len(voxels_1)

                if ((val_1 >= percentage or val_2 >= percentage) and
                        (val_3 >= percentage or val_4 >= percentage)):

                    vo_1.voxel_segments += vo_2.voxel_segments
                    growing_organs.pop(i)
                    again = True
                    break

        ltmp.append(vo_1)

    growing_organs = ltmp

    # ==========================================================================
    ## Build the object to return

    vms = VoxelSegmentation(voxels_size)
    vms.voxel_organs.append(organ_unknown)

    organ_stem = VoxelOrgan("stem")
    organ_stem.add_voxel_segment(stem_voxel, stem_path)
    vms.voxel_organs.append(organ_stem)

    for leaf_organ in growing_organs + mature_organs:
        vms.voxel_organs.append(leaf_organ)

    return vms
