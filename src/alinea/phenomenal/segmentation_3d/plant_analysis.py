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
import scipy
import math
# ==============================================================================


def simple_leaf_analysis(voxel_leaf, longest_shortest_path, verbose=False):

    leaf_array = numpy.array(list(voxel_leaf))
    planes, closest_nodes = compute_closest_nodes(leaf_array,
                                                  longest_shortest_path,
                                                  radius=8,
                                                  verbose=verbose,
                                                  dist=1)

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

    # if verbose:
    #     mayavi.mlab.figure("")
    #
    #     plot_points_3d(list(leaf),
    #                    scale_factor=1,
    #                    color=(0.7, 0, 0.1))
    #
    #     plot_points_3d(c_shorted_path,
    #                    scale_factor=1,
    #                    color=(0.1, 0.1, 1))
    #
    #     plot_points_3d(path,
    #                    scale_factor=1,
    #                    color=(0.1, 1, 1))
    #
    #     plot_points_3d(longest_shortest_path,
    #                    scale_factor=1,
    #                    color=(0, 0, 0))
    #
    #     a, b, c = vector_mean
    #     mayavi.mlab.quiver3d(float(x), float(y), float(z),
    #                          float(a), float(b), float(c),
    #                          line_width=2.0,
    #                          scale_factor=2,
    #                          color=(0, 0, 1))
    #
    #     mayavi.mlab.show()

    # if verbose:
    #     matplotlib.pyplot.figure()
    #     matplotlib.pyplot.plot(
    #         range(len(nodes_length)), nodes_length)
    #
    #     matplotlib.pyplot.plot(index_max_node_lgth,
    #                            max_node_lgth,
    #                            'bo')
    #
    #     matplotlib.pyplot.show()

    a, b, c = vector_mean

    return path, distances_max, max_longest, ((float(x), float(y), float(z)),
                                              (float(a), float(b), float(c)))
