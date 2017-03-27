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
import random
import mayavi.mlab

from alinea.phenomenal.display.center_axis import plot_center_axis
# ==============================================================================


def plot_3d(points_3d, color=None, tube_radius=1):
    pts = numpy.array(points_3d)
    pts = pts.astype(int)

    if color is None:
        color = (random.uniform(0, 1),
                 random.uniform(0, 1),
                 random.uniform(0, 1))

    if len(points_3d) > 0:
        mayavi.mlab.plot3d(pts[:, 0], pts[:, 1], pts[:, 2],
                           color=color,
                           tube_radius=tube_radius)

    del pts

    return color

# ==============================================================================
# ==============================================================================


def show_list_voxels(list_voxels_position,
                     list_voxels_size,
                     list_color=None,
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

    plot_list_voxels(list_voxels_position, list_voxels_size,
                     list_color=list_color)

    mayavi.mlab.view(azimuth=azimuth,
                     elevation=elevation,
                     distance=distance,
                     focalpoint=focalpoint)

    mayavi.mlab.show()


def show_voxels(voxels_position, voxels_size,
                color=None,
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

    plot_voxels(voxels_position, voxels_size, color=color)

    mayavi.mlab.view(azimuth=azimuth,
                     elevation=elevation,
                     distance=distance,
                     focalpoint=focalpoint)

    mayavi.mlab.show()


def screenshot_voxels(voxels_position, voxels_size,
                      color=None,
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

    plot_voxels(voxels_position, voxels_size, color=color)

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

# ==============================================================================
# ==============================================================================

def plot_voxels(voxels_position, voxels_size, color=None):

    pts = numpy.array(list(voxels_position))
    pts = pts.astype(int)

    if color is None:
        color = (random.uniform(0, 1),
                 random.uniform(0, 1),
                 random.uniform(0, 1))

    if len(voxels_position) > 0:
        mayavi.mlab.points3d(pts[:, 0], pts[:, 1], pts[:, 2],
                             mode='cube',
                             color=color,
                             scale_factor=voxels_size)

    del pts

    return color


def plot_list_voxels(list_voxels_position, list_voxels_size,
                     list_color=None):

    if list_color is None:
        list_color = [None] * len(list_voxels_position)

    for voxels_position, voxels_size, color in zip(list_voxels_position,
                                                   list_voxels_size,
                                                   list_color):

        plot_voxels(voxels_position, voxels_size, color=color)

# ==============================================================================
# ==============================================================================


def screenshot_list_voxels(list_voxels_position,
                           list_voxels_size,
                           list_color=None,
                           figure_name='',
                           size=(1600, 1400),
                           azimuth=None,
                           elevation=None,
                           distance=None,
                           focalpoint=None,
                           with_center_axis=False):

    mayavi.mlab.figure(figure=figure_name, size=size)

    if with_center_axis:
        plot_center_axis()

    plot_list_voxels(list_voxels_position, list_voxels_size,
                     list_color=list_color)

    mayavi.mlab.view(azimuth=azimuth,
                     elevation=elevation,
                     distance=distance,
                     focalpoint=focalpoint)

    return mayavi.mlab.screenshot()
