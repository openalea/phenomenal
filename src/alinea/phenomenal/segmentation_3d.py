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
import gc
import math
import time
import collections

import matplotlib.pyplot
import mayavi.mlab
import networkx
import numpy

import alinea.phenomenal.data_transformation
import alinea.phenomenal.graph
import alinea.phenomenal.viewer
from peakdetect import peakdetect


# ==============================================================================


def compute_planes(data):
    data_mean = data.mean(axis=0)

    # Do an SVD on the mean-centered data.
    uu, dd, vv = numpy.linalg.svd(data - data_mean)

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
    nodes.append(numpy.array(node_src))

    closest_node = list()
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


def compute_closest_nodes(voxels, path, radius=8, verbose=False, dist=0.75):
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

        nodes = get_node_close_to_planes(voxels, node, plane, dist=dist)

        centred_path.append(numpy.array(nodes).mean(axis=0))
        closest_nodes.append(nodes)

    if verbose:
        print "done, in ", time.time() - t0, 'seconds'

    return planes, closest_nodes, centred_path


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

    min_peaks = [index for index, value in min_peaks]
    max_peaks = [index for index, value in max_peaks]

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


def detect_maize_stem(voxel_centers, voxel_size, verbose=False):

    # ==========================================================================
    #
    # matrix, origin = alinea.phenomenal.data_transformation.points_3d_to_matrix(
    #     voxel_centers, voxel_size)
    #
    # # ==========================================================================
    # # Kept the biggest connected group
    # matrix = alinea.phenomenal.data_transformation.kept_biggest_group_connected(
    #     matrix)

    # ==========================================================================
    # Graph creation

    # graph = alinea.phenomenal.graph.create_graph(matrix, verbose=True)

    x_min, y_min, z_min, x_max, y_max, z_max = alinea.phenomenal. \
        data_transformation.limit_points_3d(voxel_centers)

    new_voxel_centers = (numpy.array(voxel_centers) - numpy.array(
        [x_min, y_min, z_min])) / voxel_size
    new_voxel_centers = new_voxel_centers.astype(int)

    graph = alinea.phenomenal.graph.create_graph(
        map(tuple, list(new_voxel_centers)), verbose=True)

    graph = max(networkx.connected_component_subgraphs(graph), key=len)

    new_voxel_centers = numpy.array(networkx.nodes(graph))

    len_x = int((x_max - x_min) / voxel_size + 1)
    len_y = int((y_max - y_min) / voxel_size + 1)
    len_z = int((z_max - z_min) / voxel_size + 1)

    matrix = numpy.zeros((len_x, len_y, len_z), dtype=numpy.uint8)

    for x, y, z in new_voxel_centers:
        matrix[x, y, z] = 1

    origin = (x_min, y_min, z_min)
    # ==========================================================================
    # Get the high points in the matrix and the suposed base plant points

    index = numpy.argmax(new_voxel_centers[:, 2])
    x_top, y_top, z_top = new_voxel_centers[index]
    print 'Node top : ', x_top, y_top, z_top

    x_stem, y_stem, z_stem = alinea.phenomenal.data_transformation. \
        find_position_base_plant(matrix, origin, voxel_size)
    print 'Node base : ', x_stem, y_stem, z_stem

    # ==========================================================================
    # Compute the shorted path

    if verbose:
        t0 = time.time()

    path = networkx.single_source_dijkstra_path(
        graph, (x_stem, y_stem, z_stem), weight="weight")

    shortest_path = path[(x_top, y_top, z_top)]

    if verbose:
        print 'Time all shorted path :', time.time() - t0
        print 'Length of shorted path', len(shortest_path)

        mayavi.mlab.figure("shorted path")
        alinea.phenomenal.viewer.plot_points_3d(
            new_voxel_centers,
            scale_factor=voxel_size * 0.1,
            color=(0.1, 1, 0.1))

        alinea.phenomenal.viewer.plot_points_3d(
            shortest_path,
            scale_factor=voxel_size * 0.5,
            color=(0, 0, 0))

        mayavi.mlab.show()

    # ==========================================================================
    # Get normal of the path and intercept voxel, plane
    #
    planes, closest_nodes, centred_shorted_path = compute_closest_nodes(
        new_voxel_centers, shortest_path, radius=8, verbose=verbose, dist=1)
    # ==========================================================================

    if verbose:

        mayavi.mlab.figure("")

        alinea.phenomenal.viewer.plot_points_3d(
            new_voxel_centers,
            scale_factor=voxel_size * 0.1,
            color=(0.1, 1, 0.1))

        alinea.phenomenal.viewer.plot_points_3d(
            centred_shorted_path,
            scale_factor=voxel_size * 0.5,
            color=(0.1, 0.1, 1))

        alinea.phenomenal.viewer.plot_points_3d(
            shortest_path,
            scale_factor=voxel_size * 0.5,
            color=(0, 0, 0))

        for i in xrange(len(planes)):

            # x, y, z = points_3d[i]
            # a, b, c, d = planes[i]
            #
            # a = float(round(a, 4) * 1000)
            # b = float(round(b, 4) * 1000)
            # c = float(round(c, 4) * 1000)
            #
            # print x, y, z, a, b, c, d
            #
            # mayavi.mlab.quiver3d(float(x), float(y), float(z),
            #                      a, b, c,
            #                      line_width=1.0,
            #                      scale_factor=0.1)
            #
            # xx, yy, zz = get_point_of_planes((a, b, c), (x, y, z), radius=40)
            # mayavi.mlab.mesh(xx, yy, zz)

            alinea.phenomenal.viewer.plot_points_3d(
                closest_nodes[i], scale_factor=voxel_size * 0.1)

        mayavi.mlab.show()

    # ==========================================================================
    # Detect peak on graphic

    nodes_length = map(len, closest_nodes)
    lookahead = int(len(closest_nodes) / 50.0)
    print lookahead

    max_peaks, min_peaks = peak_detection(
        nodes_length, lookahead, verbose=True)

    # ==========================================================================
    # Compute radius
    import scipy.interpolate

    def compute_radius(centred_node, closest_nodes):

        radius = 0
        for node in closest_nodes:
            distance = numpy.linalg.norm(
                numpy.array(node) - numpy.array(centred_node))

            radius = max(radius, distance)

        return radius * 1.2 # TODO : hack

    data = list()
    radius = list()

    data.append(centred_shorted_path[0])
    radius.append(None)
    for index in min_peaks:
        data.append(centred_shorted_path[index])
        radius.append(
            compute_radius(centred_shorted_path[index], closest_nodes[index]))

    data.append(centred_shorted_path[-1])
    radius.append(None)

    radius[0] = radius[1]
    radius[-1] = radius[-2]

    stop = None
    for index, r in enumerate(radius):
        print index, r
        d = r * 2 * voxel_size
        if d > 80: # TODO hack
            stop = index
            break

    if stop:
        data = data[0:stop]
        radius = radius[0:stop]

    data = numpy.array(data).transpose()

    # ==========================================================================
    # Interpolate

    tck, u = scipy.interpolate.splprep(data)
    xxx, yyy, zzz = scipy.interpolate.splev(numpy.linspace(0, 1, 500), tck)

    # ==========================================================================

    print "Interpolate done"


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

    score = len(xxx) / len(radius)
    j = 0

    stem = list()
    for i in xrange(len(xxx)):

        if i % score == 0 and j < len(radius):
            r = radius[j]
            j += 1

        x, y, z = xxx[i], yyy[i], zzz[i]
        stem += compute_ball_integer((x, y, z), r)
    stem = list(set(stem))

    len_x, len_y, len_z = matrix.shape
    m = numpy.zeros_like(matrix, dtype=int)
    for x, y, z in stem:

        xx = max(min(x, len_x - 1), 0)
        yy = max(min(y, len_y - 1), 0)
        zz = max(min(z, len_z - 1), 0)

        m[xx, yy, zz] = 1

    gc.collect()

    # ==========================================================================
    # Supposed Stem voxel


    print "here 1 "

    matrix = matrix.astype(int)
    mm = matrix - m * 2
    xx, yy, zz = numpy.where(mm == -1)
    stem_voxel = list()
    for i in xrange(len(xx)):
        stem_voxel.append((xx[i], yy[i], zz[i]))

    # ==========================================================================
    # Supposed Leaf voxel

    plant_without_stem = matrix - m
    plant_without_stem[plant_without_stem < 0] = 0

    mat = alinea.phenomenal.data_transformation.labeling_matrix(
        plant_without_stem)

    print "here 2 ", numpy.max(mat) + 1

    leafs = list()
    for i in range(1, numpy.max(mat) + 1):
        print i
        xx, yy, zz = numpy.where(mat == i)

        if len(xx) < 2000:

            voxel = list()
            nb = 0
            for i in xrange(len(xx)):
                node = (xx[i], yy[i], zz[i])
                voxel.append(node)

                neighbors = graph.neighbors(node)
                for x, y, z in neighbors:
                    if (x, y, z) in stem_voxel:
                        nb += 1
                        break

            print nb * 100 / len(voxel)

            if nb * 100 / len(voxel) >= 50:
                stem_voxel += voxel
            else:
                leafs.append(voxel)
        else:
            voxel = list()
            for i in xrange(len(xx)):
                voxel.append((xx[i], yy[i], zz[i]))
            leafs.append(voxel)

    # ==========================================================================

    print "Size Stem :", len(stem_voxel)
    print "Number of component :", len(leafs)

    if verbose:
        mayavi.mlab.figure("")

        for leaf in leafs:

            alinea.phenomenal.viewer.plot_points_3d(
                leaf, scale_factor=voxel_size * 0.2)

        alinea.phenomenal.viewer.plot_points_3d(
            stem_voxel,
            scale_factor=voxel_size * 0.2,
            color=(0, 0, 0))

        mayavi.mlab.show()

    gc.collect()

    simple_leaf = list()
    not_simple_leaf = list()

    for leaf in leafs:

        longest_shortest_path = None
        longest_length = 0
        for node in leaf:
            p = path[node]

            if len(p) > longest_length:
                longest_length = len(p)
                longest_shortest_path = p

        if longest_shortest_path:

            if verbose:

                mayavi.mlab.figure("Longest_shortest_path of leaf")

                alinea.phenomenal.viewer.plot_points_3d(
                    new_voxel_centers,
                    scale_factor=voxel_size * 0.1)

                alinea.phenomenal.viewer.plot_points_3d(
                    longest_shortest_path)

                mayavi.mlab.show()

            planes, closest_nodes, _ = compute_closest_nodes(
                new_voxel_centers, longest_shortest_path, radius=8,
                verbose=verbose, dist=1)

            supposed_leaf = list()
            for i in xrange(len(closest_nodes)):
                supposed_leaf += closest_nodes[i]

            supposed_leaf = list(set(supposed_leaf).intersection(leaf))
            # supposed_leaf = [n for n in supposed_leaf if n in leaf]

            print "Supposed leaf :", len(supposed_leaf)
            print "leaf :", len(leaf)
            left = list(set(leaf).difference(set(supposed_leaf)))

            print "Voxel detected : ", len(left), len(supposed_leaf), len(leaf)

            if verbose:

                mayavi.mlab.figure("")

                alinea.phenomenal.viewer.plot_points_3d(
                    new_voxel_centers, scale_factor=voxel_size * 0.1)

                alinea.phenomenal.viewer.plot_points_3d(
                    supposed_leaf,
                    scale_factor=voxel_size * 0.1,
                    color=(0.1, 1, 0.1))

                alinea.phenomenal.viewer.plot_points_3d(
                    left,
                    scale_factor=voxel_size * 0.1,
                    color=(0.1, 0.1, 1))

                mayavi.mlab.show()

            if len(left) == 0:
                simple_leaf.append(supposed_leaf)
            else:

                len_x, len_y, len_z = matrix.shape
                m = numpy.zeros_like(matrix)
                for x, y, z in left:
                    xx = max(min(x, len_x - 1), 0)
                    yy = max(min(y, len_y - 1), 0)
                    zz = max(min(z, len_z - 1), 0)

                    m[xx, yy, zz] = 1

                mat = alinea.phenomenal.data_transformation.labeling_matrix(m)

                other = list()
                is_simple_leaf = True
                for i in range(1, numpy.max(mat) + 1):

                    xx, yy, zz = numpy.where(mat == i)

                    if len(xx) < 2000: # TODO: little hack

                        voxel = list()
                        nb_leaf = 0
                        nb_stem = 0
                        for i in xrange(len(xx)):
                            node = (xx[i], yy[i], zz[i])
                            voxel.append(node)

                            neighbors = graph.neighbors(node)
                            for x, y, z in neighbors:
                                if (x, y, z) in supposed_leaf:
                                    nb_leaf += 1
                                    break
                            for x, y, z in neighbors:
                                if (x, y, z) in stem_voxel:
                                    nb_stem += 1
                                    break

                        print "Percentage leaf:", nb_leaf * 100 / len(voxel)
                        print "Percentage stem:", nb_stem * 100 / len(voxel)
                        print "Number of voxel:", len(voxel), '\n'

                        if nb_leaf * 100 / len(voxel) >= 50:
                            supposed_leaf += voxel
                        elif nb_stem * 100 / len(voxel) >= 50:
                            stem_voxel += voxel
                        elif len(voxel) * voxel_size <= 100: # TODO: hack
                            supposed_leaf += voxel
                        else:
                            is_simple_leaf = False
                            other.append(voxel)
                    else:
                        is_simple_leaf = False

                        voxel = [(xx[i], yy[i], zz[i]) for i in xrange(len(xx))]
                        other.append(voxel)

                if is_simple_leaf:
                    print ":) Simple leaf !"
                    simple_leaf.append(supposed_leaf)
                else:
                    print ":( Not a simple leaf"
                    not_simple_leaf.append(leaf)

                    mayavi.mlab.figure("")

                    alinea.phenomenal.viewer.plot_points_3d(
                        supposed_leaf,
                        scale_factor=voxel_size * 0.1)

                    for voxel in other:
                        alinea.phenomenal.viewer.plot_points_3d(
                            voxel,
                            scale_factor=voxel_size * 0.1)

                    mayavi.mlab.show()

    if verbose:

            mayavi.mlab.figure("")

            alinea.phenomenal.viewer.plot_points_3d(
                stem_voxel, scale_factor=voxel_size * 0.1, color=(0, 0, 0))

            print 'Number of simple_leaf :', len(simple_leaf)
            for leaf in simple_leaf:
                alinea.phenomenal.viewer.plot_points_3d(
                    leaf, scale_factor=voxel_size * 0.1)

            print 'Number of not_simple_leaf :', len(not_simple_leaf)
            for leaf in not_simple_leaf:
                alinea.phenomenal.viewer.plot_points_3d(
                    leaf, scale_factor=voxel_size * 0.1, color=(1, 0.1, 0.1))

            mayavi.mlab.show()

    return None


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
        list_position += alinea.phenomenal.graph.ball(
            graph, floating_node, radius)

    return list(set(list_position))


def get_path_max_radius_ball(graph, path, verbose=False):

    path_max_radius = list()
    for node in path:

        radius = alinea.phenomenal.graph.get_max_radius_ball(
            graph, node)

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

        radius = alinea.phenomenal.graph. \
            get_max_radius_floating_ball_2(graph, node, nodes)

        if verbose:
            print "\n\nNode : ", node, radius

        path_max_radius.append((node, radius))

    return path_max_radius


def get_path_max_radius_floating_ball(graph, path, verbose):
    path_max_radius = list()
    for node in path:
        radius, floating_node = alinea.phenomenal.graph.\
            get_max_radius_floating_ball(graph, node)

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
