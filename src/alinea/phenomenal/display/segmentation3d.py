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
from __future__ import division, print_function, absolute_import

import numpy
import mayavi.mlab

from .voxels import (plot_voxels)
from .center_axis import (plot_center_axis)
# ==============================================================================


def get_vector_mean(path):
    x, y, z = path[0]
    vectors = list()
    for i in range(1, len(path)):
        xx, yy, zz = path[i]

        v = (xx - x, yy - y, zz - z)
        vectors.append(v)

    vector_mean = numpy.array(vectors).mean(axis=0)

    return vector_mean


def show_voxel_point_cloud_segments_with_plant_info(voxel_point_cloud_segments,
                                                    plant_info,
                                    figure_name="",
                                    size=(800, 700),
                                    with_center_axis=False,
                                    azimuth=None,
                                    elevation=None,
                                    distance=None,
                                    focalpoint=None):

    mayavi.mlab.figure(figure=figure_name, size=size)

    if with_center_axis:
        plot_center_axis()

    nb_cornet_leaf, nb_mature_leaf = (0, 0)

    len_voxels_unknown = 0

    # voxels_path = set()
    for vs in voxel_point_cloud_segments.voxel_point_cloud_segment:

        # if len(vs.paths) > 0:
        #     voxels_path = voxels_path.union(*vs.paths)

        if vs.label == "stem":
            plot_voxels(vs.voxels_position, vs.voxels_size,
                        color=(0.0, 0.0, 0.0))

        if vs.label == "mature_leaf":
            plot_voxels(vs.voxels_position, vs.voxels_size,
                        color=None)
            nb_mature_leaf += 1

        if vs.label == "cornet_leaf":
            plot_voxels(vs.voxels_position, vs.voxels_size,
                        color=(0.9, 0.1, 0.1))
            nb_cornet_leaf += 1

        if vs.label == "unknown":
            plot_voxels(vs.voxels_position, vs.voxels_size,
                        color=(0.1, 0.9, 0.9))

            len_voxels_unknown += len(vs.voxels_position)

    for info in plant_info:
        if info["label"] == "mature_leaf":
            x, y, z = info['vector_base']
            xx, yy, zz = info['vector_mean']

            mayavi.mlab.quiver3d(x, y, z,
                                 xx, yy, zz,
                                 line_width=5.0,
                                 scale_factor=1,
                                 color=(1, 1, 1))

    print("Number of mature leaf : ", nb_mature_leaf)
    print("Number of cornet leaf: ", nb_cornet_leaf)
    print("Size of unknown voxels: ", len_voxels_unknown)
    print("Number of total leaf", (nb_mature_leaf + nb_cornet_leaf))

    mayavi.mlab.view(azimuth=azimuth,
                     elevation=elevation,
                     distance=distance,
                     focalpoint=focalpoint)

    mayavi.mlab.show()


def show_voxel_point_cloud_segments(voxel_point_cloud_segments,
                                    figure_name="",
                                    size=(800, 700),
                                    with_center_axis=False,
                                    azimuth=None,
                                    elevation=None,
                                    distance=None,
                                    focalpoint=None):

    mayavi.mlab.figure(figure=figure_name, size=size)

    if with_center_axis:
        plot_center_axis()

    nb_cornet_leaf, nb_mature_leaf = (0, 0)

    len_voxels_unknown = 0

    # voxels_path = set()
    for vs in voxel_point_cloud_segments.voxel_point_cloud_segment:

        # if len(vs.paths) > 0:
        #     voxels_path = voxels_path.union(*vs.paths)

        if vs.label == "stem":
            plot_voxels(vs.voxels_position, vs.voxels_size,
                        color=(0.0, 0.0, 0.0))

        if vs.label == "mature_leaf":
            plot_voxels(vs.voxels_position, vs.voxels_size,
                        color=None)
            nb_mature_leaf += 1

        if vs.label == "cornet_leaf":
            plot_voxels(vs.voxels_position, vs.voxels_size,
                        color=(0.9, 0.1, 0.1))
            nb_cornet_leaf += 1

        if vs.label == "unknown":
            plot_voxels(vs.voxels_position, vs.voxels_size,
                        color=(0.1, 0.9, 0.9))

            len_voxels_unknown += len(vs.voxels_position)

    print("Number of mature leaf : ", nb_mature_leaf)
    print("Number of cornet leaf: ", nb_cornet_leaf)
    print("Size of unknown voxels: ", len_voxels_unknown)
    print("Number of total leaf", (nb_mature_leaf + nb_cornet_leaf))

    mayavi.mlab.view(azimuth=azimuth,
                     elevation=elevation,
                     distance=distance,
                     focalpoint=focalpoint)

    mayavi.mlab.show()


def show_segments(segments, voxels_size,
                  with_voxels=False,
                  figure_name="",
                  size=(800, 700),
                  with_center_axis=False,
                  azimuth=None,
                  elevation=None,
                  distance=None,
                  focalpoint=None):

    mayavi.mlab.figure(figure=figure_name, size=size)

    if with_center_axis:
        plot_center_axis()

    all_voxels = set().union(*[voxels for voxels, path in segments])
    paths = set().union(*[path for voxels, path in segments])

    if with_voxels:
        plot_voxels(all_voxels, voxels_size * 0.25, color=(0, 1, 0))
        plot_voxels(paths, voxels_size, color=(1, 0, 0))
    else:
        plot_voxels(paths, voxels_size, color=(1, 0, 0))

    print("Number of segment detected : ", len(segments))

    mayavi.mlab.view(azimuth=azimuth,
                     elevation=elevation,
                     distance=distance,
                     focalpoint=focalpoint)

    mayavi.mlab.show()


def plot_plane(plane, point):

    def get_point_of_planes(normal, node, radius=5):
        a, b, c = normal
        x, y, z = node

        d = a * x + b * y + c * z

        xx = numpy.linspace(x - radius, x + radius, radius * 2)
        yy = numpy.linspace(y - radius, y + radius, radius * 2)

        xv, yv = numpy.meshgrid(xx, yy)

        zz = - (a * xv + b * yv - d) / c

        return xv, yv, zz

    x, y, z = point
    a, b, c, d = plane

    a = float(round(a, 4) * 1000)
    b = float(round(b, 4) * 1000)
    c = float(round(c, 4) * 1000)

    d = float(max(a, b, c, 1))

    mayavi.mlab.quiver3d(float(x), float(y), float(z),
                         a / d, b / d, c /d,
                         line_width=1.0,
                         scale_factor=0.1)

    xx, yy, zz = get_point_of_planes((a, b, c), (x, y, z), radius=40)
    mayavi.mlab.mesh(xx, yy, zz)
