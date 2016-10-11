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
import networkx
import numpy
import scipy.interpolate
import sklearn.cluster
import scipy.spatial
import matplotlib

from alinea.phenomenal.data_structure import (
    bounding_box)

from alinea.phenomenal.segmentation_3d.graph import (
    create_graph)

from alinea.phenomenal.segmentation_3d.peak_detection import (
    peak_detection)

from alinea.phenomenal.segmentation_3d.plane_interception import (
    compute_closest_nodes)

from alinea.phenomenal.data_structure import voxel_centers_to_image_3d

# ==============================================================================


def find_base_stem_position(voxel_centers, voxel_size, neighbor_size=50):

    image_3d = voxel_centers_to_image_3d(voxel_centers, voxel_size)

    x = int(round(0 - image_3d.world_coordinate[0] / image_3d.voxel_size))
    y = int(round(0 - image_3d.world_coordinate[1] / image_3d.voxel_size))

    k = neighbor_size / voxel_size
    x_len, y_len, z_len = image_3d.shape

    roi = image_3d[max(x - k, 0): min(x + k, x_len),
                   max(y - k, 0): min(y + k, y_len),
                   :]

    xx, yy, zz = numpy.where(roi == 1)

    min_z_value = numpy.min(zz)
    index_min_z_value = numpy.where(zz == min_z_value)
    mean_float_point = numpy.array([numpy.mean(xx[index_min_z_value]),
                                    numpy.mean(yy[index_min_z_value]),
                                    numpy.mean(zz[index_min_z_value])])

    mean_point = None
    min_dist = float('inf')
    for xxx, yyy, zzz in zip(xx, yy, zz):
        pt = numpy.array([xxx, yyy, zzz])
        dist = numpy.linalg.norm(mean_float_point - pt)
        if dist < min_dist:
            min_dist = dist
            mean_point = pt

    stem_base_position = (max(x - k, 0) + mean_point[0],
                          max(y - k, 0) + mean_point[1],
                          mean_point[2])

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


def merge(graph, voxels, remaining_voxels, percentage=50):

    voxels_neighbors = list()
    for node in voxels:
        voxels_neighbors += graph[node].keys()
    voxels_neighbors = set(voxels_neighbors)

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


def get_max_distance(node, nodes):
    max_distance = 0
    max_node = node

    for n in nodes:
        distance = abs(numpy.linalg.norm(numpy.array(node) - numpy.array(n)))
        if distance >= max_distance:
            max_distance = distance
            max_node = n

    return max_node, max_distance


def get_length_point_cloud(nodes):

    if len(nodes) >= 4:
        arr = numpy.array(nodes).astype(float)
        hull = scipy.spatial.ConvexHull(arr, qhull_options="QJ")
        nodes = hull.vertices

    max_dist = 0
    for n in nodes:
        pt, dist = get_max_distance(n, nodes)

        if dist > max_dist:
            max_dist = dist

    return max_dist


def smooth(x, window_len=11, window='hanning'):
    """smooth the data using a window with requested size.

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.

    input:
        x: the input signal
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal

    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)

    see also:

    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter

    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")
    if window_len<3:
        return x

    if window not in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("Window is on of 'flat', 'hanning',"
                         " 'hamming', 'bartlett', 'blackman'")

    s = numpy.r_[x[(window_len - 1) // 2:0:-1], x, x[-1:-window_len // 2:-1]]

    if window == 'flat': #moving average
        w = numpy.ones(window_len, 'd')
    else:
        w = eval('numpy.'+window+'(window_len)')

    y = numpy.convolve(w/w.sum(), s, mode='valid')

    return y


def peak_stem_detection(closest_nodes, leafs):
    nodes_length = map(float, map(len, closest_nodes))

    distances = list()
    for i in range(len(closest_nodes)):
        distance = get_length_point_cloud(closest_nodes[i])
        distances.append(float(distance))

    values_stem = [1] * len(closest_nodes)
    for i in range(len(closest_nodes)):
        for voxels, paths in leafs:
            v = len(set(closest_nodes[i]).intersection(voxels))
            values_stem[i] += float(v) / float(len(closest_nodes[i]))

    # stop = 0
    # for i in range(len(values_stem)):
    #     if values_stem[i] <= 2:
    #         stop = i
    #         break

    # values_stem = values_stem[:stop]
    # nodes_length = nodes_length[:stop]

    mix = list()
    for i in range(len(values_stem)):
        mix.append(float(distances[i]) * float(nodes_length[i]) /
                   float(values_stem[i]))

    stop = mix.index(max(mix))
    # mix = mix[:stop]

    def show_stop_peak(values, factor=0.50):

        # Normalize
        values = [v / float(sum(values)) for v in values]

        # Smooth
        values = smooth(numpy.array(values))

        # Peak
        lookahead = 1

        max_peaks, min_peaks = peak_detection(values, lookahead)

        # min_peaks = [(0, values[0])] + min_peaks

        # # TODO : hack !
        # mmin_peaks = list()
        # for index, value in min_peaks:
        #     if index <= stop or len(mmin_peaks) <= 2:
        #         mmin_peaks.append((index, stop))
        #
        # min_peaks = mmin_peaks

        min_peaks_values = [v for i, v in min_peaks]
        a = numpy.array(min_peaks_values).reshape((len(min_peaks_values), 1))

        meanshift = sklearn.cluster.MeanShift(
            bandwidth=min_peaks_values[0] * factor)
        meanshift.fit(a)

        ref_label = meanshift.labels_[0]

        min_peaks_stem = list()
        min_peaks_stem.append((0, values[0]))
        for (index, value), label in zip(min_peaks, meanshift.labels_):
            if ref_label == label:
                if len(min_peaks_stem) <= 1 or index <= stop:
                    min_peaks_stem.append((index, value))


        # color = {0: 'bo', 1: 'ro', 2: 'go', 3: 'co', 4: 'ko'}
        # for (index, value), label in zip(min_peaks, meanshift.labels_):
        #     if label not in color:
        #         matplotlib.pyplot.plot(index, value, 'ko')
        #     else:
        #         matplotlib.pyplot.plot(index, value, color[label])

        return min_peaks_stem

    # def plot_values(values, color):
    #     # Normalize
    #     values = [v / float(sum(values)) for v in values]
    #
    #     # Smooth
    #     values = smooth(numpy.array(values))
    #
    #     matplotlib.pyplot.plot(range(len(values)), values, color)
    #
    #     max_peaks, min_peaks = peak_detection(values, 1)
    #     min_peaks = [(0, values[0])] + min_peaks
    #     for index, value in min_peaks:
    #         matplotlib.pyplot.plot(index, value, 'ro')
    #
    # matplotlib.pyplot.figure()
    # plot_values(nodes_length, 'b')
    # plot_values(mix, 'g')
    # plot_values(values_stem, 'r')
    # min_peaks_stem = show_stop_peak(nodes_length)
    # for index, value in min_peaks_stem:
    #     matplotlib.pyplot.plot(index, value, 'bo')
    #
    # min_peaks_stem = show_stop_peak(mix, 2.0)
    # for index, value in min_peaks_stem:
    #     matplotlib.pyplot.plot(index, value, 'bo')
    # matplotlib.pyplot.show()

    # show_stop_peak(distances, 'g')
    # show_stop_peak(mix, 'r')
    min_peaks_stem = show_stop_peak(nodes_length)

    # ==========================================================================

    # matplotlib.pyplot.figure()
    distances = smooth(numpy.array(distances))
    # matplotlib.pyplot.plot(range(len(distances)), distances, 'b')
    # for index, value in min_peaks_stem:
    #     matplotlib.pyplot.plot(index, distances[index], 'ro')
    # matplotlib.pyplot.show()

    return min_peaks_stem, distances


def stem_detection_2(stem_segment_voxel, stem_segment_path, leafs, voxel_size,
                     distance_plane=0.75):

    # ==========================================================================

    arr_stem_segment_voxel = numpy.array(list(stem_segment_voxel))

    planes, closest_nodes = compute_closest_nodes(
        arr_stem_segment_voxel, stem_segment_path, radius=8,
        dist=distance_plane * voxel_size)

    # ==========================================================================

    stem_segment_centred_path = [
        numpy.array(nodes).mean(axis=0) for nodes in closest_nodes]
    # ==========================================================================

    min_peaks_stem, distances = peak_stem_detection(closest_nodes, leafs)

    # ==========================================================================

    stem_voxel = set()
    radius = dict()
    stem_centred_path_min_peak = list()
    max_index_min_peak = 0
    for index, value in min_peaks_stem:
        max_index_min_peak = max(max_index_min_peak, index)
        radius[index] = distances[index] / 2.0
        stem_centred_path_min_peak.append(stem_segment_centred_path[index])
        stem_voxel = stem_voxel.union(closest_nodes[index])

    # ==========================================================================
    # Interpolate

    new_centred_shorted_path = list()
    # new_centred_shorted_path.append(stem_segment_centred_path[0])
    new_centred_shorted_path += stem_centred_path_min_peak

    len_new_centred_shorted_path = len(new_centred_shorted_path)
    new_centred_shorted_path = numpy.array(new_centred_shorted_path).transpose()

    k = 2
    if len_new_centred_shorted_path <= k:
        k = 1

    tck, u = scipy.interpolate.splprep(new_centred_shorted_path, k=k)
    xxx, yyy, zzz = scipy.interpolate.splev(numpy.linspace(0, 1, 500), tck)

    # ==========================================================================

    arr_stem_voxels = set()
    for nodes in closest_nodes[:max_index_min_peak + 1]:
        arr_stem_voxels = arr_stem_voxels.union(set(nodes))

    arr_stem_voxels = numpy.array(list(arr_stem_voxels))

    stem_top = set(closest_nodes[max_index_min_peak])

    # ==========================================================================

    def get_nodes_radius(center, points, radius):

        x, y, z = center

        result = numpy.sqrt((points[:, 0] - x) ** 2 +
                            (points[:, 1] - y) ** 2 +
                            (points[:, 2] - z) ** 2)

        index = numpy.where(result <= numpy.array(radius))
        result = set(map(tuple, list(points[index])))

        return result

    real_path = list()
    for i in range(len(xxx)):

        index = int(i * max_index_min_peak / 500.0)
        ii = min([ind for ind in radius.keys() if index < ind])
        r = radius[ii]

        # print("Radius :", i, r)

        x, y, z = xxx[i], yyy[i], zzz[i]
        real_path.append((x, y, z))
        result = get_nodes_radius((x, y, z), arr_stem_voxels, r)
        stem_voxel = stem_voxel.union(result)

    not_stem_voxel = set(stem_segment_voxel).difference(stem_voxel)

    stem_path = stem_segment_path[:max_index_min_peak + 1]

    return stem_voxel, not_stem_voxel, stem_path, stem_top


def stem_segmentation(voxel_centers, all_shorted_path_down,
                      distance_plane_1=4,
                      distance_plane_2=0.50,
                      voxel_size=4):

    array_voxel_centers = numpy.array(voxel_centers)

    index = numpy.argmax(array_voxel_centers[:, 2])
    x_top, y_top, z_top = array_voxel_centers[index]

    stem_voxel_path = all_shorted_path_down[(x_top, y_top, z_top)]

    # import mayavi.mlab
    #
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

    # ==========================================================================
    # Get normal of the path and intercept voxel, plane

    planes, closest_nodes = compute_closest_nodes(
        array_voxel_centers, stem_voxel_path, radius=8,
        dist=distance_plane_1 * voxel_size)

    # ==========================================================================
    # Detect peak on graphic

    nodes_length = map(len, closest_nodes)
    lookahead = int(len(closest_nodes) / 50.0)
    nodes_length = [float(n) for n in nodes_length]

    max_peaks, min_peaks = peak_detection(nodes_length, lookahead)

    stop = maize_corner_detection(nodes_length, min_peaks)

    # import matplotlib.pyplot
    # matplotlib.pyplot.figure()
    # matplotlib.pyplot.plot(range(len(nodes_length)), nodes_length)
    #
    # for index, _ in min_peaks:
    #
    #     matplotlib.pyplot.plot(index, nodes_length[index], 'bo')
    #
    # matplotlib.pyplot.plot(stop, nodes_length[stop], 'ro')
    # matplotlib.pyplot.show()

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

    stem_top = set(closest_nodes[-1])

    arr_stem_voxels = set()
    for nodes in closest_nodes:
        arr_stem_voxels = arr_stem_voxels.union(set(nodes))
    arr_stem_voxels = numpy.array(list(arr_stem_voxels))

    # ==========================================================================
    # Compute radius

    # TODO : Wrong !!!!!!
    radius = list()
    radius.append(None)
    for index, value in stem_min_peaks:
        nodes = closest_nodes[index]

        pt1, _ = get_max_distance(nodes[0], nodes)
        pt2, distance = get_max_distance(pt1, nodes)
        radius.append(distance / 2.0)

    radius[0] = radius[1]

    # ==========================================================================
    # Interpolate

    new_centred_shorted_path = list()
    new_centred_shorted_path.append(stem_centred_path[0])
    new_centred_shorted_path += stem_centred_path_min_peak
    len_new_centred_shorted_path = len(new_centred_shorted_path)
    new_centred_shorted_path = numpy.array(new_centred_shorted_path).transpose()

    k = 2
    if len_new_centred_shorted_path <= k:
        k = 1

    tck, u = scipy.interpolate.splprep(new_centred_shorted_path, k=k)
    xxx, yyy, zzz = scipy.interpolate.splev(numpy.linspace(0, 1, 500), tck)

    # ==========================================================================

    def get_nodes_radius(center, points, radius):

        x, y, z = center

        result = numpy.sqrt((points[:, 0] - x) ** 2 +
                            (points[:, 1] - y) ** 2 +
                            (points[:, 2] - z) ** 2)

        index = numpy.where(result <= numpy.array(radius))
        result = set(map(tuple, list(points[index])))

        return result

    score = len(xxx) / len(radius)

    j = 0
    r = voxel_size
    for i in range(len(xxx)):
        if i % score == 0 and j < len(radius):
            r = radius[j]
            j += 1

        x, y, z = xxx[i], yyy[i], zzz[i]

        result = get_nodes_radius((x, y, z), arr_stem_voxels, r)
        stem_voxel = stem_voxel.union(result)

    not_stem_voxel = set(voxel_centers).difference(stem_voxel)

    # ==========================================================================
    # stem_top = set()
    # r = radius[-1]
    # x, y, z = xxx[-1], yyy[-1], zzz[-1]
    # get_nodes_radius((x, y, z), arr_stem_top, r)

    # ==========================================================================

    return stem_voxel, not_stem_voxel, stem_voxel_path, stem_top

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
            verbose=True)

        # show_list_points_3d(closest_nodes)

        leaf = set().union(*closest_nodes)
        leaf = leaf.intersection(connected_components)
        remain = set(voxels).difference(leaf)

        if verbose:
            print("len of connected_component :", len(voxels))
            print("len of not_leaf :", len(remain))
            print("len of leaf  :", len(leaf))

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
