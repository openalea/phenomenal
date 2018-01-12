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

from .maize_stem_detection import stem_detection
import openalea.phenomenal.object.voxelOrgan
import openalea.phenomenal.object.voxelSegmentation

# ==============================================================================


def maize_base_stem_position_octree(octree, voxel_size, neighbor_size=5):
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


def get_neighbors(graph, voxels):

    voxels_neighbors = list()
    for node in voxels:
        voxels_neighbors += graph[node].keys()

    return set(voxels_neighbors) - voxels


def get_highest_segment(voxel_segments):

    z_max = float("-inf")
    highest_voxel_segment = None
    for voxel_segment in voxel_segments:
        z = numpy.max(numpy.array(voxel_segment.polyline)[-1, 2])

        if z > z_max:
            z_max = z
            highest_voxel_segment = voxel_segment

    return highest_voxel_segment


def merge(graph, voxels, remaining_voxels, percentage=50):

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


def labelize_maize_skeleton(voxel_skeleton, voxel_graph):

    # ==========================================================================
    # Select the more highest segment on the skeleton

    graph = voxel_graph.graph
    voxels_size = voxel_graph.voxels_size

    highest_voxel_segment = get_highest_segment(voxel_skeleton.voxel_segments)

    stem_segment_voxel = highest_voxel_segment.voxels_position
    stem_segment_path = highest_voxel_segment.polyline

    # ==========================================================================
    # Compute Stem detection

    stem_voxel, not_stem_voxel, stem_path, stem_top = stem_detection(
        stem_segment_voxel, stem_segment_path, voxels_size,
        graph=graph)

    # ==========================================================================
    # Remove stem voxels from segment voxels

    for vs in voxel_skeleton.voxel_segments:

        leaf_voxel = None
        subgraph = graph.subgraph(vs.voxels_position - stem_voxel)
        for voxel_group in networkx.connected_components(subgraph):
            if vs.polyline[-1] in voxel_group:
                leaf_voxel = voxel_group
        vs.leaf_voxel = leaf_voxel

        # ======================================================================

        index_position_tip = -1
        index_position_base = len(vs.polyline) - 1
        for i in range(len(vs.polyline) - 1, -1, -1):
            if vs.polyline[i] not in set(vs.leaf_voxel):
                index_position_base = i
                break

        vs.real_polyline = vs.polyline[index_position_base:index_position_tip]

    # ==========================================================================
    # Merge remains voxels of the not stem

    for vs in voxel_skeleton.voxel_segments:
        not_stem_voxel -= vs.leaf_voxel

    stem_voxel, stem_neighbors, connected_components = merge(
        graph, stem_voxel, not_stem_voxel, percentage=50)

    for vs in voxel_skeleton.voxel_segments:
        vs.leaf_voxel, _, connected_components = merge(
            graph, vs.leaf_voxel, set().union(*connected_components),
            percentage=50)

    voxels_remain = set().union(*connected_components)

    # ==========================================================================
    # Define mature & cornet leaf

    organ_unknown = openalea.phenomenal.object.VoxelOrgan("unknown")
    organ_unknown.add_voxel_segment(voxels_remain, list())

    mature_organs = list()
    cornet_organs = list()
    for vs in voxel_skeleton.voxel_segments:

        if len(vs.real_polyline) * voxels_size <= 30:
            organ_unknown.voxel_segments.append(vs)
            continue

        if len(stem_top.intersection(vs.polyline)) > 0:
            vo = openalea.phenomenal.object.VoxelOrgan("cornet_leaf")
            vs.voxels_position = vs.leaf_voxel

            vo.voxel_segments.append(vs)
            cornet_organs.append(vo)
        else:
            vo = openalea.phenomenal.object.VoxelOrgan("mature_leaf")
            vs.voxels_position = vs.leaf_voxel

            vo.voxel_segments.append(vs)
            mature_organs.append(vo)

    # ==========================================================================
    # MERGE LEAF MATURE
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
    # MERGE LEAF CORNET
    # ==========================================================================
    percentage = 85
    ltmp = list()
    while cornet_organs:
        vo_1 = cornet_organs.pop()
        again = True
        while again:

            voxels_1 = vo_1.voxels_position()
            real_polyline_1 = set(vo_1.real_longest_polyline())

            again = False
            for i, vo_2 in enumerate(cornet_organs):
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
                    cornet_organs.pop(i)
                    again = True
                    break

        ltmp.append(vo_1)

    cornet_organs = ltmp

    # ==========================================================================
    ## build the object to return

    vms = openalea.phenomenal.object.VoxelSegmentation(voxels_size)
    vms.voxel_organs.append(organ_unknown)

    organ_stem = openalea.phenomenal.object.VoxelOrgan("stem")
    organ_stem.add_voxel_segment(stem_voxel, stem_path)
    vms.voxel_organs.append(organ_stem)

    for leaf_organ in cornet_organs:
        vms.voxel_organs.append(leaf_organ)

    for leaf_organ in mature_organs:
        vms.voxel_organs.append(leaf_organ)

    return vms
