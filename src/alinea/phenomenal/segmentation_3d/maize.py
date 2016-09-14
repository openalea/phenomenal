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

import alinea.phenomenal.segmentation_3d.algorithm
from alinea.phenomenal.segmentation_3d.peak_detection import peak_detection
from alinea.phenomenal.segmentation_3d.plane_interception import (
    compute_closest_nodes)


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


def maize_plant_segmentation_2(voxel_centers, voxel_size,
                               distance_plane_1=2,
                               distance_plane_2=0.75,
                               verbose=False):

    # ==========================================================================
    # Build skeleton of plant with graph of shorted path
    graph, biggest_component_voxel_centers, all_shorted_path = \
        graph_skeletonize(voxel_centers, voxel_size)

    arr_voxels_plants = numpy.array(biggest_component_voxel_centers)
    set_voxels_plant = set(biggest_component_voxel_centers)
    set_voxels_plant_not_connected = set_voxels_plant.difference(
        set(voxel_centers))

    stem_voxel_path, closest_nodes = alinea.phenomenal.segmentation_3d.\
        algorithm.segment_stem(biggest_component_voxel_centers,
                               all_shorted_path,
                               distance_plane_1=distance_plane_1)

    def get_max_distance(node, nodes):
        max_distance = 0
        max_node = node

        for n in nodes:
            distance = numpy.linalg.norm(numpy.array(node) - numpy.array(n))
            max_distance = max(max_distance, distance)
            max_node = n

        return max_node, max_distance

    distances = list()
    for i in range(len(closest_nodes)):
        nodes = closest_nodes[i]

        pt1, _ = get_max_distance(nodes[0], nodes)
        pt2, distance = get_max_distance(pt1, nodes)

        distances.append(float(distance) / float(voxel_size))

    values_stem = [1] * len(closest_nodes)
    nodes_length = map(len, closest_nodes)

    stem_voxels = list()
    for i in range(len(closest_nodes)):
        stem_voxels += closest_nodes[i]
    stem_voxels = set(stem_voxels)

    remaining_voxels = set(set_voxels_plant).difference(stem_voxels)
    stem_voxels, _, _ = merge(graph, stem_voxels, remaining_voxels,
                              percentage=50)
    remaining_voxels = set(set_voxels_plant).difference(stem_voxels)


    # shogun(list(stem_voxels))
    # shogun(list(remaining_voxels))

    print len(remaining_voxels), len(stem_voxels), len(set_voxels_plant)

    j = 1
    while remaining_voxels:
        j += 1
        leaf = alinea.phenomenal.segmentation_3d.algorithm.segment_leaf_2(
            remaining_voxels,
            all_shorted_path,
            arr_voxels_plants,
            distance_plane_1=distance_plane_1,
            voxel_size=voxel_size)

        leaf, _, _ = merge(graph, leaf, remaining_voxels, percentage=50)

        # shogun(list(leaf))

        for i in range(len(closest_nodes)):
            v = len(set(closest_nodes[i]).intersection(leaf))

            values_stem[i] += float(v) / float(len(closest_nodes[i]))

        remaining_voxels = remaining_voxels.difference(leaf)

    mix = list()
    for i in range(len(values_stem)):
        mix.append(float(distances[i]) * len(closest_nodes[i]) / values_stem[i])

    def find_stop_peak(values):
        lookahead = int(len(values) / 50.0)

        max_peaks, min_peaks = peak_detection(values, lookahead)
        stop = alinea.phenomenal.segmentation_3d.algorithm.maize_corner_detection(
            values, min_peaks)

        return stop, min_peaks, max_peaks

    def find_stop_peak_2(values):
        lookahead = int(len(values) / 50.0)

        max_peaks, min_peaks = peak_detection(values, lookahead)
        labels = alinea.phenomenal.segmentation_3d.algorithm\
            .maize_corner_detection_2(
            values, min_peaks)

        return labels, min_peaks, max_peaks

    import matplotlib.pyplot
    def show_stop_peak(values):
        stop, min_peaks, max_peaks = find_stop_peak(values)

        for index, _ in min_peaks:
            matplotlib.pyplot.plot(index, values[index], 'bo')

        matplotlib.pyplot.plot(stop, values[stop], 'ro')


    def show_stop_peak_2(values):
        stop, min_peaks, max_peaks = find_stop_peak_2(values)

        for index, _ in min_peaks:
            matplotlib.pyplot.plot(index, values[index], 'bo')

        matplotlib.pyplot.plot(stop, values[stop], 'ro')

        # for i in range(len(min_peaks)):
        #     index, value = min_peaks[i]

            # if labels[i] == 0:
            #     matplotlib.pyplot.plot(index, value, 'bo')
            # else:
            #     matplotlib.pyplot.plot(index, value, 'ro')

        # for i in range(len(values)):
        #     # if labels[i] == 0:
        #     #     matplotlib.pyplot.plot(i, values[i], 'b+')
        #     # else:
        #     matplotlib.pyplot.plot(i, values[i], 'b+')


    matplotlib.pyplot.figure()
    matplotlib.pyplot.plot(range(len(nodes_length)), nodes_length, 'b')
    # matplotlib.pyplot.plot(range(len(values_stem)), values_stem, 'r')
    matplotlib.pyplot.plot(range(len(mix)), mix, 'g')
    # matplotlib.pyplot.plot(range(len(distances)), distances, 'r')
    # show_stop_peak(nodes_length)
    show_stop_peak_2(mix)
    matplotlib.pyplot.show()

    # ==========================================================================
    # Little hack
    # from alinea.phenomenal.display.multi_view_reconstruction import (
    #     show_list_points_3d)
    #
    # stop, min_peaks, max_peaks = find_stop_peak(nodes_length)
    # stem_voxel_path = [v for i, v in enumerate(stem_voxel_path) if i <= stop]
    # show_list_points_3d([biggest_component_voxel_centers, stem_voxel_path],
    #                     list_color=[(0, 1, 0), (1, 0, 0)])
    #
    #
    # stop, min_peaks, max_peaks = find_stop_peak_2(mix)
    # stem_voxel_path = [v for i, v in enumerate(stem_voxel_path) if i <= stop]
    # show_list_points_3d([biggest_component_voxel_centers, stem_voxel_path],
    #                     list_color=[(0, 1, 0), (1, 0, 0)])


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
    stem_voxel, voxels_remain, stem_voxel_path, stem_geometry, stem_top = \
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

    top_stem_neighbors = set()
    for node in stem_top:
        top_stem_neighbors = top_stem_neighbors.union(graph[node].keys())
    top_stem_neighbors = top_stem_neighbors - stem_voxel

    array_voxels_plant = numpy.array(biggest_connected_voxels_plant)

    # ==========================================================================

    # top_stem_neighbors = compute_top_stem_neighbors(graph,
    #                                                 stem_voxel,
    #                                                 stem_geometry)

    from alinea.phenomenal.display.multi_view_reconstruction import (
        show_list_points_3d)

    show_list_points_3d([stem_voxel, top_stem_neighbors])

    # ==========================================================================

    simple_leaf = list()
    simple_leaf_path = list()
    voxels_cornet = set()
    connected_leaf = list()

    if verbose:
        print "Number of connected components : ", len(connected_components)

    for i, connected_component in enumerate(connected_components):

        if len(top_stem_neighbors.intersection(connected_component)) > 0:
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
                    # print len(stem_neighbors.intersection(leaf))
                    # print len(stem_intersection)

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
        labeled_skeleton_path["leaf_" + str(i)] = voxels

    for i, voxels in enumerate(connected_leaf):
        labeled_voxels["connected_leaf_" + str(i)] = voxels

    return labeled_voxels, labeled_skeleton_path
