# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
from __future__ import print_function, absolute_import

import numpy
import scipy.interpolate
import scipy.spatial
import scipy.signal

from .peak_detection import (peak_detection, smooth)
from .plane_interception import (
    intercept_points_along_path_with_planes,
    intercept_points_along_polyline_with_ball,
    max_distance_in_points)
# ==============================================================================


def maize_stem_peak_detection(values, stop_index):

    if len(values) > 15:
        nodes_length_smooth2 = list(smooth(numpy.array(values), window_len=15))
        max_peaks_smooth2, min_peaks_smooth2 = peak_detection(
            nodes_length_smooth2, order=3)
        stop_index = max([i for i, v in min_peaks_smooth2 if i <= stop_index])

    max_peaks, min_peaks = peak_detection(values, order=3)
    min_peaks = [(i, v) for i, v in min_peaks if i <= stop_index]
    if len(min_peaks) <= 1:
        min_peaks = [(0, values[0]),
                     (1, values[1])] + min_peaks
    min_peaks = list(set(min_peaks))

    return min_peaks


def get_nodes_radius(center, points, radius):
    x, y, z = center

    result = numpy.sqrt((points[:, 0] - x) ** 2 +
                        (points[:, 1] - y) ** 2 +
                        (points[:, 2] - z) ** 2)

    index = numpy.where(result <= numpy.array(radius))
    result = set(map(tuple, list(points[index])))

    return result


def stem_detection(stem_segment_voxel, stem_segment_path, voxels_size,
                   graph, distance_plane=1.00):

    # ==========================================================================

    arr_stem_segment_voxel = numpy.array(list(stem_segment_voxel))
    arr_stem_segment_path = numpy.array(stem_segment_path)

    closest_nodes_planes, _ = intercept_points_along_path_with_planes(
        arr_stem_segment_voxel,
        arr_stem_segment_path,
        distance_from_plane=distance_plane * voxels_size,
        voxels_size=voxels_size,
        points_graph=graph)

    arr_closest_nodes_planes = [numpy.array(list(nodes)) for nodes in
                                closest_nodes_planes]

    distances = list()
    for i in range(len(arr_closest_nodes_planes)):
        distance = max_distance_in_points(arr_closest_nodes_planes[i])
        distances.append(float(distance))
    ball_radius = min(max(max(distances) / 2, 25), 75)

    closest_nodes_ball = intercept_points_along_polyline_with_ball(
        arr_stem_segment_voxel,
        graph,
        arr_stem_segment_path,
        ball_radius=ball_radius)

    nodes_length = map(float, map(len, closest_nodes_ball))
    index_20_percent = int(float(len(nodes_length)) * 0.20)
    stop_index = nodes_length.index((max(nodes_length)))

    if stop_index <= index_20_percent:
        stop_index = len(nodes_length)

    nodes_length = map(float, map(len, arr_closest_nodes_planes))
    min_peaks_stem = maize_stem_peak_detection(nodes_length, stop_index)

    window_length = max(4, len(nodes_length) / 8)
    window_length = window_length + 1 if window_length % 2 == 0 else window_length
    smooth_distances = scipy.signal.savgol_filter(
        numpy.array(distances), window_length=window_length, polyorder=2)

    # ==========================================================================

    stem_segment_centred_path = [
        nodes.mean(axis=0) for nodes in arr_closest_nodes_planes]

    stem_voxel = set()
    radius = dict()
    stem_centred_path_min_peak = list()
    max_index_min_peak = 0
    xx_yy_raw = list()
    for i, _ in min_peaks_stem:
        max_index_min_peak = max(max_index_min_peak, i)
        radius[i] = smooth_distances[i] / 2.0

        xx_yy_raw.append((i, numpy.array(distances)[i] / 2.0))

        stem_centred_path_min_peak.append((i, stem_segment_centred_path[i]))
        stem_voxel = stem_voxel.union(closest_nodes_planes[i])

    # ==========================================================================

    if (0, stem_segment_centred_path[0]) not in stem_centred_path_min_peak:
        stem_centred_path_min_peak.append((0, stem_segment_centred_path[0]))
    stem_centred_path_min_peak.sort(key=lambda x: x[0])
    stem_centred_path_min_peak = [v for i, v in stem_centred_path_min_peak]

    xx_yy_raw.sort(key=lambda x: x[0])
    xx = numpy.array([x for x, y in xx_yy_raw])
    yy_raw = numpy.array([y for x, y in xx_yy_raw])
    radius_raw = numpy.poly1d(numpy.polyfit(
        xx, numpy.array(yy_raw), deg=min(len(min_peaks_stem) - 1, 5)))
    rad = numpy.array(distances)[:max_index_min_peak + 1] / 2.0

    # ==========================================================================
    # Interpolate

    arr_stem_centred_path_min_peak = numpy.array(
        stem_centred_path_min_peak).transpose()
    tck, u = scipy.interpolate.splprep(arr_stem_centred_path_min_peak, k=1)
    xxx, yyy, zzz = scipy.interpolate.splev(numpy.linspace(0, 1, 500), tck)

    # ==========================================================================

    arr_stem_voxels = set()
    for nodes in closest_nodes_planes[:max_index_min_peak + 1]:
        arr_stem_voxels = arr_stem_voxels.union(set(nodes))
    arr_stem_voxels = numpy.array(list(arr_stem_voxels))

    # ==========================================================================

    real_path = list()
    for i in range(len(xxx)):
        r = radius_raw(i * len(rad) / 500.0)

        x, y, z = xxx[i], yyy[i], zzz[i]
        real_path.append((x, y, z))
        result = get_nodes_radius((x, y, z), arr_stem_voxels, r)
        stem_voxel = stem_voxel.union(result)

    not_stem_voxel = stem_segment_voxel - stem_voxel

    stem_path = arr_stem_segment_path[:max_index_min_peak + 1]
    stem_top = set(closest_nodes_planes[max_index_min_peak])

    return stem_voxel, not_stem_voxel, stem_path, stem_top

