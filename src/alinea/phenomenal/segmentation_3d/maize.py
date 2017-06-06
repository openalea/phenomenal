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
    merge, stem_detection)

from alinea.phenomenal.data_structure import (
    VoxelSkeleton,
    VoxelOrgan,
    VoxelMaizeSegmentation)

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
        z = numpy.max(numpy.array(voxel_segment.polyline)[:, 2])

        if z > z_max:
            z_max = z
            highest_voxel_segment = voxel_segment

    return highest_voxel_segment


def labelize_maize_skeleton(voxel_skeleton, voxel_graph):

    # ==========================================================================
    # Select the more highest segment on the skeleton

    graph = voxel_graph.graph
    voxels_size = voxel_graph.voxels_size

    highest_voxel_segment = get_highest_segment(voxel_skeleton.voxel_segments)

    stem_segment_voxel = highest_voxel_segment.voxels_position
    stem_segment_path = highest_voxel_segment.polyline


    # ==========================================================================
    from alinea.phenomenal.display import (
        show_list_voxels)

    show_list_voxels([stem_segment_voxel, stem_segment_path], [8, 8])

    # ==========================================================================
    # Fusion little segment close to the stem to the stem

    tmp_segments = list()
    for voxel_segment in voxel_skeleton.voxel_segments:

        voxels_position = voxel_segment.voxels_position
        polyline = voxel_segment.polyline

        supposed_leaf_voxels = voxels_position - stem_segment_voxel

        leaf_path = set(polyline).intersection(supposed_leaf_voxels)

        if len(leaf_path) == 0:
            stem_segment_voxel = stem_segment_voxel.union(supposed_leaf_voxels)
        else:

            leaf_voxel = None
            subgraph = graph.subgraph(voxels_position)

            i = -1
            while leaf_voxel is None:
                for voxels_group in networkx.connected_components(subgraph):
                    if polyline[i] in voxels_group:
                        leaf_voxel = voxels_group
                i -= 1

            neighbors = get_neighbors(graph, leaf_voxel)
            stem_neighbors = neighbors.intersection(stem_segment_voxel)
            tmp_segments.append((leaf_voxel, polyline, stem_neighbors))

    # ==========================================================================
    # Fusion segments if is have at least 1 voxels stem neighbors in common
    tmp_leafs = list()
    while tmp_segments:
        segment_voxel, segment_path, stem_neighbors = tmp_segments.pop()

        paths = [segment_path]

        again = True
        while again:
            again = False
            for i, (segment_voxel_2, segment_path_2, stem_neighbors_2) in \
                    enumerate(tmp_segments):

                if (stem_neighbors.intersection(stem_neighbors_2) and
                        segment_voxel.intersection(segment_voxel_2)):
                    segment_voxel = segment_voxel.union(segment_voxel_2)
                    stem_neighbors = stem_neighbors.union(stem_neighbors_2)
                    paths.append(segment_path_2)
                    tmp_segments.pop(i)
                    again = True
                    break

        tmp_leafs.append((segment_voxel, paths))

    # ==========================================================================
    # Compute Stem detection

    stem_voxel, not_stem_voxel, stem_path, stem_top = stem_detection(
        stem_segment_voxel, stem_segment_path, tmp_leafs, voxels_size)

    # stem_voxel, stem_neighbors, connected_components = merge(
    #     graph, stem_voxel, not_stem_voxel, percentage=50)

    # show_list_points_3d([all_voxels, stem_voxel],
    #                     list_color=[(0.1, 0.9, 0.1),
    #                                 (0.1, 0.1, 0.1)],
    #                     list_scale_factor=[voxels_size,
    #                                        voxels_size],
    #                     size=(5000, 5000),
    #                     azimuth=310,
    #                     distance=2000,
    #                     elevation=90,
    #                     focalpoint=(0, 0, -250))

    # ==========================================================================
    # Compute Stem top neighbors

    stem_top_neighbors = set()
    for node in stem_top:
        stem_top_neighbors = stem_top_neighbors.union(graph[node].keys())

    stem_without_top = stem_voxel - stem_top
    stem_without_top_neighbors = set()
    for node in stem_without_top:
        stem_without_top_neighbors = stem_without_top_neighbors.union(
            graph[node].keys())

    stem_top_neighbors = stem_top_neighbors - stem_without_top_neighbors

    # ==========================================================================
    # Remove stem voxel from voxel segments

    for vs in voxel_skeleton.voxel_segments:

        leaf_voxel = None
        subgraph = graph.subgraph(vs.voxels_position - stem_voxel)
        for voxel_group in networkx.connected_components(subgraph):
            if vs.polyline[-1] in voxel_group:
                leaf_voxel = voxel_group

        vs.leaf_voxel = leaf_voxel

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

    mature_organs = list()
    cornet_organs = list()
    for vs in voxel_skeleton.voxel_segments:
        if len(stem_top_neighbors.intersection(vs.leaf_voxel)) > 0:
            vo = VoxelOrgan("cornet_leaf")
            vo.voxel_segments.append(vs)
            cornet_organs.append(vo)
        else:
            vo = VoxelOrgan("mature_leaf")
            vo.voxel_segments.append(vs)
            mature_organs.append(vo)

    # ==========================================================================
    # MERGE LEAF MATURE
    # ==========================================================================

    percentage = 50
    ltmp = list()
    while mature_organs:

        vo_1 = mature_organs.pop()
        voxels_1 = vo_1.voxels_position()

        again = True
        while again:
            again = False
            for i, vo_2 in enumerate(mature_organs):
                voxels_2 = vo_2.voxels_position()

                nb = len(voxels_1.intersection(voxels_2))

                if ((nb * 100 / len(voxels_1) >= percentage) or
                    (nb * 100 / len(voxels_2) >= percentage)):

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
        voxels_1 = vo_1.voxels_position()

        again = True
        while again:
            again = False
            for i, vo_2 in enumerate(cornet_organs):
                voxels_2 = vo_2.voxels_position()

                nb = len(voxels_1.intersection(voxels_2))

                if ((nb * 100 / len(voxels_1) >= percentage) or
                    (nb * 100 / len(voxels_2) >= percentage)):

                    vo_1.voxel_segments += vo_2.voxel_segments

                    cornet_organs.pop(i)
                    again = True
                    break

        ltmp.append(vo_1)

    cornet_organs = ltmp

    # ==========================================================================

    vms = VoxelMaizeSegmentation(voxels_size)

    organ_unknown = VoxelOrgan("unknown")
    organ_unknown.add_voxel_segment(voxels_remain, list())
    vms.voxel_organs.append(organ_unknown)

    organ_stem = VoxelOrgan("stem")
    organ_stem.add_voxel_segment(stem_voxel, stem_path)
    vms.voxel_organs.append(organ_stem)

    for leaf_organ in cornet_organs:
        vms.voxel_organs.append(leaf_organ)

    for leaf_organ in mature_organs:
        vms.voxel_organs.append(leaf_organ)

    # ==========================================================================

    return vms
