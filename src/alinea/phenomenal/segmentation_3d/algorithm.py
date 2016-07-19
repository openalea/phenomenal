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

from alinea.phenomenal.multi_view_reconstruction.routines import (
    bounding_box)

from alinea.phenomenal.segmentation_3d.graph import (
    create_graph)

from alinea.phenomenal.segmentation_3d.peak_detection import (
    peak_detection)

from alinea.phenomenal.segmentation_3d.plane_interception import (
    compute_closest_nodes)

# ==============================================================================
# Stem


def grid_voxel(voxel_centers, voxel_size):
    (x_min, y_min, z_min), _ = bounding_box(voxel_centers)

    origin = numpy.array([x_min, y_min, z_min])

    new_voxel_centers = (numpy.array(voxel_centers) - origin) / voxel_size

    new_voxel_centers = new_voxel_centers.astype(int)

    return new_voxel_centers, origin


def graph_skeletonize(voxel_centers, voxel_size, stem_base_position):
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


def maize_corner_detection(nodes_length, min_peaks):
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

    return stop


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


def stem_segmentation(voxel_centers, all_shorted_path_down):

    index = numpy.argmax(voxel_centers[:, 2])
    x_top, y_top, z_top = voxel_centers[index]
    print 'Node top : ', x_top, y_top, z_top

    stem_voxel_path = all_shorted_path_down[(x_top, y_top, z_top)]

    # ==========================================================================
    # Get normal of the path and intercept voxel, plane

    planes, closest_nodes = compute_closest_nodes(
        voxel_centers, stem_voxel_path, radius=8,
        dist=5)

    centred_shorted_path = [
        numpy.array(nodes).mean(axis=0) for nodes in closest_nodes]

    # ==========================================================================
    # Detect peak on graphic

    nodes_length = map(len, closest_nodes)
    lookahead = int(len(closest_nodes) / 50.0)
    nodes_length = [float(n) for n in nodes_length]

    max_peaks, min_peaks = peak_detection(
        nodes_length, lookahead)

    stop = maize_corner_detection(nodes_length, min_peaks)

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


# ==============================================================================
# Plant

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


        return leaf, left, stem_voxel, longest_shortest_path


