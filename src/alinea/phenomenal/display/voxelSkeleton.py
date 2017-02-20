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
                            color=(0.0, 1.0, 0.0))

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

    nb_cornet_leaf, nb_mature_leaf = (0, 0)

    len_voxels_unknown = 0
    for vs in voxel_skeleton.voxel_segments:

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

    print("Number of segments : ", len(voxel_skeleton.voxel_segments))
    print("Number of mature leaf : ", nb_mature_leaf)
    print("Number of cornet leaf: ", nb_cornet_leaf)
    print("Size of unknown voxels: ", len_voxels_unknown)
    print("Number of total leaf", (nb_mature_leaf + nb_cornet_leaf))

    mayavi.mlab.view(azimuth=azimuth,
                     elevation=elevation,
                     distance=distance,
                     focalpoint=focalpoint)

    mayavi.mlab.show()
