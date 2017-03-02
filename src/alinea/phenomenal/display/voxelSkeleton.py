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

import mayavi.mlab

from .voxels import (plot_voxels)
from .center_axis import (plot_center_axis)
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

        if vs.label is None:
            plot_voxels(vs.polylines[0],
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

    mayavi.mlab.view(azimuth=azimuth,
                     elevation=elevation,
                     distance=distance,
                     focalpoint=focalpoint)

    mayavi.mlab.show()


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
