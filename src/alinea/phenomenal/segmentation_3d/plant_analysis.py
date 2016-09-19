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
import scipy.interpolate
import collections
import math

from alinea.phenomenal.segmentation_3d.plane_interception import (
    compute_closest_nodes)

# ==============================================================================


def get_max_distance(node, nodes):
    max_distance = 0
    max_node = node

    for n in nodes:
        distance = numpy.linalg.norm(numpy.array(node) - numpy.array(n))
        max_distance = max(max_distance, distance)
        max_node = n

    return max_node, max_distance


def voxel_analysis(voxel, voxel_size):

    info = dict()

    info['voxel_size'] = voxel_size
    info['number_of_voxel'] = len(voxel)

    return info


def voxels_path_analysis(voxel, path, voxel_size,
                         verbose=False,
                         distance_plane=0.75):

    info = collections.defaultdict()

    set_voxel = set(list(voxel))
    arr_voxel = numpy.array(list(voxel))
    planes, closest_nodes = compute_closest_nodes(
        arr_voxel,
        path,
        radius=8,
        verbose=verbose,
        dist=distance_plane * voxel_size)

    # ==========================================================================

    closest_nodes = [nodes for nodes in closest_nodes
                     if len(set_voxel.intersection(set(nodes))) > 0]

    # print(len(closest_nodes), len(path))

    # ==========================================================================

    width = list()
    for nodes in closest_nodes:
        pt1, _ = get_max_distance(nodes[0], nodes)
        pt2, distance = get_max_distance(pt1, nodes)
        width.append(distance)

    # info['width'] = width
    info['max_width'] = max(width)
    info['mean_width'] = sum(width) / float(len(width))
    info['min_width'] = min(width)

    # ==========================================================================

    centred_path = [numpy.array(nodes).mean(axis=0) for nodes in closest_nodes]
    arr_centred_path = numpy.array(centred_path).transpose()

    k = 5
    while len(centred_path) <= k and k > 1:
        k -= 1

    tck, u = scipy.interpolate.splprep(arr_centred_path, k=k)
    xxx, yyy, zzz = scipy.interpolate.splev(numpy.linspace(0, 1, 500), tck)

    real_path = [(x, y, z) for x, y, z in zip(xxx, yyy, zzz)]

    # info['polyline'] = real_path

    # ==========================================================================

    length = 0
    for n1, n2 in zip(path, path[1:]):
        length += numpy.linalg.norm(numpy.array(n1) - numpy.array(n2))

    # ==========================================================================

    info['lenght'] = length
    info['height'] = real_path[-1][2]
    info['base'] = real_path[0][2]

    # ==========================================================================

    x, y, z = real_path[0]
    vectors = list()
    for i in range(1, len(path)):
        xx, yy, zz = path[i]

        v = (xx - x, yy - y, zz - z)
        vectors.append(v)

    vector_mean = numpy.array(vectors).mean(axis=0)

    x, y, z = vector_mean
    angle = math.atan2(y, x)
    angle = angle + 2 * math.pi if angle < 0 else angle
    info['azimuth'] = angle

    # ==========================================================================

    info['voxel_size'] = voxel_size
    info['number_of_voxel'] = len(voxel)

    return info


def info_plant_empty():
    info = dict()

    info['max_width'] = None
    info['mean_width'] = None
    info['min_width'] = None
    info['lenght'] = None
    info['height'] = None
    info['base'] = None
    info['azimuth'] = None
    info['voxel_size'] = None
    info['number_of_voxel'] = None

    return info


def plant_info_empty():

    plant_info = dict()
    labels = ['stem', 'cornet']
    for i in range(0, 20):
        labels.append('leaf_' + str(i))
    for i in range(0, 20):
        labels.append('connected_leaf_' + str(i))

    for label in labels:
        info = info_plant_empty()

        for info_key in list(info.keys()):
            plant_info[label + '_' + info_key] = info.pop(info_key)

    return plant_info


def plant_analysis(labeled_voxels, labeled_path, voxel_size):

    plant_info = dict()
    for label in labeled_voxels:

        voxel = labeled_voxels[label]

        if label in labeled_path:
            path = labeled_path[label]
            info = voxels_path_analysis(voxel, path, voxel_size)
        else:
            info = voxel_analysis(voxel, voxel_size)

        for info_key in list(info.keys()):
            plant_info[label + '_' + info_key] = info.pop(info_key)

    return plant_info




