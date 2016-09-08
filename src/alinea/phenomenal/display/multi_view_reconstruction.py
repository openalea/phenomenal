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
"""

"""
# ==============================================================================
import random
import numpy
import mayavi.mlab
# ==============================================================================

__all__ = ["show_points_3d",
           "plot_points_3d",
           "plot_3d"]

# ==============================================================================


def show_points_3d(points_3d,
                   color=None,
                   scale_factor=1,
                   figure_name="",
                   notebook=False):

    fg = mayavi.mlab.figure(figure_name, size=(800, 700))
    mayavi.mlab.quiver3d(0, 0, 0,
                         100, 0, 0,
                         line_width=5.0,
                         scale_factor=1,
                         color=(1, 0, 0))

    mayavi.mlab.quiver3d(0, 0, 0,
                         0, 100, 0,
                         line_width=5.0,
                         scale_factor=1,
                         color=(0, 1, 0))

    mayavi.mlab.quiver3d(0, 0, 0,
                         0, 0, 100,
                         line_width=5.0,
                         scale_factor=1,
                         color=(0, 0, 1))

    plot_points_3d(points_3d, color=color, scale_factor=scale_factor)


    mayavi.mlab.show(stop=notebook)

    im = mayavi.mlab.screenshot()

    mayavi.mlab.close()
    return im


def show_list_points_3d(list_points_3d,
                        list_color=None,
                        scale_factor=1,
                        figure_name="",
                        notebook=False):

    fg = mayavi.mlab.figure(figure_name, size=(800, 700))
    mayavi.mlab.quiver3d(0, 0, 0,
                         100, 0, 0,
                         line_width=5.0,
                         scale_factor=1,
                         color=(1, 0, 0))

    mayavi.mlab.quiver3d(0, 0, 0,
                         0, 100, 0,
                         line_width=5.0,
                         scale_factor=1,
                         color=(0, 1, 0))

    mayavi.mlab.quiver3d(0, 0, 0,
                         0, 0, 100,
                         line_width=5.0,
                         scale_factor=1,
                         color=(0, 0, 1))

    if list_color is None:
        list_color = [None] * len(list_points_3d)

    for points_3d, color in zip(list_points_3d, list_color):
        plot_points_3d(list(points_3d), color=color, scale_factor=scale_factor)

    mayavi.mlab.show(stop=notebook)

    im = mayavi.mlab.screenshot()

    mayavi.mlab.close()
    return im


def screenshot_list_voxels(list_points_3d,
                           list_color=None,
                           voxel_size=1,
                           size=(1600, 1400),
                           azimuth=None,
                           elevation=None,
                           distance=None,
                           focalpoint=None):

    fg = mayavi.mlab.figure(size=size)
    mayavi.mlab.quiver3d(0, 0, 0,
                         100, 0, 0,
                         line_width=5.0,
                         scale_factor=1,
                         color=(1, 0, 0))

    mayavi.mlab.quiver3d(0, 0, 0,
                         0, 100, 0,
                         line_width=5.0,
                         scale_factor=1,
                         color=(0, 1, 0))

    mayavi.mlab.quiver3d(0, 0, 0,
                         0, 0, 100,
                         line_width=5.0,
                         scale_factor=1,
                         color=(0, 0, 1))

    if list_color is None:
        list_color = [None] * len(list_points_3d)

    for points_3d, color in zip(list_points_3d, list_color):
        plot_points_3d(list(points_3d),
                       color=color,
                       scale_factor=voxel_size)

    mayavi.mlab.view(azimuth=azimuth,
                     elevation=elevation,
                     distance=distance,
                     focalpoint=focalpoint)

    return mayavi.mlab.screenshot()


def plot_points_3d(points_3d, color=None, scale_factor=5):
    pts = numpy.array(points_3d)
    pts = pts.astype(int)

    if color is None:
        color = (random.uniform(0, 1),
                 random.uniform(0, 1),
                 random.uniform(0, 1))

    if len(points_3d) > 0:
        mayavi.mlab.points3d(pts[:, 0], pts[:, 1], pts[:, 2],
                             mode='cube',
                             color=color,
                             scale_factor=scale_factor)

    del pts

    return color


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


