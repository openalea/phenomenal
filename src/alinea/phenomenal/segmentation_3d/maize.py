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


def maize_plant_segmentation(segments, voxel_size, graph):

    # ==========================================================================
    # Stem segment attribution

    z_max = float("-inf")
    stem_segment = None
    for voxels, path in segments:

        z = numpy.max(numpy.array(path)[:, 2])

        if z > z_max:
            z_max = z
            stem_segment = voxels, path

    segments.remove(stem_segment)
    stem_segment_voxel, stem_segment_path = stem_segment

    # show_points_3d(stem_segment_voxel)
    # show_list_points_3d([voxels - stem_segment_voxel for voxels, _ in segments])

    # ==========================================================================
    # Fusion leaf

    new_segments = list()
    for segment_voxel, segment_path in segments:
        result = segment_voxel - stem_segment_voxel

        leaf_voxel = None
        subgraph = graph.subgraph(result)
        i = -1
        while leaf_voxel is None:
            for voxel_group in networkx.connected_components(subgraph):
                if segment_path[i] in voxel_group:
                    leaf_voxel = voxel_group
            i -= 1

        neighbors = get_neighbors(graph, leaf_voxel)
        stem_neighbors = neighbors.intersection(stem_segment_voxel)
        new_segments.append((segment_voxel, segment_path, stem_neighbors))

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

    stem_voxel, not_stem_voxel, stem_path, stem_top = stem_detection(
        stem_segment_voxel, stem_segment_path, leafs, voxel_size)

    # stem_voxel, stem_neighbors, connected_components = merge(
    #     graph, stem_voxel, not_stem_voxel, percentage=50)

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
    real_leaf = list()

    result = stem_segment_voxel - stem_voxel
    leaf_voxel = None
    subgraph = graph.subgraph(result)
    for voxel_group in networkx.connected_components(subgraph):
        if stem_segment_path[-1] in voxel_group:
            leaf_voxel = voxel_group

    real_leaf.append((leaf_voxel, [stem_segment_path]))

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

    stem_voxel = stem_voxel.union(*connected_components)

    # ==========================================================================

    segments = list()
    stem_dict = dict()
    stem_dict["voxel"] = stem_voxel
    stem_dict["paths"] = [stem_path]
    stem_dict["label"] = "stem"
    segments.append(stem_dict)

    i = 0
    for leaf, paths in real_leaf:

        leaf_dict = dict()
        leaf_dict["voxel"] = leaf
        leaf_dict["paths"] = paths

        if len(stem_top_neighbors.intersection(leaf)) > 0:
            leaf_dict["label"] = "cornet_leaf_" + str(i)
        else:
            leaf_dict["label"] = "mature_leaf_" + str(i)

        i += 1

        segments.append(leaf_dict)

    # ==========================================================================

    # TODO :  put voxel intersection in the nearest neighbors

    # for i in range(len(simple_leafs)):
    #     r = simple_leafs[i].intersection(voxels_cornet)
    #     simple_leafs[i] = simple_leafs[i] - r

    # ==========================================================================

    return segments
