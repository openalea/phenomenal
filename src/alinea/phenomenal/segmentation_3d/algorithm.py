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
import collections

from alinea.phenomenal.segmentation_3d.peak_detection import (
    peak_detection)

from alinea.phenomenal.segmentation_3d.plane_interception import (
    compute_closest_nodes_with_planes)

# ==============================================================================


def merge(graph, voxels, remaining_voxels, percentage=50):

    voxels_neighbors = list()
    for node in voxels:
        voxels_neighbors += graph[node].keys()
    voxels_neighbors = set(voxels_neighbors) - voxels

    subgraph = graph.subgraph(remaining_voxels)

    connected_components = list()
    for voxel_group in networkx.connected_components(subgraph):
        nb = len(voxel_group.intersection(voxels_neighbors))

        if nb * 100 / len(voxel_group) >= percentage:
            voxels = voxels.union(voxel_group)
        else:
            connected_components.append(voxel_group)

    return voxels, voxels_neighbors, connected_components


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

    res = scipy.spatial.distance.pdist(nodes, 'euclidean')

    if len(res) > 0:
        return res.max()
    else:
        return 0


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

    distances_length = list()
    for i in range(len(values_stem)):
        distances_length.append(float(distances[i]) * float(nodes_length[i]))

    mix = list()
    for i in range(len(values_stem)):
        mix.append(float(distances[i]) * float(nodes_length[i]) /
                   float(values_stem[i]))

    # import matplotlib.pyplot
    # from alinea.phenomenal.display.peak import plot_values, show_values

    # show_values([nodes_length],
    #             ['r'],
    #             normalize_values=False,
    #             smooth_values=False,
    #             plot_peak=False)
    #
    # show_values([nodes_length, distances],
    #             ['r', 'g'],
    #             normalize_values=False,
    #             smooth_values=False,
    #             plot_peak=False)
    #
    # show_values([nodes_length, distances, values_stem],
    #             ['r', 'g', 'b'],
    #             normalize_values=False,
    #             smooth_values=False,
    #             plot_peak=False)
    #
    # show_values([nodes_length, distances, values_stem],
    #             ['r', 'g', 'b'],
    #             normalize_values=True,
    #             smooth_values=False,
    #             plot_peak=False)
    #
    # show_values([nodes_length, distances, values_stem, mix],
    #             ['r', 'g', 'b', 'm'],
    #             normalize_values=True,
    #             smooth_values=False,
    #             plot_peak=False)
    #
    # show_values([nodes_length, distances, mix],
    #             ['r', 'g', 'm'],
    #             normalize_values=True,
    #             smooth_values=False,
    #             plot_peak=True)

    stop = mix.index(max(mix))

    # show_values([nodes_length, mix],
    #             ['r', 'm'],
    #             normalize_values=True,
    #             smooth_values=True,
    #             plot_peak=True)
    #

    # label_color = collections.defaultdict(lambda: 'co')
    # label_color[0] = 'ro'
    # label_color[1] = 'bo'
    # label_color[2] = 'go'
    # label_color[3] = 'ko'

    def find_stem_min_peak(values):

        # Normalize
        values = [v / float(sum(values)) for v in values]

        # Smooth
        values = smooth(numpy.array(values),
                        window_len=11,
                        window='hanning')

        values = smooth(numpy.array(values),
                        window_len=11,
                        window='hanning')

        # Peak
        lookahead = 1

        max_peaks, min_peaks = peak_detection(values, lookahead)

        min_peaks_values = [v for i, v in min_peaks if i <= stop]

        if len(min_peaks_values) > 0:

            bandwith = max(values) / 5.0

            # Meanshift
            a = numpy.array(min_peaks_values).reshape(
                (len(min_peaks_values), 1))

            meanshift = sklearn.cluster.MeanShift(
                bandwidth=bandwith)
            meanshift.fit(a)

            # Option, maybe resolve stem cut problem
            c = collections.Counter(meanshift.labels_)
            ref_label = max(c, key=c.get)

            min_peaks_stem = list()
            min_peaks_stem.append((0, values[0]))
            for (index, value), label in zip(min_peaks, meanshift.labels_):
                if ref_label == label:
                    min_peaks_stem.append((index, value))

        else:
            min_peaks_stem = list()
            for i, v in enumerate(values):
                min_peaks_stem.append((i, v))

        return min_peaks_stem

    min_peaks_stem = find_stem_min_peak(nodes_length)

    # import matplotlib.pyplot
    # from alinea.phenomenal.display.peak import plot_values
    # matplotlib.pyplot.figure()
    # plot_values(nodes_length, 'r', plot_peak=True)
    # plot_values(mix, 'm', plot_peak=True)
    # for index, value in min_peaks_stem:
    #     matplotlib.pyplot.plot(index, value, 'bo')
    # matplotlib.pyplot.show()

    distances = smooth(numpy.array(distances))

    return min_peaks_stem, distances


def stem_detection(stem_segment_voxel, stem_segment_path, leafs, voxel_size,
                   distance_plane=0.50):

    # ==========================================================================

    arr_stem_segment_voxel = numpy.array(list(stem_segment_voxel))

    closest_nodes = compute_closest_nodes_with_planes(
        arr_stem_segment_voxel, stem_segment_path, radius=6,
        dist=distance_plane * voxel_size)

    stem_segment_centred_path = [
        numpy.array(nodes).mean(axis=0) for nodes in closest_nodes]

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

        x, y, z = xxx[i], yyy[i], zzz[i]
        real_path.append((x, y, z))
        result = get_nodes_radius((x, y, z), arr_stem_voxels, r)
        stem_voxel = stem_voxel.union(result)

    not_stem_voxel = stem_segment_voxel - stem_voxel
    stem_path = stem_segment_path[:max_index_min_peak + 1]

    return stem_voxel, not_stem_voxel, stem_path, stem_top

