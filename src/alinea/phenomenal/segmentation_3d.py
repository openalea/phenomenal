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
import time
import matplotlib.pyplot
import mayavi.mlab
import math

import alinea.phenomenal.data_transformation
import alinea.phenomenal.graph
import alinea.phenomenal.viewer
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


def get_node_close_to_planes(graph, node_src, plane):

    closest_node = list()
    closest_node.append(node_src)

    nodes = list()
    nodes += networkx.all_neighbors(graph, node_src)
    while nodes:
        node = nodes.pop()

        if node not in closest_node:
            distance = get_distance_point_to_plane(node, plane)
            if distance < 0.75:
                closest_node.append(node)
                nodes += graph.neighbors(node)

    return closest_node


def detect_maize_stem(matrix, origin, voxel_size, verbose=False):

    # ==========================================================================
    # Kept the biggest connected group
    matrix = alinea.phenomenal.data_transformation. \
        kept_biggest_group_connected(matrix)

    # ==========================================================================
    # Graph creation

    graph = alinea.phenomenal.graph.create_graph(matrix, verbose=True)

    # ==========================================================================
    # Get the high points in the matrix and the suposed base plant points

    xx, yy, zz = numpy.where(matrix == 1)
    j = numpy.argmax(zz)
    x_top, y_top, z_top = xx[j], yy[j], zz[j]
    print 'Node top : ', x_top, y_top, z_top

    x_stem, y_stem, z_stem = alinea.phenomenal.data_transformation. \
        find_position_base_plant(matrix, origin, voxel_size)
    print 'Node base : ', x_stem, y_stem, z_stem

    # ==========================================================================
    # Compute the sorthed path

    if verbose:
        t0 = time.time()

    shortest_path = networkx.shortest_path(
        graph, (x_stem, y_stem, z_stem), (x_top, y_top, z_top), weight="weight")

    if verbose:
        print 'Time shorted path :', time.time() - t0
        print shortest_path

    def get_neighbors(src, path, radius):
        neighbors = list()
        for dst in path:
            if numpy.linalg.norm(numpy.array(dst) - numpy.array(src)) <= radius:
                neighbors.append(dst)

        return neighbors

    # ==========================================================================
    # Get normal of the path and intercept voxel, plane

    normals = list()
    planes = list()
    closest = list()
    size_disc = list()
    centred_shorted_path = list()
    for node in shortest_path:
        x, y, z = node

        neighbors = get_neighbors(node, shortest_path, 8)

        k = compute_planes(numpy.array(neighbors))

        normal = (round(k[0], 4) * 1000,
                  round(k[1], 4) * 1000,
                  round(k[2], 4) * 1000)
        normals.append(normal)

        a, b, c = (k[0], k[1], k[2])
        d = a * x + b * y + c * z
        plane = (a, b, c, d)
        planes.append(plane)

        nodes = get_node_close_to_planes(graph, node, plane)
        nn = numpy.array(nodes)

        centred_shorted_path.append(nn.mean(axis=0))
        closest.append(nodes)
        size_disc.append(len(nodes))

    # ==========================================================================

    # if verbose:
    #
    #     mayavi.mlab.figure("")
    #
    #     voxel_centers = alinea.phenomenal.data_transformation. \
    #         matrix_to_points_3d(matrix, voxel_size, origin=origin)
    #
    #     alinea.phenomenal.viewer.plot_points_3d(
    #         voxel_centers, scale_factor=voxel_size * 0.1)
    #
    #     points_3d = list()
    #     for x, y, z in centred_shorted_path:
    #         xx = origin[0] + x * voxel_size
    #         yy = origin[1] + y * voxel_size
    #         zz = origin[2] + z * voxel_size
    #
    #         points_3d.append((xx, yy, zz))
    #     alinea.phenomenal.viewer.plot_points_3d(points_3d)
    #
    #     points_3d = list()
    #     for x, y, z in shortest_path:
    #         xx = origin[0] + x * voxel_size
    #         yy = origin[1] + y * voxel_size
    #         zz = origin[2] + z * voxel_size
    #
    #         points_3d.append((xx, yy, zz))
    #     alinea.phenomenal.viewer.plot_points_3d(points_3d)
    #
    #     for i in xrange(len(normals)):
    #         x, y, z = points_3d[i]
    #         u, v, w = normals[i]
    #
    #         mayavi.mlab.quiver3d(x, y, z,
    #                              u, v, w,
    #                              line_width=1.0,
    #                              scale_factor=0.1)
    #
    #         xx, yy, zz = get_point_of_planes((u, v, w), (x, y, z), radius=40)
    #         mayavi.mlab.mesh(xx, yy, zz)
    #
    #         pts = list()
    #         for i, j, k in closest[i]:
    #             ii = origin[0] + i * voxel_size
    #             jj = origin[1] + j * voxel_size
    #             kk = origin[2] + k * voxel_size
    #             pts.append((ii, jj, kk))
    #
    #         alinea.phenomenal.viewer.plot_points_3d(pts)

        mayavi.mlab.show()

    # ==========================================================================
    # Detect peak on graphic
    from peakdetect import peakdetect

    max_peaks, min_peaks = peakdetect(size_disc, lookahead=2)
    # ==========================================================================
    # Split peaks in two

    from sklearn.cluster import KMeans

    l = list()
    for index, value in min_peaks:
        l.append(value)
    l = numpy.array(l).reshape((len(l), 1))

    cluster = KMeans(n_clusters=2)
    cluster_min_peak = cluster.fit_predict(l)

    # ==========================================================================

    i_save = 0
    min_peak_stem = list()
    ref_value = cluster_min_peak[i_save]
    for i, v in enumerate(cluster_min_peak):
        if v == ref_value:
            index, value = min_peaks[i_save]
            min_peak_stem.append(index)
        else:
            break


    # ==========================================================================

    if verbose:
        matplotlib.pyplot.figure()
        matplotlib.pyplot.plot(range(len(list(size_disc))), size_disc)

        for i, (index, value) in enumerate(min_peaks):
            if cluster_min_peak[i] == 0:
                matplotlib.pyplot.plot(index, value, 'ro')
            else:
                matplotlib.pyplot.plot(index, value, 'bo')

    matplotlib.pyplot.show()

    # ==========================================================================

    index = min_peak_stem[-1]
    stem_path = shortest_path[:index]
    centred_shorted_path = centred_shorted_path[:index]

    for index in range(0, len(min_peak_stem)):




        shortest_path = networkx.shortest_path(
            graph, (x_stem, y_stem, z_stem), (x_top, y_top, z_top), weight="weight")


    # ==========================================================================

    if verbose:
        mayavi.mlab.figure("")

        voxel_centers = alinea.phenomenal.data_transformation.\
            matrix_to_points_3d(matrix, voxel_size, origin=origin)

        alinea.phenomenal.viewer.plot_points_3d(
            voxel_centers, scale_factor=voxel_size * 0.1)

        points_3d = list()
        for node in stem_path:
            x, y, z = node

            xx = origin[0] + x * voxel_size
            yy = origin[1] + y * voxel_size
            zz = origin[2] + z * voxel_size

            points_3d.append((xx, yy, zz))

        alinea.phenomenal.viewer.plot_points_3d(
            points_3d, scale_factor=voxel_size * 0.5)

        mayavi.mlab.show()

    # ==========================================================================

    points_3d = convert_to_real_point_3d(stem_positions, origin, voxel_size)

    return points_3d


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
