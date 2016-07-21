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
    stem_segmentation,
    merge,
    compute_top_stem_neighbors,
    extract_data_leaf,
    segment_leaf)

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

    roi = image_3d[
          max(x - k, 0): min(x + k, x_len),
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
                            distance_plane_2=0.75):

    graph, new_voxel_centers, all_shorted_path_down, origin = graph_skeletonize(
        voxel_centers, voxel_size)

    # ==========================================================================
    stem_voxel, not_stem_voxel, stem_voxel_path, stem_geometry = \
        stem_segmentation(new_voxel_centers, all_shorted_path_down,
                          distance_plane_1=distance_plane_1,
                          distance_plane_2=distance_plane_2)

    stem_voxel, stem_neighbors, connected_components = merge(
        graph, stem_voxel, not_stem_voxel, percentage=50)

    not_stem_voxel = set()
    for voxels in connected_components:
        not_stem_voxel = not_stem_voxel.union(voxels)

    stem_voxel = (numpy.array(list(stem_voxel)) * voxel_size) + origin
    stem_voxel = map(tuple, list(stem_voxel))

    not_stem_voxel = (numpy.array(list(not_stem_voxel)) * voxel_size) + origin
    not_stem_voxel = map(tuple, list(not_stem_voxel))

    return stem_voxel, not_stem_voxel


def maize_plant_segmentation(voxel_centers, voxel_size,
                             verbose=False):

    graph, new_voxel_centers, all_shorted_path_down, origin = graph_skeletonize(
        voxel_centers, voxel_size)

    # ==========================================================================
    stem_voxel, not_stem_voxel, stem_voxel_path, stem_geometry = \
        stem_segmentation(new_voxel_centers, all_shorted_path_down)

    nvc = set(map(tuple, list(new_voxel_centers)))

    top_stem_neighbors = compute_top_stem_neighbors(nvc, graph, stem_geometry)

    stem_voxel, stem_neighbors, connected_components = merge(
        graph, stem_voxel, not_stem_voxel, percentage=50)

    # ==========================================================================

    if verbose:
        print "Stem Segmentation done :"
        print "Size Stem :", len(stem_voxel)
        print "Number of connected components :", len(connected_components)

    # ==========================================================================

    simple_leaf = list()
    simple_leaf_data = list()
    corners = list()
    connected_leaf = list()

    for connected_component in connected_components:

        if len(top_stem_neighbors.intersection(connected_component)) > 0:
            corners.append(connected_component)
        else:

            leaf, left, stem_voxel, longest_shortest_path = segment_leaf(
                list(connected_component), connected_component,
                all_shorted_path_down, new_voxel_centers,
                stem_voxel, stem_neighbors, graph, voxel_size, verbose=False)

            # skeletonize.append(longest_shortest_path)

            if len(left) == 0:
                simple_leaf.append(leaf)

                path, distances_max, max_longest, vector = extract_data_leaf(
                    leaf, longest_shortest_path)

                simple_leaf_data.append((path, distances_max, max_longest,
                                         vector))

            else:
                # not_simple_leaf.append(connected_component)

                stem_connection = stem_neighbors.intersection(leaf)
                same = len(stem_connection)

                big_leaf = list()
                is_same_leaf = True
                while len(left) != 0:

                    # TODO : update stem neighbors
                    leaf, left, stem_voxel, _ = segment_leaf(
                        list(left), connected_component, all_shorted_path_down,
                        new_voxel_centers,
                        stem_voxel, stem_neighbors, graph, voxel_size,
                        verbose=False)

                    if len(stem_neighbors.intersection(leaf)) != same:
                        is_same_leaf = False
                        break
                    else:
                        big_leaf += list(leaf)

                        # skeletonize.append(longest_shortest_path)

                if is_same_leaf is True:
                    simple_leaf.append(set(big_leaf))

                    path, distances_max, max_longest, vector = \
                        extract_data_leaf(big_leaf,
                                          longest_shortest_path,
                                          verbose=False)

                    simple_leaf_data.append((path, distances_max, max_longest,
                                             vector))

                else:
                    connected_leaf.append(connected_component)

    return stem_voxel, simple_leaf, simple_leaf_data, connected_leaf, corners