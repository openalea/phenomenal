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


def labelize_maize_skeleton(voxel_skeleton, voxel_graph):

    # ==========================================================================
    # Stem segment attribution

    graph = voxel_graph.graph
    voxels_size = voxel_graph.voxels_size
    segments = list()
    for voxel_segment in voxel_skeleton.voxel_segments:
        segments.append((voxel_segment.voxels_position,
                         voxel_segment.polylines[0]))

    z_max = float("-inf")
    stem_segment = None
    for voxels, path in segments:

        z = numpy.max(numpy.array(path)[:, 2])

        if z > z_max:
            z_max = z
            stem_segment = voxels, path

    # all_voxels = set().union(*[voxels for voxels, path in segments])
    # all_paths = set().union(*[path for voxels, path in segments])

    segments.remove(stem_segment)
    stem_segment_voxel, stem_segment_path = stem_segment

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
    for voxels, path in segments:
        supposed_leaf_voxels = voxels - stem_segment_voxel
        leaf_path = set(path).intersection(supposed_leaf_voxels)

        if len(leaf_path) == 0:
            stem_segment_voxel = stem_segment_voxel.union(supposed_leaf_voxels)
        else:
            tmp_segments.append((voxels, path))
    segments = tmp_segments

    # ==========================================================================
    # Fusion leaf

    # 1. Remove stem voxel to voxels segments
    # 2. Compute subgraph of the result
    # 3. Kept the connected components with the last position of the path is
    # in that
    # 4. Compute the Stem neighbors of this voxels

    new_segments = list()
    for voxels, path in segments:
        supposed_leaf_voxels = voxels - stem_segment_voxel

        leaf_voxel = None
        subgraph = graph.subgraph(supposed_leaf_voxels)
        i = -1
        while leaf_voxel is None:
            for voxels_group in networkx.connected_components(subgraph):
                if path[i] in voxels_group:
                    leaf_voxel = voxels_group
            i -= 1

        neighbors = get_neighbors(graph, leaf_voxel)
        stem_neighbors = neighbors.intersection(stem_segment_voxel)
        new_segments.append((voxels, path, stem_neighbors))

    # print len(new_segments)

    # Fusion segments if is have at least 1 voxels stem neighbors in common
    # TODO : BUG HERE don't do that for cornet voxels
    leafs = list()
    while new_segments:
        segment_voxel, segment_path, stem_neighbors = \
            new_segments.pop()

        paths = [segment_path]

        again = True
        while again:
            again = False
            for i, (segment_voxel_2, segment_path_2, stem_neighbors_2) in \
                    enumerate(new_segments):

                if stem_neighbors.intersection(stem_neighbors_2):
                    segment_voxel = segment_voxel.union(segment_voxel_2)
                    stem_neighbors = stem_neighbors.union(stem_neighbors_2)
                    paths.append(segment_path_2)
                    new_segments.pop(i)
                    again = True
                    break

        leafs.append((segment_voxel, paths))

    # ==========================================================================
    # Compute Stem detection

    stem_voxel, not_stem_voxel, stem_path, stem_top = stem_detection(
        stem_segment_voxel, stem_segment_path, leafs, voxels_size)

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

    stem_top_neighbors = set()
    for node in stem_top:
        stem_top_neighbors = stem_top_neighbors.union(graph[node].keys())
    # stem_top_neighbors = stem_neighbors - stem_voxel

    stem_without_top = stem_voxel - stem_top
    stem_without_top_neighbors = set()
    for node in stem_without_top:
        stem_without_top_neighbors = stem_without_top_neighbors.union(
            graph[node].keys())

    stem_top_neighbors = stem_top_neighbors - stem_without_top_neighbors

    # ==========================================================================
    # Take back the leaf segment from original stem_segment

    real_leaf = list()
    result = stem_segment_voxel - stem_voxel
    leaf_voxel = None
    subgraph = graph.subgraph(result)
    for voxel_group in networkx.connected_components(subgraph):
        if stem_segment_path[-1] in voxel_group:
            leaf_voxel = voxel_group

    if leaf_voxel is not None:
        real_leaf.append((leaf_voxel, [stem_segment_path]))

    # Get the real leaf by remove real stem_voxel compute to the segment voxel
    for segment_voxel, paths in leafs:
        result = segment_voxel - stem_voxel

        leaf_voxel = None
        subgraph = graph.subgraph(result)
        for voxel_group in networkx.connected_components(subgraph):
            if paths[0][-1] in voxel_group:
                leaf_voxel = voxel_group

        real_leaf.append((leaf_voxel, paths))

    # ==========================================================================

    for leaf, paths in real_leaf:
        not_stem_voxel = not_stem_voxel - leaf

    stem_voxel, stem_neighbors, connected_components = merge(
        graph, stem_voxel, not_stem_voxel, percentage=50)

    for i, (leaf, paths) in enumerate(real_leaf):
        l, _, connected_components = merge(
            graph, leaf, set().union(*connected_components), percentage=50)

        real_leaf[i] = (l, paths)

    voxels_remain = set().union(*connected_components)

    # ==========================================================================

    vss = VoxelSkeleton()
    vss.add_voxel_segment(voxels_remain, voxels_size, list(), "unknown")
    vss.add_voxel_segment(stem_voxel, voxels_size, [stem_path], "stem")

    for leaf, paths in real_leaf:

        if len(stem_top_neighbors.intersection(leaf)) > 0:
            label = "cornet_leaf"
        else:
            label = "mature_leaf"

        vss.add_voxel_segment(leaf, voxels_size, paths, label)

    # ==========================================================================

    # TODO :  put voxel intersection in the nearest neighbors

    # for i in range(len(simple_leafs)):
    #     r = simple_leafs[i].intersection(voxels_cornet)
    #     simple_leafs[i] = simple_leafs[i] - r

    # ==========================================================================

    return vss
