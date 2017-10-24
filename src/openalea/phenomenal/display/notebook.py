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
from ._order_color_map import order_color_map

import numpy
import ipyvolume


def plot_voxel(voxels_position, size_ratio=1.0, marker="box", color="green"):

    if len(voxels_position) > 0:
        x, y, z = (voxels_position[:, 0],
                   voxels_position[:, 1],
                   voxels_position[:, 2])

        ipyvolume.scatter(x, y, z, size=size_ratio, marker=marker, color=color)


def show_voxel_grid(vg,
                    size_ratio=1,
                    color='green',
                    width=800, height=800):

    ipyvolume.figure(width=width, height=height)
    plot_voxel(vg.voxels_position, size_ratio=size_ratio, color=color)
    ipyvolume.style.use(['default', 'minimal'])
    ipyvolume.view(0, 90)
    ipyvolume.show()


def show_mesh(vertices, faces, color='green'):

    ipyvolume.figure(width=800, height=800)
    ipyvolume.style.use(['default', 'minimal'])
    ipyvolume.view(0, 90)

    x, y, z = (vertices[:, 0], vertices[:, 1], vertices[:, 2])
    ipyvolume.plot_trisurf(x, y, z, triangles=faces, color=color)
    ipyvolume.show()


def show_skeleton(voxel_skeleton,
                  with_voxel=True,
                  size_ratio=1.0,
                  color='green',
                  width=800, height=800):

    ipyvolume.figure(width=width, height=height)
    ipyvolume.style.use(['default', 'minimal'])
    ipyvolume.view(0, 90)

    for vs in voxel_skeleton.voxel_segments:

        if with_voxel:

            plot_voxel(numpy.array(list(vs.voxels_position)),
                       size_ratio=size_ratio * 0.25,
                       color=color)

        plot_voxel(numpy.array(list(vs.polyline)),
                   size_ratio=size_ratio,
                   color="red")

        plot_voxel(numpy.array([vs.polyline[0]]),
                   size_ratio=size_ratio * 2.0,
                   marker="sphere",
                   color="blue")

        plot_voxel(numpy.array([vs.polyline[-1]]),
                   size_ratio=size_ratio * 2.0,
                   marker="sphere",
                   color="red")

    ipyvolume.show()


def show_segmentation(voxel_segmentation,
                      size_ratio=1.0,
                      width=800, height=800):

    ipyvolume.figure(width=width, height=height)
    ipyvolume.style.use(['default', 'minimal'])
    ipyvolume.view(0, 90)

    def get_color(label, info):

        if label == "stem":
            color = (128, 128, 128)
        elif label == "unknown":
            color = (255, 255, 255)
        elif 'order' in info:
            color_map = order_color_map()
            color = color_map[info['order']]
            color = tuple([int(255 * x) for x in color])

        else:
            if label == "cornet_leaf":
                color = (255, 0, 0)
            else:
                color = (0, 255, 0)

        return "rgb" + str(color)

    for vo in voxel_segmentation.voxel_organs:

        voxels_position = numpy.array(
            map(tuple, list(vo.voxels_position())))

        plot_voxel(voxels_position,
                   size_ratio * 1,
                   color=get_color(vo.label, vo.info))

        if ((vo.label == "mature_leaf" or vo.label == "cornet_leaf") and
                len(vo.voxel_segments) > 0 and "position_tip" in vo.info):

            plot_voxel(numpy.array([vo.info['position_tip']]),
                       size_ratio * 2,
                       color="red",
                       marker="sphere")

            plot_voxel(numpy.array([vo.info['position_base']]),
                       size_ratio * 2,
                       color="blue",
                       marker="sphere")

    ipyvolume.show()