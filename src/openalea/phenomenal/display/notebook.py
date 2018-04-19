# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
from __future__ import division, print_function

import numpy
import ipyvolume

from ._order_color_map import order_color_map
# ==============================================================================


def plot_voxel(voxels_position, marker="box", color="green", size=2.0):
    if len(voxels_position) > 0:
        x, y, z = (voxels_position[:, 0],
                   voxels_position[:, 1],
                   voxels_position[:, 2])

        ipyvolume.scatter(x, y, z, size=size, marker=marker, color=color)


def show_voxel_grid(voxel_grid,
                    color='green',
                    size=2,
                    width=500,
                    height=500):

    ipyvolume.figure(width=width, height=height, controls=True, lighting=True)
    plot_voxel(voxel_grid.voxels_position, size=size, color=color)

    ipyvolume.xlim(numpy.min(voxel_grid.voxels_position[:, 0]),
                   numpy.max(voxel_grid.voxels_position[:, 0]))
    ipyvolume.ylim(numpy.min(voxel_grid.voxels_position[:, 1]),
                   numpy.max(voxel_grid.voxels_position[:, 1]))
    ipyvolume.zlim(numpy.min(voxel_grid.voxels_position[:, 2]),
                   numpy.max(voxel_grid.voxels_position[:, 2]))
    ipyvolume.view(0, 90)
    ipyvolume.show()


def show_mesh(vertices, faces, color='green', width=500, height=500):

    ipyvolume.figure(width=width, height=height)
    ipyvolume.view(0, 90)
    ipyvolume.plot_trisurf(
        vertices[:, 0], vertices[:, 1], vertices[:, 2],
        triangles=faces, color=color)
    ipyvolume.xlim(numpy.min(vertices[:, 0]), numpy.max(vertices[:, 0]))
    ipyvolume.ylim(numpy.min(vertices[:, 1]), numpy.max(vertices[:, 1]))
    ipyvolume.zlim(numpy.min(vertices[:, 2]), numpy.max(vertices[:, 2]))
    ipyvolume.show()


def show_skeleton(voxel_skeleton,
                  size=2,
                  with_voxel=True,
                  voxels_color='green',
                  polyline_color='red',
                  width=500, height=500):

    ipyvolume.figure(width=width, height=height)
    ipyvolume.view(0, 90)

    if with_voxel:
        voxels_position = voxel_skeleton.voxels_position()
        plot_voxel(voxels_position, size=size / 2, color=voxels_color)

    voxels_position = voxel_skeleton.voxels_position_polyline()
    plot_voxel(voxels_position, size=size, color=polyline_color)

    for vs in voxel_skeleton.voxel_segments:
        for color, index in [("blue", 0), ("red", -1)]:
            plot_voxel(numpy.array([vs.polyline[index]]),
                       size=size * 2,
                       marker="sphere",
                       color=color)

    ipyvolume.xlim(numpy.min(voxels_position[:, 0]),
                   numpy.max(voxels_position[:, 0]))
    ipyvolume.ylim(numpy.min(voxels_position[:, 1]),
                   numpy.max(voxels_position[:, 1]))
    ipyvolume.zlim(numpy.min(voxels_position[:, 2]),
                   numpy.max(voxels_position[:, 2]))

    ipyvolume.show()


def show_segmentation(voxel_segmentation,
                      size=2.0,
                      width=500, height=500):

    ipyvolume.figure(width=width, height=height)
    ipyvolume.view(0, 90)

    def get_color(label, info):

        if label == "stem":
            color = (128, 128, 128)
        elif label == "unknown":
            color = (255, 255, 255)
        elif 'pm_leaf_number' in info:
            color_map = order_color_map()
            color = color_map[info['pm_leaf_number']]
            color = tuple([int(255 * x) for x in color])
        else:
            if label == "growing_leaf":
                color = (255, 0, 0)
            else:
                color = (0, 255, 0)

        return "rgb" + str(color)

    for vo in voxel_segmentation.voxel_organs:

        voxels_position = numpy.array(
            map(tuple, list(vo.voxels_position())))

        plot_voxel(voxels_position,
                   size=size * 1,
                   color=get_color(vo.label, vo.info))

        if ((vo.label == "mature_leaf" or vo.label == "growing_leaf") and
                len(vo.voxel_segments) > 0 and "pm_position_tip" in vo.info):

            plot_voxel(numpy.array([vo.info['pm_position_tip']]),
                       size=size * 2,
                       color="red",
                       marker="sphere")

            plot_voxel(numpy.array([vo.info['pm_position_base']]),
                       size=size * 2,
                       color="blue",
                       marker="sphere")

    voxels_position = numpy.array(list(
        voxel_segmentation.get_voxels_position()))

    ipyvolume.xlim(numpy.min(voxels_position[:, 0]),
                   numpy.max(voxels_position[:, 0]))
    ipyvolume.ylim(numpy.min(voxels_position[:, 1]),
                   numpy.max(voxels_position[:, 1]))
    ipyvolume.zlim(numpy.min(voxels_position[:, 2]),
                   numpy.max(voxels_position[:, 2]))
    ipyvolume.show()
