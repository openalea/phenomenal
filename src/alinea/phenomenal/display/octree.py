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
import random
import mayavi.mlab
import numpy

# ==============================================================================

__all__ = ["show_octree",
           "show_each_stage_of_octree"]
# ==============================================================================


def show_octree(octree,
                scale_factor=1,
                color=None,
                figure_name="",
                size=(800, 700),
                with_center_axis=False,
                azimuth=None,
                elevation=None,
                distance=None,
                focalpoint=None):

    fg = mayavi.mlab.figure(figure=figure_name, size=size)

    if with_center_axis:
        plot_center_axis()

    leafs = octree.get_leafs()

    depth = octree.root.depth()
    root_size = octree.root.size

    for i in range(depth + 1):

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

    mayavi.mlab.view(azimuth=azimuth,
                     elevation=elevation,
                     distance=distance,
                     focalpoint=focalpoint)

    mayavi.mlab.show()
    mayavi.mlab.clf(fg)


def show_each_stage_of_octree(octree,
                              scale_factor=1,
                              color=None,
                              size=(800, 700),
                              with_center_axis=False,
                              azimuth=None,
                              elevation=None,
                              distance=None,
                              focalpoint=None):

    if color is None:
        color = (random.uniform(0, 1),
                 random.uniform(0, 1),
                 random.uniform(0, 1))

    depth = octree.root.depth()
    root_size = octree.root.size

    for i in range(depth + 1):
        voxels_size = root_size / (2 ** i)

        voxels_position = octree.get_voxels_position(voxels_size)

        fg = mayavi.mlab.figure(figure=str(voxels_size), size=size)

        if with_center_axis:
            plot_center_axis()

        if voxels_position:
            voxels_position = numpy.array(voxels_position)
            mayavi.mlab.points3d(voxels_position[:, 0],
                                 voxels_position[:, 1],
                                 voxels_position[:, 2],
                                 mode='cube',
                                 color=color,
                                 scale_factor=voxels_size * scale_factor)

        mayavi.mlab.view(azimuth=azimuth,
                         elevation=elevation,
                         distance=distance,
                         focalpoint=focalpoint)

        mayavi.mlab.show()
        mayavi.mlab.clf(fg)
