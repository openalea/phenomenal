# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================


import k3d
import numpy as np
from matplotlib.colors import rgb2hex
from ._order_color_map import order_color_map


# ==============================================================================


def plot_voxel(voxels, color=0x00ff00):
    # contiguous array and uint8 are required to avoid k3d implicit cast warning
    plt_voxels = k3d.voxels(np.ascontiguousarray(voxels, dtype=np.uint8), color_map=color)
    return plt_voxels


def plot_points(voxels_position, color=0x00ff00, size=2.0):
    plt_points = k3d.points(positions=voxels_position.astype(np.float32),
                            point_size=size, color=color)
    return plt_points


def show_point_cloud(xyz_positions,
                     color=0x00ff00,
                     size=2):

    plot = k3d.plot()
    plot += k3d.points(positions=xyz_positions.astype(np.float32),
                    point_size=size, color=color)
    plot.display()


def show_voxel_grid(voxel_grid,
                    color=0x00ff00):

    plot = k3d.plot()
    voxels = voxel_grid.to_image_3d()
    plot += plot_voxel(voxels, color)
    plot.display()


def show_mesh(mesh, color=0x00ff00):
    if mesh.colors.size:
        rgb = mesh.colors.astype(np.uint32)
        colors = (rgb[:, 0] << 16) | (rgb[:, 1] << 8) | rgb[:, 2]
        mesh = k3d.mesh(mesh.vertices.astype(np.float32), indices=mesh.faces.astype(np.uint32), colors=colors.tolist())
    else:
        mesh = k3d.mesh(mesh.vertices.astype(np.float32), indices=mesh.faces.astype(np.uint32), color=color)
    plot = k3d.plot()
    plot += mesh
    return plot


def show_skeleton(
    voxel_skeleton,
    size=2,
    with_voxel=True,
    voxels_color=0x00ff00,
    polyline_color=0xff0000,
):
    plot = k3d.plot()
    if with_voxel:
        voxels_position = voxel_skeleton.voxels_position()
        plot += plot_points(voxels_position, size=size / 2, color=voxels_color)

    voxels_position = voxel_skeleton.voxels_position_polyline()
    plot += plot_points(voxels_position, size=size, color=polyline_color)

    for vs in voxel_skeleton.segments:
        for color, index in [(0x0000ff, 0), (0xff0000, -1)]:
            plot += plot_points(
                np.array([vs.polyline[index]]),
                size=size * 2,
                color=color,
            )
    plot.display()


def show_segmentation(voxel_segmentation, size=2.0):
    plot = k3d.plot()
    def get_color(label, info):
        if label == "stem":
            color = (128, 128, 128)
        elif label == "unknown":
            color = (255, 255, 255)
        elif "pm_leaf_number" in info:
            color_map = order_color_map()
            color = color_map[info["pm_leaf_number"]]
            color = tuple([int(255 * x) for x in color])
        else:
            if label == "growing_leaf":
                color = (255, 0, 0)
            else:
                color = (0, 255, 0)

        return color

    for vo in voxel_segmentation.voxel_organs:
        voxels_position = np.array(list(map(tuple, list(vo.voxels_position()))))
        vo_color = int(rgb2hex(np.array(get_color(vo.label, vo.info)) / 255.0).replace("#", ""), 16)
        plot += plot_points(voxels_position, size=size * 1, color=vo_color)

        if (
            (vo.label == "mature_leaf" or vo.label == "growing_leaf")
            and len(vo.voxel_segments) > 0
            and "pm_position_tip" in vo.info
        ):
            plot += plot_points(
                np.array([vo.info["pm_position_tip"]]),
                size=size * 2,
                color=0xff0000,
            )

            plot += plot_points(
                np.array([vo.info["pm_position_base"]]),
                size=size * 2,
                color=0x0000ff,
            )
    plot.display()


def show_synthetic_plant(
    vertices, faces, meta_data=None, size=0.5, color=0x00ff00):
    plot = k3d.plot()
    plot += k3d.mesh(vertices.astype(np.float32), indices=faces.astype(np.uint32), color=color)

    if meta_data is not None:
        ranks = meta_data["leaf_order"]
        polylines = {
            n: list(map(np.array, list(zip(*meta_data["leaf_polylines"][i]))))
            for i, n in enumerate(ranks)
        }

        voxels = set()
        for leaf_order in polylines:
            x, y, z, r = polylines[leaf_order]
            polyline = np.array(list(zip(x, y, z))) * 10 - np.array([0, 0, 750])

            plot+= plot_points(polyline, size=size, color=0xff0000)
            voxels = voxels.union(set(map(tuple, list(polyline))))

    plot.display()