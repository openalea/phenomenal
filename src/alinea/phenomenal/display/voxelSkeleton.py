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

import math
import mayavi.mlab
import collections

from .voxels import (plot_voxels)
from .center_axis import (plot_center_axis)
from .colormap import random_color_map
# ==============================================================================


def show_voxel_skeleton(voxel_skeleton,
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

    for vs in voxel_skeleton.voxel_segments:

        if vs.label is None or vs.label != "unknown":
            for polyline in vs.polylines:
                plot_voxels(polyline,
                            vs.voxels_size,
                            color=(0.0, 0.0, 1.0))

            if with_voxels:
                plot_voxels(vs.voxels_position,
                            vs.voxels_size * 0.25,
                            # color=(0.0, 1.0, 0.0))
                            )

    print("Number of segments : ", len(voxel_skeleton.voxel_segments))

    mayavi.mlab.view(azimuth=azimuth,
                     elevation=elevation,
                     distance=distance,
                     focalpoint=focalpoint)

    mayavi.mlab.show()


def show_voxel_skeleton_labeled(voxel_skeleton,
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

    color_label = {"cornet_leaf": (1, 0, 0),
                   "mature_leaf": None,
                   "stem": (0, 0, 0),
                   "unknown": (1, 1, 1)}

    nb_label = collections.defaultdict(lambda: 0)

    vs = voxel_skeleton.get_stem()
    plot_voxels(vs.voxels_position, vs.voxels_size,
                color=(0.0, 0.0, 0.0))

    for vs in voxel_skeleton.voxel_segments:
        nb_label[vs.label] += 1
        color = color_label[vs.label]
        plot_voxels(vs.voxels_position, vs.voxels_size / 2.0, color=color)

        for polyline in vs.polylines:
            plot_voxels(polyline, vs.voxels_size / 2.0, color=(1, 1, 1))

    s = ("Mature leaf {nb_mature_leaf}\n"
         "Non Mature leaf {nb_non_mature_leaf}\n"
         "Unknown size {nb_unknown}".format(
            nb_mature_leaf=nb_label['mature_leaf'],
            nb_non_mature_leaf=nb_label['cornet_leaf'],
            nb_unknown=nb_label['unknown']))

    mayavi.mlab.text3d(-500, -500, -500, s, scale=50, color=(1, 1, 1))

    mayavi.mlab.view(azimuth=azimuth,
                     elevation=elevation,
                     distance=distance,
                     focalpoint=focalpoint)

    mayavi.mlab.show()




def plot_voxel_skeleton_labeled_with_info(voxel_skeleton):

    random_color_leaf = random_color_map()

    color_label = {"cornet_leaf": (0.9, 0.1, 0.1),
                   "mature_leaf": None,
                   "stem": (0.0, 0.0, 0.0),
                   "unknown": (1.0, 1.0, 1.0)}

    nb_label = collections.defaultdict(lambda: 0)

    for vs in voxel_skeleton.voxel_segments:

        nb_label[vs.label] += 1

        if 'order' in vs.info:
            color = tuple(random_color_leaf[int(vs.info['order'])])
        else:
            color = color_label[vs.label]

        plot_voxels(vs.voxels_position, vs.voxels_size, color=color)

        if ((vs.label == "mature_leaf" or vs.label == "cornet_leaf") and
                    'length' in vs.info):
            x, y, z = vs.info['position_tip']

            mayavi.mlab.points3d(x, y, z, mode="sphere",
                                 color=(1, 0, 0),
                                 scale_factor=30)

            x, y, z = vs.info['position_base']
            mayavi.mlab.points3d(x, y, z, mode="sphere",
                                 color=(0, 0, 1),
                                 scale_factor=30)

            s = ("{length}\n{max_width}\n{mean_width}".format(
                length=int(vs.info['length']) / 10.0,
                max_width=int(vs.info['width_max']) / 10.0,
                mean_width=int(vs.info['width_mean']) / 10.0))

            xt, yt, zt = vs.info['position_tip']
            mayavi.mlab.text3d(xt, yt, zt, s,
                               scale=30,
                               color=(0, 0, 1))

            xb, yb, zb = vs.info['position_base']
            xm, ym, zm = vs.info['vector_mean']
            mayavi.mlab.quiver3d(xb, yb, zb,
                                 xm, ym, zm,
                                 line_width=5.0,
                                 scale_factor=1,
                                 color=(1, 1, 1))

        if vs.label == "mature_leaf" and 'vector_mean_one_quarter' in vs.info:
            xb, yb, zb = vs.info['position_base']
            xm, ym, zm = vs.info['vector_mean_one_quarter']
            mayavi.mlab.quiver3d(xb, yb, zb,
                                 xm, ym, zm,
                                 line_width=5.0,
                                 scale_factor=2,
                                 color=(0, 0, 1))


def show_voxel_skeleton_labeled_with_info(voxel_skeleton,
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

    plot_voxel_skeleton_labeled_with_info(voxel_skeleton)

    mayavi.mlab.view(azimuth=azimuth,
                     elevation=elevation,
                     distance=distance,
                     focalpoint=focalpoint)

    mayavi.mlab.show()


def screenshot_voxel_skeleton_labeled_with_info(voxel_skeleton,
                                          figure_name="",
                                          size=(800, 700),
                                          with_center_axis=False,
                                          azimuths=None,
                                          elevation=None,
                                          distance=None,
                                          focalpoint=None):

    mayavi.mlab.figure(figure=figure_name, size=size)

    if with_center_axis:
        plot_center_axis()

    plot_voxel_skeleton_labeled_with_info(voxel_skeleton)

    if azimuths is None:
        azimuths = [None]

    images = list()
    for azimuth in azimuths:

        mayavi.mlab.view(azimuth=azimuth,
                         elevation=elevation,
                         distance=distance,
                         focalpoint=focalpoint)

        images.append(mayavi.mlab.screenshot())

    mayavi.mlab.close()

    return images


def screenshot_voxel_skeleton_labeled(voxel_skeleton,
                                      figure_name="",
                                      size=(800, 700),
                                      with_center_axis=False,
                                      azimuths=None,
                                      elevation=None,
                                      distance=None,
                                      focalpoint=None):

    mayavi.mlab.figure(figure=figure_name, size=size)

    if with_center_axis:
        plot_center_axis()

    nb_non_mature_leaf, nb_mature_leaf, unknown_size = 0, 0, 0

    for vs in voxel_skeleton.voxel_segments:
        if vs.label == "unknown":
            plot_voxels(vs.voxels_position, vs.voxels_size,
                        color=(0.1, 0.9, 0.9))
            unknown_size += len(vs.voxels_position)

    for vs in voxel_skeleton.voxel_segments:
        if vs.label == "cornet_leaf":
            plot_voxels(vs.voxels_position, vs.voxels_size,
                        color=(0.9, 0.1, 0.1))
            nb_non_mature_leaf += 1

    for vs in voxel_skeleton.voxel_segments:
        if vs.label == "mature_leaf":
            plot_voxels(vs.voxels_position, vs.voxels_size,
                        color=None)
            nb_mature_leaf += 1

    for vs in voxel_skeleton.voxel_segments:
        if vs.label == "stem":
            plot_voxels(vs.voxels_position, vs.voxels_size,
                        color=(0.0, 0.0, 0.0))

    s = ("Mature leaf {nb_mature_leaf}\n"
         "Non Mature leaf {nb_non_mature_leaf}\n"
         "Unknown size {nb_unknown}".format(
            nb_mature_leaf=nb_mature_leaf,
            nb_non_mature_leaf=nb_non_mature_leaf,
            nb_unknown=unknown_size))

    mayavi.mlab.text3d(-500, -500, -500, s, scale=50, color=(1, 1, 1))

    images = list()

    for azimuth in azimuths:

        mayavi.mlab.view(azimuth=azimuth,
                         elevation=elevation,
                         distance=distance,
                         focalpoint=focalpoint)

        images.append(mayavi.mlab.screenshot())

    mayavi.mlab.close()

    return images
