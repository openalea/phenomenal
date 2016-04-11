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

import alinea.phenomenal.data_transformation
import alinea.phenomenal.graph
import alinea.phenomenal.viewer
# ==============================================================================


def planes(data):
    data_mean = data.mean(axis=0)

    # Do an SVD on the mean-centered data.
    uu, dd, vv = numpy.linalg.svd(data - data_mean)

    return vv[0]

def get_point_of_planes(normal):




def detect_maize_stem(matrix, origin, voxel_size, verbose=False):
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

    # normals = list()
    # for node in shortest_path:
    #     neighbors = get_neighbors(node, shortest_path, 8)
    #
    #     A = numpy.array(neighbors)
    #     B = numpy.ones_like(A)
    #
    #     k, _, _, _ = numpy.linalg.lstsq(A, B[:, 0])
    #
    #     normal = (round(k[0], 4) * 10000,
    #               round(k[1], 4) * 10000,
    #               round(k[2], 4) * 10000)
    #
    #     normals.append(normal)
    #     print normals

    normals = list()
    for node in shortest_path:
        neighbors = get_neighbors(node, shortest_path, 8)

        k = planes(numpy.array(neighbors))

        normal = (round(k[0], 4) * 1000,
                  round(k[1], 4) * 1000,
                  round(k[2], 4) * 1000)

        normals.append(normal)

        print normal

    # A = numpy.array(shortest_path)
    # print A
    #
    #
    #
    # def func(data, params):
    #     x = data[:, 0]
    #     z = data[:, 2]
    #     a, b, c = params
    #
    #     return a * x + z + c
    #
    # def curve_fitting(data, a, b, c):
    #     return func(data, [a, b, c])
    #
    # import scipy.optimize
    # guess = [1, 2, 1]
    # params, _ = scipy.optimize.curve_fit(
    #     curve_fitting, A, A[:, 1], guess, maxfev=1000000)

    # ==========================================================================

    if verbose:

        mayavi.mlab.figure("")

        # A = numpy.array(shortest_path)
        # Y = func(A, params)
        #
        # A[:, 1] = Y
        #
        # points_3d = list()
        # for x, y, z in A:
        #
        #     xx = origin[0] + x * voxel_size
        #     yy = origin[1] + y * voxel_size
        #     zz = origin[2] + z * voxel_size
        #
        #     points_3d.append((xx, yy, zz))
        #
        # alinea.phenomenal.viewer.plot_3d(points_3d)

        points_3d = list()
        for x, y, z in shortest_path:
            xx = origin[0] + x * voxel_size
            yy = origin[1] + y * voxel_size
            zz = origin[2] + z * voxel_size

            points_3d.append((xx, yy, zz))

        alinea.phenomenal.viewer.plot_points_3d(points_3d)

        for i in xrange(len(normals)):
            x, y, z = points_3d[i]
            u, v, w = normals[i]

            mayavi.mlab.quiver3d(x, y, z,
                                 u, v, w,
                                 line_width=1.0,
                                 scale_factor=0.01)

        mayavi.mlab.show()




    exit()
    # ==========================================================================

    path_max_radius = get_path_max_radius_ball(
        graph, shortest_path, verbose=verbose)

    # ==========================================================================

    path_max_radius = detect_corners_plant(path_max_radius, verbose=verbose)

    # ==========================================================================

    stem_positions = get_position_of_path_max_radius(graph, path_max_radius)

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

        path_max_radius.append((node, radius, node))

    if verbose:
        z = numpy.array(path)[:, 2]
        r = numpy.array(path_max_radius)[:, 1]
        matplotlib.pyplot.figure()
        matplotlib.pyplot.plot(z, r)
        matplotlib.pyplot.show()

    return path_max_radius


def get_path_max_radius_floating_ball(graph, path, verbose):
    path_max_radius = list()
    for node in path:
        radius, floating_node = alinea.phenomenal.graph.\
            get_max_radius_floating_ball(graph, node)

        if verbose:
            print "\n\nNode : ", node, radius, floating_node

        path_max_radius.append((node, radius, floating_node))

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
        node, value, _ = path_max_radius[i]

        if value < tmp_max:

            if tmp_max > mmax:
                mmax = tmp_max
                index_max = tmp_index_max
                mmin = tmp_min
                index_min = tmp_index_min

            tmp_max = -1
            tmp_min = 100

        if value > tmp_max:
            tmp_max = value
            tmp_index_max = i

        if value < tmp_min:
            tmp_min = value
            tmp_index_min = i

    if verbose:
        print path_max_radius[index_max], mmax
        print path_max_radius[index_min], mmin

    return path_max_radius[:index_min]
