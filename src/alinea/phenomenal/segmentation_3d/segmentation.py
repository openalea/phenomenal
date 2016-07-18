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
import collections
import math
import time

import matplotlib.pyplot
import mayavi.mlab
import networkx
import numpy
import scipy.interpolate

# ==============================================================================

from alinea.phenomenal.multi_view_reconstruction.routines import (
    bounding_box)

from alinea.phenomenal.display import plot_points_3d
from alinea.phenomenal.segmentation_3d.graph import (
    create_graph,
    ball,
    get_max_radius_ball,
    get_max_radius_floating_ball_2,
    get_max_radius_floating_ball)

from alinea.phenomenal.segmentation_3d.peakdetect import peakdetect


# ==============================================================================


def compute_planes(points):
    mean_point = points.mean(axis=0)

    # Do an SVD on the mean-centered data.
    uu, dd, vv = numpy.linalg.svd(points - mean_point)

    return vv[0]


def get_point_of_planes(normal, node, radius=5):
    a, b, c = normal
    x, y, z = node

    d = a * x + b * y + c * z

    xx = numpy.linspace(x - radius, x + radius, radius * 2)
    yy = numpy.linspace(y - radius, y + radius, radius * 2)

    xv, yv = numpy.meshgrid(xx, yy)

    zz = - (a * xv + b * yv - d) / c

    return xv, yv, zz


def get_distance_point_to_plane(node, plane):
    x, y, z = node
    a, b, c, d = plane

    return abs(a * x + b * y + c * z - d) / math.sqrt(a**2 + b**2 + c**2)


def get_node_close_to_planes_2(graph, node_src, plane, dist=0.75):

    a, b, c, d = plane
    plane_square = math.sqrt(a ** 2 + b ** 2 + c ** 2)

    closest_node = list()
    closest_node.append(node_src)

    nodes = collections.deque()
    nodes += graph[node_src].keys()
    while nodes:
        node = nodes.pop()

        if node not in closest_node:
            x, y, z = node

            # Plane distance equation
            distance = abs(a * x + b * y + c * z - d) / plane_square

            if distance < dist:
                closest_node.append(node)

                nodes += graph[node].keys()

    return closest_node


def compute_closest_nodes_2(graph, path, radius=8, verbose=False, dist=0.75):

    if verbose:
        print "Computation of planes long to the path : ...",
        t0 = time.time()

    planes = list()
    closest_nodes = list()
    centred_path = list()

    length_path = len(path)
    for i in xrange(length_path):
        node = path[i]

        neighbors = numpy.array(
            path[max(0, i - radius):min(length_path, i + radius)])

        # Do an SVD on the mean-centered neighbors points.
        k = numpy.linalg.svd(neighbors - neighbors.mean(axis=0))[2][0]

        # Computation of plane equation
        # x, y, z = node
        # a, b, c, _ = k
        # Plane equation : d = a * x + b * y + c * z
        d = k[0] * node[0] + k[1] * node[1] + k[2] * node[2]
        plane = (k[0], k[1], k[2], d)
        planes.append(plane)

        nodes = get_node_close_to_planes_2(graph, node, plane, dist=dist)

        centred_path.append(numpy.array(nodes).mean(axis=0))
        closest_nodes.append(nodes)

    if verbose:
        print "done, in ", time.time() - t0, 'seconds'

    return planes, closest_nodes, centred_path


def get_node_close_to_planes(voxels, node_src, plane, dist=0.75):
    """
    - voxels is a numpy array
    - node_src tuple
    - plane is a tuple of 4 elements containing (a, b, c, d) value of a plane
    equation

    - dist : is the maximal distance between plane and node

    """

    res = abs(voxels[:, 0] * plane[0] +
              voxels[:, 1] * plane[1] +
              voxels[:, 2] * plane[2] -
              plane[3]) / (math.sqrt(plane[0] ** 2 +
                                     plane[1] ** 2 +
                                     plane[2] ** 2))

    index = numpy.where(res < dist)[0]
    closest_voxel = voxels[index]

    nodes = list()
    closest_node = list()

    # if node_src in map(tuple, voxels):
    nodes.append(numpy.array(node_src))
    closest_node.append(numpy.array(node_src))

    while nodes:
        node = nodes.pop()

        rr = numpy.sum(abs(closest_voxel - node), 1)

        index = numpy.where(rr <= 3)[0]
        nodes += list(closest_voxel[index])
        closest_node += list(closest_voxel[index])

        closest_voxel = numpy.delete(closest_voxel, index, 0)

        if closest_voxel.size == 0:
            break

    return map(tuple, closest_node)


def compute_closest_nodes(voxels, path, radius=8, dist=0.75):

    planes = list()
    closest_nodes = list()

    length_path = len(path)
    for i in xrange(length_path):
        node = path[i]

        neighbors = numpy.array(
            path[max(0, i - radius):min(length_path, i + radius)])

        # Do an SVD on the mean-centered neighbors points.
        k = abs(numpy.linalg.svd(neighbors - neighbors.mean(axis=0))[2][0])

        # Computation of plane equation
        # x, y, z = node
        # a, b, c, _ = k
        # Plane equation : d = a * x + b * y + c * z
        d = k[0] * node[0] + k[1] * node[1] + k[2] * node[2]
        plane = (k[0], k[1], k[2], d)

        planes.append(plane)

        nodes = get_node_close_to_planes(voxels, node, plane, dist=dist)
        closest_nodes.append(nodes)

    return planes, closest_nodes


def peak_detection(values, lookahead, verbose=False):

    lookahead = max(1, int(lookahead))

    max_peaks, min_peaks = peakdetect(
        values, range(len(values)), lookahead=lookahead)

    if verbose:
        matplotlib.pyplot.figure()
        matplotlib.pyplot.plot(range(len(values)), values)

        for index, value in min_peaks:
            matplotlib.pyplot.plot(index, value, 'bo')

        for index, value in max_peaks:
            matplotlib.pyplot.plot(index, value, 'ro')

        matplotlib.pyplot.show()

    return max_peaks, min_peaks


def peak_detection_2(values, lookahead, verbose=False):
    import scipy.signal

    lookahead = max(1, int(lookahead))

    max_peaks = scipy.signal.argrelmax(numpy.array(values), order=lookahead)[0]
    min_peaks = scipy.signal.argrelmin(numpy.array(values), order=lookahead)[0]

    if verbose:
        matplotlib.pyplot.figure()
        matplotlib.pyplot.plot(range(len(values)), values)

        for index in min_peaks:
            matplotlib.pyplot.plot(index, values[index], 'bo')

        for index in max_peaks:
            matplotlib.pyplot.plot(index, values[index], 'ro')

        matplotlib.pyplot.show()

    return max_peaks, min_peaks


def segment_leaf(nodes, connected_components, all_shorted_path,
                 new_voxel_centers, stem_voxel, stem_neighbors, graph,
                 voxel_size, verbose=False):

    longest_shortest_path = None
    longest_length = 0
    for node in nodes:
        p = all_shorted_path[node]

        if len(p) > longest_length:
            longest_length = len(p)
            longest_shortest_path = p

    if longest_shortest_path:

        # if verbose:
        #
        #     mayavi.mlab.figure("Longest_shortest_path of leaf")
        #
        #     plot_points_3d(new_voxel_centers,
        #                    scale_factor=voxel_size * 0.1,
        #                    color=(0.1, 1, 0.1))
        #
        #     plot_points_3d(longest_shortest_path,
        #                    scale_factor=voxel_size * 0.2,
        #                    color=(0, 0, 0))
        #
        #     mayavi.mlab.show()

        planes, closest_nodes = compute_closest_nodes(new_voxel_centers,
                                                      longest_shortest_path,
                                                      radius=8,
                                                      dist=2)

        leaf = list()
        for i in xrange(len(closest_nodes)):
            leaf += closest_nodes[i]

        leaf = set(leaf).intersection(connected_components)
        not_leaf = set(nodes).difference(leaf)

        if verbose:
            print "len of connected_component :", len(nodes)
            print "len of not_leaf :", len(not_leaf)
            print "len of leaf  :", len(leaf)

        left = set()
        if len(not_leaf) > 0:
            leaf_neighbors = list()
            for node in leaf:
                leaf_neighbors += graph[node].keys()
            leaf_neighbors = set(leaf_neighbors)

            subgraph = graph.subgraph(not_leaf)

            for voxels in networkx.connected_components(subgraph):
                nb_leaf = len(voxels.intersection(leaf_neighbors))
                nb_stem = len(voxels.intersection(stem_neighbors))

                if verbose:
                    print "Percentage leaf:", nb_leaf * 100 / len(voxels)
                    print "Percentage stem:", nb_stem * 100 / len(voxels)
                    print "Number of voxel:", len(voxels), '\n'

                if nb_leaf * 100 / len(voxels) >= 50:
                    leaf = leaf.union(voxels)
                elif nb_stem * 100 / len(voxels) >= 50:
                    stem_voxel = stem_voxel.union(voxels)
                elif len(voxels) * voxel_size <= 100:  # TODO: hack
                    leaf = leaf.union(voxels)
                else:
                    left = left.union(voxels)

        # if verbose:
        #
        #     mayavi.mlab.figure("")
        #     plot_points_3d(new_voxel_centers,
        #                    scale_factor=voxel_size * 0.1,
        #                    color=(0.1, 1, 0.1))
        #
        #     plot_points_3d(list(stem_voxel),
        #                    scale_factor=voxel_size * 0.1,
        #                    color=(0, 0, 0))
        #
        #     plot_points_3d(list(leaf),
        #                    scale_factor=voxel_size * 0.1,
        #                    color=(0, 0, 1))
        #
        #     plot_points_3d(list(left),
        #                    scale_factor=voxel_size * 0.1,
        #                    color=(1, 0, 0))
        #     mayavi.mlab.show()

        return leaf, left, stem_voxel, longest_shortest_path


def maize_corner_detection(nodes_length, min_peaks, verbose=False):

    d = {index: value for (index, value) in list(min_peaks)}

    print min_peaks

    sum_lgth, sum_width = (0, 0)

    l = list()
    for index in xrange(len(nodes_length)):
        sum_lgth += nodes_length[index]
        sum_width += index
        if index in d:
            l.append((index, nodes_length[index], sum_lgth, sum_width))
            sum_lgth, sum_width = (0, 0)

    del l[0]
    print l

    stop = 0
    sum_values = 0
    sum_all_lgth = 0
    sum_all_width = 0
    for i in xrange(len(l)):
        index, v, sum_lgth, sum_width = l[i]

        sum_values += v
        sum_all_lgth += sum_lgth
        sum_all_width += sum_width

        if i + 2 < len(l):
            index_2, v_2, sum_lgth_2, sum_width_2 = l[i + 1]

            print (sum_values / (i + 1)) * 2.8, v_2
            if (sum_values / (i + 1)) * 2.8 < v_2:
                stop = index
                print "Index values, stop", stop
                break

            print (sum_all_width / (i + 1)) * 1.5, sum_width_2
            if (sum_all_width / (i + 1)) * 1.5 < sum_width_2:
                print (sum_all_lgth / (i + 1)) * 2.8, sum_lgth_2
                if (sum_all_lgth / (i + 1)) * 2.8 < sum_lgth_2:
                    stop = index
                    print "Index lgth, stop", stop
                    break
        else:
            print "Index end, stop", stop
            stop = index
            break

    if verbose:
        matplotlib.pyplot.figure()
        matplotlib.pyplot.plot(range(len(nodes_length)), nodes_length)

        for index, value in min_peaks:
            matplotlib.pyplot.plot(index, value, 'bo')
        matplotlib.pyplot.plot(stop, d[stop], 'ro')
        matplotlib.pyplot.show()

    return stop


def extract_data_leaf(leaf, longest_shortest_path, verbose=False):

    leaf_array = numpy.array(list(leaf))
    planes, closest_nodes = compute_closest_nodes(leaf_array,
                                                  longest_shortest_path,
                                                  radius=8,
                                                  dist=1)

    # TODO : hack little
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

    if verbose:
        mayavi.mlab.figure("")

        plot_points_3d(list(leaf),
                       scale_factor=1,
                       color=(0.7, 0, 0.1))

        plot_points_3d(c_shorted_path,
                       scale_factor=1,
                       color=(0.1, 0.1, 1))

        plot_points_3d(path,
                       scale_factor=1,
                       color=(0.1, 1, 1))

        plot_points_3d(longest_shortest_path,
                       scale_factor=1,
                       color=(0, 0, 0))

        a, b, c = vector_mean
        mayavi.mlab.quiver3d(float(x), float(y), float(z),
                             float(a), float(b), float(c),
                             line_width=2.0,
                             scale_factor=2,
                             color=(0, 0, 1))

        mayavi.mlab.show()

    if verbose:
        matplotlib.pyplot.figure()
        matplotlib.pyplot.plot(
            range(len(nodes_length)), nodes_length)

        matplotlib.pyplot.plot(index_max_node_lgth,
                               max_node_lgth,
                               'bo')

        matplotlib.pyplot.show()

    a, b, c = vector_mean

    return path, distances_max, max_longest, ((float(x), float(y), float(z)),
                                              (float(a), float(b), float(c)))


def find_stem_base_position(octree, voxel_size):

    k = 5 * voxel_size

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


def grid_voxel(voxel_centers, voxel_size):

    (x_min, y_min, z_min), _ = bounding_box(voxel_centers)

    origin = numpy.array([x_min, y_min, z_min])

    new_voxel_centers = (numpy.array(voxel_centers) - origin) / voxel_size

    new_voxel_centers = new_voxel_centers.astype(int)

    return new_voxel_centers, origin


def graph_skeletonize(voxel_centers, voxel_size, stem_base_position, verbose=False):
    # ==========================================================================
    # Graph creation

    new_voxel_centers, origin = grid_voxel(voxel_centers, voxel_size)

    graph = create_graph(map(tuple, list(new_voxel_centers)))

    # Keep the biggest connected components
    graph = max(networkx.connected_component_subgraphs(graph, copy=False),
                key=len)

    # Convert to numpy array
    new_voxel_centers = numpy.array(networkx.nodes(graph))

    # ==========================================================================
    # Get the high points in the matrix and the suposed base plant points

    stem_base_position = (stem_base_position - origin) / voxel_size
    x_stem, y_stem, z_stem = stem_base_position
    print 'Node base : ', x_stem, y_stem, z_stem

    # ==========================================================================
    # Compute the shorted path

    all_shorted_path_down = networkx.single_source_dijkstra_path(
        graph, (x_stem, y_stem, z_stem), weight="weight")

    return graph, new_voxel_centers, all_shorted_path_down, origin


def compute_ball_integer(node, r):
    x, y, z = node

    l = list()
    diameter = r * 2
    for i in xrange(int(x - diameter), int(x + diameter), 1):
        for j in xrange(int(y - diameter), int(y + diameter), 1):
            for k in xrange(int(z - diameter), int(z + diameter), 1):
                if math.sqrt((i - x) ** 2 + (j - y) ** 2 + (k - z) ** 2) <= r:
                    l.append((i, j, k))
    return l


def stem_segmentation(voxel_centers, all_shorted_path_down,
                      verbose=False):

    index = numpy.argmax(voxel_centers[:, 2])
    x_top, y_top, z_top = voxel_centers[index]
    print 'Node top : ', x_top, y_top, z_top

    stem_voxel_path = all_shorted_path_down[(x_top, y_top, z_top)]

    # if verbose:
    #     print 'Length of shorted path', len(shortest_path)
    #
    #     mayavi.mlab.figure("shorted path")
    #
    #     plot_points_3d(voxel_centers,
    #                    scale_factor=0.5,
    #                    color=(0.1, 1, 0.1))
    #
    #     plot_points_3d(shortest_path,
    #                    scale_factor=0.5,
    #                    color=(0, 0, 0))
    #
    #     mayavi.mlab.show()

    # ==========================================================================
    # Get normal of the path and intercept voxel, plane

    planes, closest_nodes = compute_closest_nodes(
        voxel_centers, stem_voxel_path, radius=8,
        dist=5)

    centred_shorted_path = [
        numpy.array(nodes).mean(axis=0) for nodes in closest_nodes]

    # if verbose:
    #
    #     mayavi.mlab.figure("")
    #
    #     plot_points_3d(
    #         voxel_centers,
    #         scale_factor=0.5,
    #         color=(0.1, 1, 0.1))
    #
    #     plot_points_3d(
    #         centred_shorted_path,
    #         scale_factor=0.5,
    #         color=(0.1, 0.1, 1))
    #
    #     plot_points_3d(
    #         shortest_path,
    #         scale_factor=0.5,
    #         color=(0, 0, 0))
    #
    #     for i in xrange(len(planes)):
    #         # x, y, z = points_3d[i]
    #         # a, b, c, d = planes[i]
    #         #
    #         # a = float(round(a, 4) * 1000)
    #         # b = float(round(b, 4) * 1000)
    #         # c = float(round(c, 4) * 1000)
    #         #
    #         # print x, y, z, a, b, c, d
    #         #
    #         # mayavi.mlab.quiver3d(float(x), float(y), float(z),
    #         #                      a, b, c,
    #         #                      line_width=1.0,
    #         #                      scale_factor=0.1)
    #         #
    #         # xx, yy, zz = get_point_of_planes((a, b, c), (x, y, z), radius=40)
    #         # mayavi.mlab.mesh(xx, yy, zz)
    #
    #         plot_points_3d(closest_nodes[i], scale_factor=0.5)
    #
    #     mayavi.mlab.show()
    # ==========================================================================
    # Detect peak on graphic

    nodes_length = map(len, closest_nodes)
    lookahead = int(len(closest_nodes) / 50.0)
    nodes_length = [float(n) for n in nodes_length]

    max_peaks, min_peaks = peak_detection(
        nodes_length, lookahead, verbose=verbose)

    stop = maize_corner_detection(nodes_length, min_peaks, verbose=verbose)

    # ==========================================================================
    # Compute radius

    def compute_radius(centred_node, closest_nodes):

        radius = 0
        for node in closest_nodes:
            distance = numpy.linalg.norm(
                numpy.array(node) - numpy.array(centred_node))

            radius = max(radius, distance)

        return radius

    data = list()
    radius = list()
    data.append(centred_shorted_path[0])
    radius.append(None)
    for index, value in min_peaks:
        print index, value, stop
        if index <= stop:
            data.append(centred_shorted_path[index])
            radius.append(compute_radius(centred_shorted_path[index],
                                         closest_nodes[index]))

    radius[0] = radius[1]

    data = numpy.array(data).transpose()

    # ==========================================================================
    # Interpolate

    tck, u = scipy.interpolate.splprep(data)
    xxx, yyy, zzz = scipy.interpolate.splev(numpy.linspace(0, 1, 500), tck)
    # ==========================================================================

    print "Interpolate done"

    score = len(xxx) / len(radius)
    j = 0

    stem_voxel = list()
    stem_geometry = list()
    for i in xrange(len(xxx)):

        if i % score == 0 and j < len(radius):
            r = radius[j]
            j += 1

        x, y, z = xxx[i], yyy[i], zzz[i]

        stem_geometry.append(((x, y, z), max(r, 1)))

        stem_voxel += compute_ball_integer((x, y, z), max(r, 1))

    stem_voxel = set(stem_voxel)

    nvc = set(map(tuple, list(voxel_centers)))
    stem_voxel = stem_voxel.intersection(nvc)
    not_stem_voxel = nvc.difference(stem_voxel)

    return stem_voxel, not_stem_voxel, stem_voxel_path, stem_geometry


def compute_top_stem_neighbors(nvc, graph, stem_geometry):

    i = -1
    (x, y, z), radius = stem_geometry[i]
    top_1_stem = compute_ball_integer((x, y, z), radius)

    top_stem = set()
    while len(top_stem) == 0:
        i -= 1
        (x, y, z), radius = stem_geometry[i]
        top_2_stem = compute_ball_integer((x, y, z), radius)

        top_stem = set(top_1_stem) - set(top_2_stem)
        top_stem = set(top_stem).intersection(nvc)

    subgraph = graph.subgraph(top_stem)
    top_stem = max(networkx.connected_components(subgraph), key=len)

    top_stem_neighbors = list()
    for node in top_stem:
        top_stem_neighbors += graph[node].keys()
    top_stem_neighbors = set(top_stem_neighbors)

    return top_stem_neighbors

    # ==========================================================================


def merge(graph, stem_voxel, not_stem_voxel, percentage=50):

    stem_neighbors = list()
    for node in stem_voxel:
        stem_neighbors += graph[node].keys()
    stem_neighbors = set(stem_neighbors)

    subgraph = graph.subgraph(not_stem_voxel)

    connected_components = list()
    for voxels in networkx.connected_components(subgraph):
        nb_stem = len(voxels.intersection(stem_neighbors))

        print "Percentage stem:", nb_stem * 100 / len(voxels)

        if nb_stem * 100 / len(voxels) >= percentage:
            stem_voxel = stem_voxel.union(voxels)
        else:
            connected_components.append(voxels)

    return stem_voxel, stem_neighbors, connected_components


def maize_segmentation(voxel_centers, voxel_size,
                       stem_base_position=None,
                       verbose=False):

    graph, new_voxel_centers, all_shorted_path_down, origin = graph_skeletonize(
        voxel_centers, voxel_size, stem_base_position)

    # ==========================================================================
    stem_voxel, not_stem_voxel, stem_voxel_path, stem_geometry = \
        stem_segmentation(new_voxel_centers, all_shorted_path_down, verbose=verbose)

    nvc = set(map(tuple, list(new_voxel_centers)))

    top_stem_neighbors = compute_top_stem_neighbors(nvc, graph, stem_geometry)

    stem_voxel, stem_neighbors, connected_components = merge(
        graph, stem_voxel, not_stem_voxel, percentage=50)

    # ==========================================================================

    print "Size Stem :", len(stem_voxel)
    print "Number of connected components :", len(connected_components)

    if True:
        mayavi.mlab.figure("")

        for voxels in connected_components:
            plot_points_3d(list(voxels), scale_factor=0.5)

        plot_points_3d(list(stem_voxel), scale_factor=0.5, color=(0, 0, 0))

        plot_points_3d(list(top_stem_neighbors), scale_factor=0.2,
                       color=(1, 0, 0.5))

        mayavi.mlab.show()

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
                    leaf, longest_shortest_path, verbose=False)

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

# ==============================================================================
# ==============================================================================
# ==============================================================================


def convert_to_real_point_3d(stem_positions, origin, voxel_size):

    points_3d = list()
    for x, y, z in stem_positions:
        xx = origin[0] + x * voxel_size
        yy = origin[1] + y * voxel_size
        zz = origin[2] + z * voxel_size

        points_3d.append((xx, yy, zz))

    return points_3d


def get_position_of_path_max_radius(graph, path_max_radius):

    list_position = list()
    for node, radius, floating_node in path_max_radius:
        list_position.append(node)
        list_position += ball(graph, floating_node, radius)

    return list(set(list_position))


def get_path_max_radius_ball(graph, path, verbose=False):

    path_max_radius = list()
    for node in path:

        radius = get_max_radius_ball(graph, node)

        if verbose:
            print node, radius

        path_max_radius.append((node, radius))

    # if verbose:
    #     z = numpy.array(path)[:, 0]
    #     r = numpy.array(path_max_radius)
    #     matplotlib.pyplot.figure()
    #     matplotlib.pyplot.plot(z, r)
    #     matplotlib.pyplot.show()

    return path_max_radius


def get_path_max_radius_floating_ball_2(graph, path, closests, verbose=False):
    path_max_radius = list()
    for i in xrange(len(path)):

        node = path[i]
        nodes = closests[i]

        radius = get_max_radius_floating_ball_2(graph, node, nodes)

        if verbose:
            print "\n\nNode : ", node, radius

        path_max_radius.append((node, radius))

    return path_max_radius


def get_path_max_radius_floating_ball(graph, path, verbose):
    path_max_radius = list()
    for node in path:
        radius, floating_node = get_max_radius_floating_ball(graph, node)

        if verbose:
            print "\n\nNode : ", node, radius, floating_node

        path_max_radius.append((node, radius))

    if verbose:
        z = numpy.array(path)[:, 2]
        r = numpy.array(path_max_radius)[:, 1]
        matplotlib.pyplot.figure()
        matplotlib.pyplot.plot(z, r)
        matplotlib.pyplot.show()

    return path_max_radius


def detect_corners_plant(path_max_radius, verbose=False):

    mmax = -1
    index_max = -1
    mmin = 100
    index_min = -1

    tmp_max = -1
    tmp_index_max = -1
    tmp_min = 100
    tmp_index_min = -1

    for i in xrange(len(path_max_radius)):
        node, value = path_max_radius[i]

        if value < tmp_max:

            if tmp_max > mmax:
                mmax = tmp_max
                index_max = tmp_index_max
                mmin = tmp_min
                index_min = tmp_index_min

            tmp_max = -1
            tmp_min = 10000

        if value > tmp_max:
            tmp_max = value
            tmp_index_max = i

        if value < tmp_min:
            tmp_min = value
            tmp_index_min = i

    if verbose:
        print path_max_radius[index_max], mmax, index_max
        print path_max_radius[index_min], mmin, index_min

    return path_max_radius[:index_min]
