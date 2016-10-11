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
import sys
import networkx

import alinea.phenomenal.segmentation_3d.algorithm
from alinea.phenomenal.segmentation_3d.peak_detection import peak_detection
from alinea.phenomenal.segmentation_3d.plane_interception import (
    compute_closest_nodes)

from alinea.phenomenal.display import (
    plot_points_3d, show_points_3d, show_list_points_3d, plot_list_points_3d)

from alinea.phenomenal.segmentation_3d.algorithm import (
    graph_skeletonize,
    stem_segmentation,
    merge,
    compute_top_stem_neighbors,
    segment_leaf,
    stem_detection_2)

from alinea.phenomenal.data_structure import voxel_centers_to_image_3d

# ==============================================================================


def maize_base_stem_position_voxel_centers(voxel_centers,
                                           voxel_size,
                                           neighbor_size=5):

    image_3d = voxel_centers_to_image_3d(voxel_centers, voxel_size)

    stem_base_position = maize_base_stem_position_image3d(
        image_3d, neighbor_size=neighbor_size)

    pos = numpy.array(stem_base_position)
    pos = pos * voxel_size + image_3d.world_coordinate

    return pos


def maize_base_stem_position_image3d(image_3d, neighbor_size=5):
    x = int(round(0 - image_3d.world_coordinate[0] / image_3d.voxel_size))
    y = int(round(0 - image_3d.world_coordinate[1] / image_3d.voxel_size))

    k = neighbor_size
    x_len, y_len, z_len = image_3d.shape

    roi = image_3d[max(x - k, 0): min(x + k, x_len),
                   max(y - k, 0): min(y + k, y_len),
                   :]

    xx, yy, zz = numpy.where(roi == 1)
    i = numpy.argmin(zz)

    return x - k + xx[i], y - k + yy[i], zz[i]


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


def maize_stem_segmentation(voxel_centers, voxel_size,
                            distance_plane_1=4,
                            distance_plane_2=0.75,
                            verbose=False):

    # ==========================================================================
    # Build skeleton of plant with graph of shorted path
    graph, biggest_component_voxel_centers, all_shorted_path_down = \
        graph_skeletonize(voxel_centers, voxel_size)

    voxel_not_connected = set(graph.nodes()).difference(
        set(voxel_centers))

    if verbose:
        print("Graph building : done")

    # ==========================================================================
    # Stem Segmentation
    stem_voxel, not_stem_voxel, stem_voxel_path, stem_geometry = \
        stem_segmentation(biggest_component_voxel_centers,
                          all_shorted_path_down,
                          distance_plane_1=distance_plane_1,
                          distance_plane_2=distance_plane_2)

    if verbose:
        print("Stem segmentation done : done")

    # ==========================================================================
    # Merge stem_voxel with this neighbors voxel component if the percentage
    # of neighborhood is superior to percentage=50
    stem_voxel, stem_neighbors, connected_components = merge(
        graph, stem_voxel, not_stem_voxel, percentage=50)

    if verbose:
        print("Merge voxel stem : done")

    # ==========================================================================
    # Group connected components except stem in one group
    not_stem_voxel = voxel_not_connected
    for voxels in connected_components:
        not_stem_voxel = not_stem_voxel.union(voxels)

    not_stem_voxel = not_stem_voxel.union()

    labeled_voxels = dict()
    labeled_voxels["stem"] = stem_voxel
    labeled_voxels["not_stem"] = not_stem_voxel

    return labeled_voxels


def shogun(voxels):
    import mayavi.mlab

    from alinea.phenomenal.display.multi_view_reconstruction import (
        plot_points_3d)

    mayavi.mlab.figure()

    mayavi.mlab.quiver3d(0, 0, 0,
                         100, 0, 0,
                         line_width=5.0,
                         scale_factor=1,
                         color=(1, 0, 0))

    mayavi.mlab.quiver3d(0, 0, 0,
                         0, 100, 0,
                         line_width=5.0,
                         scale_factor=1,
                         color=(0, 1, 0))

    mayavi.mlab.quiver3d(0, 0, 0,
                         0, 0, 100,
                         line_width=5.0,
                         scale_factor=1,
                         color=(0, 0, 1))

    plot_points_3d(
        list(voxels),
        scale_factor=2,
        color=(0.1, 0.9, 0.1))

    mayavi.mlab.show()


def get_neighbors(graph, voxels):

    voxels_neighbors = list()
    for node in voxels:
        voxels_neighbors += graph[node].keys()

    return set(voxels_neighbors) - voxels


def maize_plant_segmentation_3(segments, voxel_size, graph):

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

    stem_voxel, not_stem_voxel, stem_path, stem_top = stem_detection_2(
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

    # print("Number all leaf :", len(real_leaf))
    # Put voxel remain as voxel stem
    stem_voxel = stem_voxel.union(*connected_components)

    # ==========================================================================

    voxels_cornet = set()
    simple_leafs = list()
    simple_leafs_paths = list()

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


def maize_plant_segmentation(voxels_plant, voxel_size,
                             distance_plane_1=4,
                             distance_plane_2=0.75,
                             verbose=False):

    # ==========================================================================
    # Build skeleton of plant with graph of shorted path
    if verbose:
        print "Graph"

    graph, biggest_connected_voxels_plant, skeleton_path = \
        graph_skeletonize(voxels_plant, voxel_size)

    voxel_plant_not_connected = set(graph.nodes()).difference(set(voxels_plant))

    if verbose:
        print "Build Skeleton done"

    # ==========================================================================
    # Stem Segmentation
    stem_voxel, voxels_remain, stem_voxel_path, stem_top = \
        stem_segmentation(
            biggest_connected_voxels_plant,
            skeleton_path,
            distance_plane_1=distance_plane_1,
            distance_plane_2=distance_plane_2)

    stem_voxel, stem_neighbors, connected_components = merge(
        graph, stem_voxel, voxels_remain, percentage=50)

    if verbose:
        print "Stem Segmentation done"

    # ==========================================================================

    stem_top_neighbors = set()
    for node in stem_top:
        stem_top_neighbors = stem_top_neighbors.union(graph[node].keys())
    # stem_top_neighbors = stem_top_neighbors - stem_voxel

    stem_without_top = stem_voxel - stem_top
    stem_without_top_neighbors = set()
    for node in stem_without_top:
        stem_without_top_neighbors = stem_without_top_neighbors.union(
            graph[node].keys())

    # stem_neighbors = set()
    # for node in stem_voxel:
    #     stem_neighbors = stem_neighbors.union(graph[node].keys())

    stem_top_neighbors = stem_top_neighbors - stem_without_top_neighbors

    array_voxels_plant = numpy.array(biggest_connected_voxels_plant)

    # ==========================================================================

    # from alinea.phenomenal.display.multi_view_reconstruction import (
    #     show_list_points_3d)
    #
    # show_list_points_3d([stem_voxel, stem_top_neighbors])

    # ==========================================================================

    simple_leaf = list()
    simple_leaf_path = list()
    voxels_cornet = set()
    connected_leaf = list()

    if verbose:
        print "Number of connected components : ", len(connected_components)

    for i, connected_component in enumerate(connected_components):

        if len(stem_top_neighbors.intersection(connected_component)) > 0:
            voxels_cornet = voxels_cornet.union(connected_component)
        else:
            final_leaf = set()
            final_path = None
            is_same_leaf = True
            remain_leaf = list(connected_component)
            stem_intersection = set()

            all_group = list()
            all_path = list()

            while len(remain_leaf) != 0:

                leaf, remain_leaf, leaf_skeleton_path = segment_leaf(
                    list(remain_leaf), connected_component, skeleton_path,
                    array_voxels_plant, graph, voxel_size,
                    verbose=False)

                all_group.append(leaf)
                all_path.append(leaf_skeleton_path)

                stem_voxel, stem_neighbors, connected_components_remain = merge(
                    graph, stem_voxel, leaf)

                stem_voxel, stem_neighbors, connected_components_remain = merge(
                    graph, stem_voxel, remain_leaf)

                remain_leaf = set().union(*connected_components_remain)

                stem_neighbors = set()
                for node in stem_voxel:
                    stem_neighbors = stem_neighbors.union(graph[node].keys())

                if not stem_intersection:
                    final_leaf = final_leaf.union(leaf)
                    final_path = leaf_skeleton_path
                    stem_intersection = stem_neighbors.intersection(leaf)
                else:

                    if len(stem_neighbors.intersection(leaf)) == \
                            len(stem_intersection):
                        final_leaf = final_leaf.union(leaf)
                    else:
                        is_same_leaf = False
                        break

            if is_same_leaf:
                simple_leaf.append(final_leaf)
                simple_leaf_path.append(final_path)

                # path, distances_max, max_longest, vector = \
                #     extract_data_leaf(final_leaf, final_path)

                # simple_leaf_data.append((path, distances_max, max_longest,
                #                          vector))
            else:
                # from alinea.phenomenal.display.multi_view_reconstruction import (
                #     show_list_points_3d)
                #
                # show_list_points_3d(all_group)
                # show_list_points_3d(all_path)

                connected_leaf.append(connected_component)

    # ==========================================================================

    labeled_voxels = dict()
    labeled_voxels["stem"] = stem_voxel
    labeled_voxels["not_connected"] = voxel_plant_not_connected
    labeled_voxels["cornet"] = voxels_cornet

    labeled_skeleton_path = dict()
    labeled_skeleton_path["stem"] = stem_voxel_path

    for i, (voxels, path) in enumerate(zip(simple_leaf, simple_leaf_path)):
        labeled_voxels["leaf_" + str(i)] = voxels
        labeled_skeleton_path["leaf_" + str(i)] = path

    for i, voxels in enumerate(connected_leaf):
        labeled_voxels["connected_leaf_" + str(i)] = voxels

    return labeled_voxels, labeled_skeleton_path
