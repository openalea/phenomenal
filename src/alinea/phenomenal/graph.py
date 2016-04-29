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
import time
import math
import networkx
import numpy
import scipy.spatial
import gc
# ==============================================================================


def create_graph(matrix, verbose=False):

    if verbose:
        t0 = time.time()

    graph = networkx.Graph()

    len_x, len_y, len_z = matrix.shape
    mm = numpy.zeros((len_x + 2, len_y + 2, len_z + 2))
    mm[1:-1, 1:-1, 1:-1] = matrix

    xx, yy, zz = numpy.where(mm == 1)
    for i in xrange(len(xx)):
        x, y, z = xx[i], yy[i], zz[i]

        graph.add_node((x - 1, y - 1, z - 1))

        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                for k in [-1, 0, 1]:
                    ind = x + i, y + j, z + k
                    if mm[ind] == 1:
                        graph.add_edge((x - 1, y - 1, z - 1),
                                       (x + i - 1, y + j - 1, z + k - 1),
                                       weight=abs(i) + abs(j) + abs(k))

    gc.collect()

    if verbose:
        print 'Time graph building : ', time.time() - t0
        print 'Nodes :', graph.number_of_nodes()
        print 'Edges :', graph.number_of_edges()

    return graph


# ==============================================================================

def ball(graph, node_src, radius):
    g = networkx.single_source_shortest_path_length(
        graph, node_src, cutoff=int(radius * 2))

    ball_list = list()
    for node in g:
        d = scipy.spatial.distance.euclidean(node_src, node)
        if d <= radius:
            ball_list.append(node)

    return ball_list


def get_max_size_ball(value):
    m = 0
    my_range = int(1 + value * 2)
    for i in xrange(-my_range, my_range, 1):
        for j in xrange(-my_range, my_range, 1):
            for k in xrange(-my_range, my_range, 1):
                if math.sqrt(i ** 2 + j ** 2 + k ** 2) <= value:
                    m += 1

    return m


len_max_ball = dict()
for radius in numpy.arange(0, 10, 0.1):
    radius = round(radius, 2)
    len_max_ball[radius] = get_max_size_ball(radius)


def get_max_radius_ball_2(graph, node_src):
    max_radius_ball = 0

    for radius_int in xrange(0, 10, 1):

        g = networkx.single_source_shortest_path_length(
            graph, node_src, cutoff=radius_int)

        for radius_decimal in numpy.arange(0, 1, 0.1):
            radius_decimal = round(radius_decimal, 2)
            radius = radius_int + radius_decimal

            len_ball = 0
            for node in g:
                d = scipy.spatial.distance.euclidean(node_src, node)
                if d <= radius:
                    len_ball += 1

            if len_ball == len_max_ball[radius]:
                max_radius_ball = radius
            else:
                return max_radius_ball

    return max_radius_ball


def get_max_radius_ball(graph, node_src):
    max_radius_ball = 0
    for radius in numpy.arange(0, 15, 0.1):
        radius = round(radius, 2)
        len_ball = len(ball(graph, node_src, radius))

        if len_ball >= len_max_ball[radius]:
            max_radius_ball = radius
        else:
            break

    return max_radius_ball


def get_max_radius_floating_ball(graph, node_src):

    max_radius = get_max_radius_ball(graph, node_src)
    node_save = node_src

    labelize = list()
    labelize.append(node_src)

    nodes = list()
    nodes += networkx.all_neighbors(graph, node_src)
    while nodes:
        node = nodes.pop()

        if node not in labelize:
            labelize.append(node)

            radius = get_max_radius_ball(graph, node)
            d = scipy.spatial.distance.euclidean(node_src, node)
            if d <= radius:
                nodes += networkx.all_neighbors(graph, node)

                if radius >= max_radius:
                    max_radius = radius
                    node_save = node

    return max_radius, node_save


def get_max_radius_floating_ball_2(graph, node_src, nodes):

    max_radius = get_max_radius_ball(graph, node_src)
    for node in nodes:
        r = get_max_radius_ball(graph, node)
        d = scipy.spatial.distance.euclidean(node_src, node)

        if d <= r and r >= max_radius:
            max_radius = r

    return max_radius
