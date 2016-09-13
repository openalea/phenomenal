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
import math
import networkx
import numpy
import scipy.interpolate
from scipy.integrate._ode import vode
from sklearn.cluster import SpectralClustering, KMeans

from alinea.phenomenal.data_structure import (
    bounding_box)

from alinea.phenomenal.segmentation_3d.graph import (
    create_graph)

from alinea.phenomenal.segmentation_3d.peak_detection import (
    peak_detection)

from alinea.phenomenal.segmentation_3d.plane_interception import (
    compute_closest_nodes)

from alinea.phenomenal.data_structure import voxel_centers_to_image_3d

from alinea.phenomenal.display import show_points_3d, show_list_points_3d
# ==============================================================================
# Stem


def find_base_stem_position(voxel_centers, voxel_size, neighbor_size=40):

    image_3d = voxel_centers_to_image_3d(voxel_centers, voxel_size)

    x = int(round(0 - image_3d.world_coordinate[0] / image_3d.voxel_size))
    y = int(round(0 - image_3d.world_coordinate[1] / image_3d.voxel_size))

    k = neighbor_size / voxel_size
    x_len, y_len, z_len = image_3d.shape

    roi = image_3d[
          max(x - k, 0): min(x + k, x_len),
          max(y - k, 0): min(y + k, y_len),
          :]

    xx, yy, zz = numpy.where(roi == 1)
    i = numpy.argmin(zz)

    stem_base_position = max(x - k, 0) + xx[i], max(y - k, 0) + yy[i], zz[i]
    pos = numpy.array(stem_base_position)
    pos = pos * voxel_size + image_3d.world_coordinate
    return pos


def voxel_position_grid_to_real(grid_voxel_centers, voxel_size, origin):
    real_voxel_centers = numpy.array(grid_voxel_centers) * voxel_size + origin
    real_voxel_centers = map(tuple, list(real_voxel_centers))
    return real_voxel_centers


def voxel_position_real_to_grid(real_voxel_centers, voxel_size):
    (x_min, y_min, z_min), _ = bounding_box(real_voxel_centers)

    origin = numpy.array([x_min, y_min, z_min])

    grid_voxel_centers = (numpy.array(real_voxel_centers) - origin) / voxel_size
    grid_voxel_centers = grid_voxel_centers.astype(int)
    grid_voxel_centers = map(tuple, list(grid_voxel_centers))

    return grid_voxel_centers, origin


def graph_skeletonize(voxel_centers, voxel_size):
    # ==========================================================================
    # Graph creation
    graph = create_graph(voxel_centers, voxel_size=voxel_size)

    # Keep the biggest connected components
    graph = max(
        networkx.connected_component_subgraphs(graph, copy=False), key=len)

    # Keep the voxel cloud of the biggest component
    biggest_component_voxel_centers = graph.nodes()

    # ==========================================================================
    # Get the high points in the matrix and the supposed base plant points
    x_stem, y_stem, z_stem = find_base_stem_position(
        graph.nodes(), voxel_size)

    # ==========================================================================
    # Compute the shorted path

    all_shorted_path_to_stem_base = networkx.single_source_dijkstra_path(
        graph, (x_stem, y_stem, z_stem), weight="weight")

    return graph, biggest_component_voxel_centers, all_shorted_path_to_stem_base


def compute_ball_integer(node, r):
    x, y, z = map(int, map(round, node))
    r = int(round(r))

    xx = numpy.arange(x - r, x + r)
    yy = numpy.arange(y - r, y + r)
    zz = numpy.arange(z - r, z + r)

    xxx, yyy, zzz = numpy.meshgrid(xx, yy, zz)
    res = numpy.sqrt((xxx - x) ** 2 + (yyy - y) ** 2 + (zzz - z) ** 2) <= r

    l = list()
    for i in range(0, len(xx)):
        for j in range(0, len(xx)):
            for k in range(0, len(xx)):
                if res[i, j, k]:
                    l.append((xxx[i, j, k], yyy[i, j, k], zzz[i, j, k]))

    return l


def maize_corner_detection(nodes_length, min_peaks):
    d = {index: value for (index, value) in list(min_peaks)}

    sum_lgth, sum_width = (0, 0)

    l = list()
    for index in range(len(nodes_length)):
        sum_lgth += nodes_length[index]
        # sum_width += index
        sum_width += 1
        if index in d:
            # print "Sum width", sum_width
            l.append((index, nodes_length[index], sum_lgth, sum_width))
            sum_lgth, sum_width = (0, 0)

    del l[0]

    stop = 0
    sum_values = 0
    sum_all_lgth = 0
    sum_all_width = 0
    for i in range(len(l)):
        index, v, sum_lgth, sum_width = l[i]

        sum_values += v
        sum_all_lgth += sum_lgth
        sum_all_width += sum_width
        # print sum_all_width, i, (sum_all_width / (i + 1))

        if i + 2 < len(l):
            index_2, v_2, sum_lgth_2, sum_width_2 = l[i + 1]

            # print 'Sum value', (sum_values / (i + 1)) * 2.8, v_2
            if (sum_values / (i + 1)) * 2.8 < v_2:
                stop = index
                # print "Index values, stop", stop
                break

            # print 'Sum width', (sum_all_width / (i + 1)) * 1.0, sum_width_2
            if (sum_all_width / (i + 1)) * 1.5 < sum_width_2:
                # print (sum_all_lgth / (i + 1)) * 2.8, sum_lgth_2
                if (sum_all_lgth / (i + 1)) * 2.8 < sum_lgth_2:
                    stop = index
                    # print "Index lgth, stop", stop
                    break
        else:
            # print "Index end, stop", stop
            stop = index
            break

    return stop


def maize_corner_detection_2(values, min_peaks):
    # print min_peaks
    # l = [(index, value) for (index, value) in list(min_peaks)]
    #
    # sum_lgth, sum_width = (0, 0)
    #
    # index_values = list()
    # for i, value in enumerate(values):
    #     index_values.append((i, value))
    #
    # index_values = numpy.array(index_values)
    # print index_values
    #
    # k = KMeans(n_clusters=2)
    # k.fit(l)
    #
    # print k.labels_
    #
    # return k.labels_

    d = {index: value for (index, value) in list(min_peaks)}

    sum_lgth, sum_width = (0, 0)

    l = list()
    for index in range(len(values)):
        sum_lgth += values[index]
        # sum_width += index
        sum_width += 1
        if index in d:
            # print "Sum width", sum_width
            l.append((index, values[index], sum_lgth, sum_width))
            sum_lgth, sum_width = (0, 0)

    del l[0]

    stop = 0
    sum_values = 0
    sum_all_lgth = 0
    sum_all_width = 0
    for i in range(len(l)):
        index, v, sum_lgth, sum_width = l[i]

        sum_values += v

        # sum_all_lgth += sum_lgth
        # sum_all_width += sum_width
        # print sum_all_width, i, (sum_all_width / (i + 1))

        if i + 2 < len(l):
            index_2, v_2, sum_lgth_2, sum_width_2 = l[i + 1]

            # print 'Sum value', (sum_values / (i + 1)) * 2.8, v_2
            if (sum_values / (i + 1)) * 4 < v_2:
                stop = index
                # print "Index values, stop", stop
                break

        else:
            # print "Index end, stop", stop
            stop = index
            break

    return stop


def merge(graph, voxels, remaining_voxels, percentage=50):

    voxels_neighbors = set()
    for node in voxels:
        voxels_neighbors = voxels_neighbors.union(graph[node].keys())

    subgraph = graph.subgraph(remaining_voxels)

    connected_components = list()
    for voxel_group in networkx.connected_components(subgraph):
        nb = len(voxel_group.intersection(voxels_neighbors))

        if nb * 100 / len(voxel_group) >= percentage:
            voxels = voxels.union(voxel_group)
        else:
            connected_components.append(voxel_group)

    return voxels, voxels_neighbors, connected_components


def segment_stem(voxel_centers, all_shorted_path,
                 distance_plane_1=4,
                 voxel_size=4):

    array_voxel_centers = numpy.array(voxel_centers)
    index = numpy.argmax(array_voxel_centers[:, 2])
    x_top, y_top, z_top = array_voxel_centers[index]

    stem_voxel_path = all_shorted_path[(x_top, y_top, z_top)]

    planes, closest_nodes = compute_closest_nodes(
        array_voxel_centers, stem_voxel_path, radius=8,
        dist=distance_plane_1 * voxel_size)

    return stem_voxel_path, closest_nodes


def segment_leaf_2(nodes, all_shorted_path, voxel_centers,
                   distance_plane_1=4,
                   voxel_size=4):

    longest_shortest_path = None
    longest_length = 0
    for node in nodes:
        p = all_shorted_path[node]

        if len(p) > longest_length:
            longest_length = len(p)
            longest_shortest_path = p

    if longest_shortest_path:
        planes, closest_nodes = compute_closest_nodes(
            voxel_centers, longest_shortest_path, radius=8,
            dist=distance_plane_1 * voxel_size)

        leaf = list()
        for i in range(len(closest_nodes)):
            leaf += closest_nodes[i]

        return set(leaf)

def stem_segmentation(voxel_centers, all_shorted_path_down,
                      distance_plane_1=4,
                      distance_plane_2=0.75,
                      voxel_size=4):

    array_voxel_centers = numpy.array(voxel_centers)

    index = numpy.argmax(array_voxel_centers[:, 2])
    x_top, y_top, z_top = array_voxel_centers[index]

    stem_voxel_path = all_shorted_path_down[(x_top, y_top, z_top)]


    # import mayavi.mlab
    # from alinea.phenomenal.display.multi_view_reconstruction import (
    #     plot_points_3d)
    #
    # print stem_voxel_path
    #
    # mayavi.mlab.figure()
    #
    # mayavi.mlab.quiver3d(0, 0, 0,
    #                      100, 0, 0,
    #                      line_width=5.0,
    #                      scale_factor=1,
    #                      color=(1, 0, 0))
    #
    # mayavi.mlab.quiver3d(0, 0, 0,
    #                      0, 100, 0,
    #                      line_width=5.0,
    #                      scale_factor=1,
    #                      color=(0, 1, 0))
    #
    # mayavi.mlab.quiver3d(0, 0, 0,
    #                      0, 0, 100,
    #                      line_width=5.0,
    #                      scale_factor=1,
    #                      color=(0, 0, 1))
    #
    # plot_points_3d(
    #     list(stem_voxel_path),
    #     scale_factor=4,
    #     color=(1, 0, 0))
    #
    # plot_points_3d(
    #     voxel_centers,
    #     scale_factor=2,
    #     color=(0.1, 0.9, 0.1))
    #
    # mayavi.mlab.show()

    # ==================================== ======================================
    # Get normal of the path and intercept voxel, plane

    planes, closest_nodes = compute_closest_nodes(
        array_voxel_centers, stem_voxel_path, radius=8,
        dist=distance_plane_1 * voxel_size)

    # centred_shorted_path = [
    #     numpy.array(nodes).mean(axis=0) for nodes in closest_nodes]

    # ==========================================================================
    # Detect peak on graphic

    nodes_length = map(len, closest_nodes)
    lookahead = int(len(closest_nodes) / 50.0)
    nodes_length = [float(n) for n in nodes_length]

    max_peaks, min_peaks = peak_detection(nodes_length, lookahead)

    stop = maize_corner_detection(nodes_length, min_peaks)

    import matplotlib.pyplot
    matplotlib.pyplot.figure()
    matplotlib.pyplot.plot(range(len(nodes_length)), nodes_length)

    for index, _ in min_peaks:

        matplotlib.pyplot.plot(index, nodes_length[index], 'bo')

    matplotlib.pyplot.plot(stop, nodes_length[stop], 'ro')
    matplotlib.pyplot.show()

    # ==========================================================================
    stem_voxel_path = [v for i, v in enumerate(stem_voxel_path) if i <= stop]
    stem_min_peaks = [(i, v) for i, v in min_peaks if i <= stop]

    planes, closest_nodes = compute_closest_nodes(
        array_voxel_centers, stem_voxel_path, radius=8,
        dist=distance_plane_2 * voxel_size)

    stem_centred_path = [
        numpy.array(nodes).mean(axis=0) for nodes in closest_nodes]

    stem_centred_path_min_peak = [stem_centred_path[index]
                                  for index, value in stem_min_peaks]

    stem_voxel = set()
    for index, value in stem_min_peaks:
        stem_voxel = stem_voxel.union(closest_nodes[index])

    arr_stem_voxels = set()
    for nodes in closest_nodes:
        arr_stem_voxels = arr_stem_voxels.union(set(nodes))
    arr_stem_voxels = numpy.array(list(arr_stem_voxels))

    # ==========================================================================
    # Compute radius

    def get_max_distance(node, nodes):
        max_distance = 0
        max_node = node

        for n in nodes:
            distance = numpy.linalg.norm(numpy.array(node) - numpy.array(n))
            max_distance = max(max_distance, distance)
            max_node = n

        return max_node, max_distance

    # distances = list()
    # for i in range(len(closest_nodes)):
    #     nodes = closest_nodes[i]
    #
    #     pt1, _ = get_max_distance(nodes[0], nodes)
    #     pt2, distance = get_max_distance(pt1, nodes)
    #
    #     distances.append(float(distance) / float(voxel_size))

    # def compute_max_distance(centred_node, closest_nodes):
    #     radius = 0
    #     for node in closest_nodes:
    #         distance = numpy.linalg.norm(
    #             numpy.array(node) - numpy.array(centred_node))
    #
    #         radius = max(radius, distance)
    #
    #     return radius

    radius = list()
    radius.append(None)
    for index, value in stem_min_peaks:
        nodes = closest_nodes[index]

        pt1, _ = get_max_distance(nodes[0], nodes)
        pt2, distance = get_max_distance(pt1, nodes)

        radius.append(distance / 2.0)

        # radius.append(compute_max_distance(
        #     stem_centred_path[index], closest_nodes[index]))

    radius[0] = radius[1]

    # ==========================================================================
    # Interpolate

    new_centred_shorted_path = list()
    new_centred_shorted_path.append(stem_centred_path[0])
    new_centred_shorted_path += stem_centred_path_min_peak
    len_new_centred_shorted_path = len(new_centred_shorted_path)
    new_centred_shorted_path = numpy.array(new_centred_shorted_path).transpose()

    k = 3
    if len_new_centred_shorted_path <= k:
        k = 1

    tck, u = scipy.interpolate.splprep(new_centred_shorted_path, k=k)
    xxx, yyy, zzz = scipy.interpolate.splev(numpy.linspace(0, 1, 500), tck)

    # ==========================================================================

    score = len(xxx) / len(radius)

    j = 0
    # stem_voxel = set()
    stem_geometry = list()
    for i in range(len(xxx)):
        if i % score == 0 and j < len(radius):
            r = radius[j]
            j += 1

        x, y, z = xxx[i], yyy[i], zzz[i]

        stem_geometry.append(((x, y, z), max(r, float(voxel_size))))

        # res = numpy.sqrt((array_voxel_centers[:, 0] - x) ** 2 +
        #                  (array_voxel_centers[:, 1] - y) ** 2 +
        #                  (array_voxel_centers[:, 2] - z) ** 2)
        #
        # index = numpy.where(res <= numpy.array(r))
        #
        # res = map(tuple, list(array_voxel_centers[index]))
        # stem_voxel = stem_voxel.union(set(res))

        res = numpy.sqrt((arr_stem_voxels[:, 0] - x) ** 2 +
                         (arr_stem_voxels[:, 1] - y) ** 2 +
                         (arr_stem_voxels[:, 2] - z) ** 2)

        index = numpy.where(res <= numpy.array(r))

        res = map(tuple, list(arr_stem_voxels[index]))
        stem_voxel = stem_voxel.union(set(res))

    not_stem_voxel = set(voxel_centers).difference(stem_voxel)

    return stem_voxel, not_stem_voxel, stem_voxel_path, stem_geometry


# ==============================================================================
# Plant

# def compute_top_stem_neighbors(nvc, graph, stem_geometry):
#     i = -1
#     (x, y, z), radius = stem_geometry[i]
#     top_1_stem = compute_ball_integer((x, y, z), radius)
#
#     top_stem = set()
#     while len(top_stem) == 0:
#         i -= 1
#         (x, y, z), radius = stem_geometry[i]
#         top_2_stem = compute_ball_integer((x, y, z), radius)
#
#         top_stem = set(top_1_stem) - set(top_2_stem)
#         top_stem = set(top_stem).intersection(nvc)
#
#     subgraph = graph.subgraph(top_stem)
#     top_stem = max(networkx.connected_components(subgraph), key=len)
#
#     top_stem_neighbors = list()
#     for node in top_stem:
#         top_stem_neighbors += graph[node].keys()
#     top_stem_neighbors = set(top_stem_neighbors)
#
#     return top_stem_neighbors

def compute_top_stem_neighbors(graph, stem, stem_geometry):

    def compute_ball(array_voxels, center, radius):
        x, y, z = center
        res = numpy.sqrt((array_voxels[:, 0] - numpy.array(x)) ** 2 +
                         (array_voxels[:, 1] - numpy.array(y)) ** 2 +
                         (array_voxels[:, 2] - numpy.array(z)) ** 2)

        index = numpy.where(res <= numpy.array(radius))

        return set(map(tuple, list(array_stem_voxels[index])))

    array_stem_voxels = numpy.array(list(stem))

    i = -1
    center, radius = stem_geometry[i]

    stem_top_src = compute_ball(array_stem_voxels, center, radius)

    stem_top = set()
    while not stem_top:
        i -= 1
        center, radius = stem_geometry[i]
        stem_top_prev = compute_ball(array_stem_voxels, center, radius)

        stem_top = stem_top_src - stem_top_prev

    stem_top_neighbors = set()
    for node in stem_top:
        stem_top_neighbors = stem_top_neighbors.union(graph[node].keys())

    return stem_top_neighbors


def extract_data_leaf(leaf, longest_shortest_path):
    leaf_array = numpy.array(list(leaf))

    planes, closest_nodes = compute_closest_nodes(leaf_array,
                                                  longest_shortest_path,
                                                  radius=8,
                                                  dist=1)

    # TODO : little hack
    c_shorted_path = list()
    for nodes in closest_nodes:

        if len(nodes) > 1:
            # print len(nodes)
            # if nodes:
            c_shorted_path.append(numpy.array(nodes).mean(axis=0))
            # else:
            #     pass

    # ==============================================================
    # Interpolate
    print c_shorted_path
    data = numpy.array(c_shorted_path).transpose()

    k = 5
    print len(c_shorted_path)
    if len(c_shorted_path) <= 5:
        k = len(c_shorted_path) - 1
    print k
    idim, m = data.shape
    print m

    tck, u = scipy.interpolate.splprep(data, k=k)
    xxx, yyy, zzz = scipy.interpolate.splev(
        numpy.linspace(0, 1, 500),
        tck)

    path = list()
    for i in xrange(len(xxx)):
        path.append((xxx[i], yyy[i], zzz[i]))

    nodes_length = map(len, closest_nodes)
    max_node_lgth = max(nodes_length)
    index_max_node_lgth = nodes_length.index(max_node_lgth)

    plane = closest_nodes[index_max_node_lgth]

    def distance(n1, n2):
        x, y, z = n1
        xx, yy, zz = n2

        d = (x - xx) ** 2 + (y - yy) ** 2 + (z - zz) ** 2
        return math.sqrt(d)

    max_dist = list()
    for n1 in plane:
        max_dist.append(max([distance(n1, n2) for n2 in plane]))

    max_longest = 0
    for i in xrange(len(path)):
        n1 = path[i]

        if i + 1 < len(path):
            n2 = path[i + 1]
            max_longest += distance(n1, n2)

    x, y, z = path[0]
    vectors = list()
    for i in xrange(1, len(path)):
        xx, yy, zz = path[i]

        v = (xx - x, yy - y, zz - z)
        vectors.append(v)

    vector_mean = numpy.array(vectors).mean(axis=0)
    print vector_mean

    distances_max = max(max_dist)
    print "Max largest :", distances_max
    print "Max longest :", max_longest

    # nodes_length = map(len, closest_nodes)
    # lookahead = int(len(closest_nodes) / 50.0)
    # nodes_length = [float(n) for n in nodes_length]
    #
    # max_peaks, min_peaks = peak_detection(
    #     nodes_length, lookahead, verbose=verbose)

    a, b, c = vector_mean

    return path, distances_max, max_longest, ((float(x), float(y), float(z)),
                                              (float(a), float(b), float(c)))


def segment_leaf(voxels,
                 connected_components,
                 skeleton_path,
                 array_voxel_centers,
                 graph,
                 voxel_size, verbose=False):

    # ==========================================================================
    # Get the longest shorted path of voxels

    leaf_skeleton_path = None
    longest_length = 0
    for node in voxels:
        p = skeleton_path[node]

        if len(p) > longest_length:
            longest_length = len(p)
            leaf_skeleton_path = p

    # print len(connected_components)

    # ==========================================================================

    if leaf_skeleton_path:

        planes, closest_nodes = compute_closest_nodes(
            array_voxel_centers,
            leaf_skeleton_path,
            radius=8,
            dist=2 * voxel_size,
            verbose=True,
            graph=graph)

        # show_list_points_3d(closest_nodes)

        leaf = set().union(*closest_nodes)
        leaf = leaf.intersection(connected_components)
        remain = set(voxels).difference(leaf)

        if verbose:
            print "len of connected_component :", len(voxels)
            print "len of not_leaf :", len(remain)
            print "len of leaf  :", len(leaf)

        leaf, leaf_neighbors, connected_components_remain = merge(
            graph, leaf, remain)

        remain = set().union(*connected_components_remain)

        # remain = set()
        # if not_leaf > 0:
        #     leaf_neighbors = set()
        #     for node in leaf:
        #         leaf_neighbors = leaf_neighbors.union(graph[node].keys())
        #
        #     subgraph = graph.subgraph(not_leaf)
        #
        #     for voxels in networkx.connected_components(subgraph):
        #         nb_leaf = len(voxels.intersection(leaf_neighbors))
        #         nb_stem = len(voxels.intersection(stem_neighbors))
        #
        #         if verbose:
        #             print "Percentage leaf:", nb_leaf * 100 / len(voxels)
        #             print "Percentage stem:", nb_stem * 100 / len(voxels)
        #             print "Number of voxel:", len(voxels), '\n'
        #
        #         if nb_leaf * 100 / len(voxels) >= 50:
        #             leaf = leaf.union(voxels)
        #         elif nb_stem * 100 / len(voxels) >= 50:
        #             stem_voxel = stem_voxel.union(voxels)
        #         elif len(voxels) * voxel_size <= 100:  # TODO: hack remove
        #             leaf = leaf.union(voxels)
        #         else:
        #             remain = remain.union(voxels)

        return leaf, remain, leaf_skeleton_path
