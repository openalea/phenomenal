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
import mayavi.mlab
import numpy
# ==============================================================================

__all__ = ["show_points_3d",
           "plot_points_3d",
           "plot_3d",
           "show_octree",
           "show_each_stage_of_octree"]

# ==============================================================================


def show_points_3d(points_3d,
                   color=None,
                   scale_factor=1,
                   figure_name=""):

    fg = mayavi.mlab.figure(figure_name)
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


def show_octree(octree, figure_name="", color=None, scale_factor=1):
    fg = mayavi.mlab.figure(figure_name)
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

    leafs = octree.get_leafs()

    depth = octree.root.depth()
    root_size = octree.root.size

    for i in xrange(depth + 1):

        voxel_size = root_size / (2 ** i)

        voxel_centers = [leaf.position for leaf in leafs if
               leaf.data is True and leaf.size == voxel_size]

        if voxel_centers:

            if color is None:
                c = (random.uniform(0, 1),
                     random.uniform(0, 1),
                     random.uniform(0, 1))
            else:
                c = color

            voxel_centers = numpy.array(voxel_centers)
            mayavi.mlab.points3d(
                voxel_centers[:, 0], voxel_centers[:, 1], voxel_centers[:, 2],
                mode='cube',
                color=c,
                scale_factor=voxel_size * scale_factor)

    mayavi.mlab.show()
    mayavi.mlab.clf(fg)


def show_each_stage_of_octree(octree, color=None, scale_factor=1):

    if color is None:
        color = (random.uniform(0, 1),
                 random.uniform(0, 1),
                 random.uniform(0, 1))

    depth = octree.root.depth()
    root_size = octree.root.size

    for i in xrange(depth + 1):
        voxel_size = root_size / (2 ** i)

        nodes = octree.get_nodes_with_size_equal_to(voxel_size)
        voxel_centers = [node.position for node in nodes if node.data is True]

        fg = mayavi.mlab.figure(voxel_size)
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

        if voxel_centers:

            voxel_centers = numpy.array(voxel_centers)
            mayavi.mlab.points3d(
                voxel_centers[:, 0], voxel_centers[:, 1], voxel_centers[:, 2],
                mode='cube',
                color=color,
                scale_factor=voxel_size * scale_factor)

        mayavi.mlab.show()
        mayavi.mlab.clf(fg)
