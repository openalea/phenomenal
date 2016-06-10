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
import mayavi.mlab
import numpy
import random
# ==============================================================================


def show_points_3d(points_3d,
                   color=None,
                   scale_factor=5,
                   figure_name=""):

    fg = mayavi.mlab.figure(figure_name)
    mayavi.mlab.quiver3d(0, 0, 0, 1, 0, 0, line_width=5.0, scale_factor=100)
    mayavi.mlab.quiver3d(0, 0, 0, 0, 1, 0, line_width=5.0, scale_factor=100)
    mayavi.mlab.quiver3d(0, 0, 0, 0, 0, 1, line_width=5.0, scale_factor=100)
    plot_points_3d(points_3d, color=color, scale_factor=scale_factor)
    mayavi.mlab.show()
    mayavi.mlab.clf(fg)


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
