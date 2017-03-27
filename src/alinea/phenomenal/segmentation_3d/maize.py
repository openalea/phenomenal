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

from alinea.phenomenal.data_structure.voxelSkeleton import VoxelSkeleton

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
        z = numpy.max(numpy.array(voxel_segment.polylines[0])[:, 2])

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
    stem_segment_path = highest_voxel_segment.polylines[0]


    # ==========================================================================
    # from alinea.phenomenal.display.multi_view_reconstruction import (
    #     show_list_points_3d)
    #
    # show_list_points_3d([all_voxels, all_paths, stem_segment_path],
    #                     list_color=[(0.1, 0.9, 0.1),
    #                                 (0.9, 0.1, 0.1),
    #                                 (0.1, 0.1, 0.9)],
    #                     list_scale_factor=[voxels_size * 0.25,
    #                                        voxels_size,
    #                                        voxels_size],
    #                     size=(5000, 5000),
    #                     azimuth=310,
    #                     distance=2000,
    #                     elevation=90,
    #                     focalpoint=(0, 0, -250))
    #
    # show_list_points_3d([all_voxels, all_paths,
    #                      stem_segment_voxel,
    #                      stem_segment_path],
    #                     list_color=[(0.1, 0.9, 0.1),
    #                                 (0.9, 0.1, 0.1),
    #                                 (0.1, 0.1, 0.9),
    #                                 (0.1, 0.1, 0.9)],
    #                     list_scale_factor=[voxels_size * 0.25,
    #                                        voxels_size,
    #                                        voxels_size * 0.25,
    #                                        voxels_size],
    #                     size=(5000, 5000),
    #                     azimuth=310,
    #                     distance=2000,
    #                     elevation=90,
    #                     focalpoint=(0, 0, -250))

    # ==========================================================================
    # Fusion little segment close to the stem to the stem

    tmp_segments = list()
    for voxel_segment in voxel_skeleton.voxel_segments:

        voxels_position = voxel_segment.voxels_position
        polyline = voxel_segment.polylines[0]
        voxels_size = voxel_segment.voxels_size

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
    # Remove

    real_leaf = list()
    for voxel_segment in voxel_skeleton.voxel_segments:

        voxels_position = voxel_segment.voxels_position
        polylines = voxel_segment.polylines
        voxels_size = voxel_segment.voxels_size

        leaf_voxel = None
        subgraph = graph.subgraph(voxels_position - stem_voxel)
        for voxel_group in networkx.connected_components(subgraph):
            if polylines[0][-1] in voxel_group:
                leaf_voxel = voxel_group

        if leaf_voxel is not None:
            real_leaf.append((leaf_voxel, polylines))

    # ==========================================================================
    # Merge voxels

    for voxels_position, polylines in real_leaf:
        not_stem_voxel -= voxels_position

    stem_voxel, stem_neighbors, connected_components = merge(
        graph, stem_voxel, not_stem_voxel, percentage=50)

    for i, (leaf, paths) in enumerate(real_leaf):
        l, _, connected_components = merge(
            graph, leaf, set().union(*connected_components), percentage=50)

        real_leaf[i] = (l, paths)

    voxels_remain = set().union(*connected_components)
    # ==========================================================================
    leaf_mature, leaf_cornet = list(), list()

    for leaf, polylines in real_leaf:
        if len(stem_top_neighbors.intersection(leaf)) > 0:
            leaf_cornet.append((leaf, polylines))
        else:
            leaf_mature.append((leaf, polylines))

    # ==========================================================================
    new_segments = list()
    for voxels_position, polylines in leaf_mature:
        neighbors = get_neighbors(graph, voxels_position)
        stem_neighbors = neighbors.intersection(stem_segment_voxel)
        new_segments.append((voxels_position, polylines, stem_neighbors))

    percentage = 50
    leafs = list()
    while new_segments:
        segment_voxel, polylines, stem_neighbors = new_segments.pop()

        again = True
        while again:
            again = False
            for i, (segment_voxel_2, polylines_2, stem_neighbors_2) in \
                    enumerate(new_segments):

                nb = len(segment_voxel.intersection(segment_voxel_2))

                if (stem_neighbors.intersection(stem_neighbors_2) and (
                        (nb * 100 / len(segment_voxel) >= percentage) or
                        (nb * 100 / len(segment_voxel_2) >= percentage))):

                    segment_voxel = segment_voxel.union(segment_voxel_2)
                    stem_neighbors = stem_neighbors.union(stem_neighbors_2)
                    polylines += polylines_2
                    new_segments.pop(i)
                    again = True
                    break

        leafs.append((segment_voxel, polylines))

    leaf_mature = leafs
    # ==========================================================================
    # ==========================================================================
    new_segments = list()
    for voxels_position, polylines in leaf_cornet:
        new_segments.append((voxels_position, polylines))

    percentage = 85
    leafs = list()
    while new_segments:
        segment_voxel, polylines = new_segments.pop()

        again = True
        while again:
            again = False
            for i, (segment_voxel_2, polylines_2) in enumerate(new_segments):

                nb = len(segment_voxel.intersection(segment_voxel_2))

                if ((nb * 100 / len(segment_voxel) >= percentage) or
                    (nb * 100 / len(segment_voxel_2) >= percentage)):

                    segment_voxel = segment_voxel.union(segment_voxel_2)
                    polylines += polylines_2
                    new_segments.pop(i)
                    again = True
                    break

        leafs.append((segment_voxel, polylines))

    leaf_cornet = leafs
    # ==========================================================================

    vss = VoxelSkeleton()
    vss.add_voxel_segment(voxels_remain, voxels_size, list(), "unknown")
    vss.add_voxel_segment(stem_voxel, voxels_size, [stem_path], "stem")

    for leaf, polylines in leaf_cornet:
        vss.add_voxel_segment(leaf, voxels_size, polylines, "cornet_leaf")

    for leaf, polylines in leaf_mature:
        vss.add_voxel_segment(leaf, voxels_size, polylines, "mature_leaf")

    # ==========================================================================

    return vss
