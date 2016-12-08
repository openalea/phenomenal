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
import mayavi.mlab

from alinea.phenomenal.display.multi_view_reconstruction import (
    show_list_points_3d)

# ==============================================================================

def show_voxel_point_cloud_segments(voxel_point_cloud_segments):

    voxels_size = None
    nb_cornet_leaf, nb_mature_leaf = (0, 0)

    voxels_stem, voxels_mature_leaf, voxels_cornet_leaf, voxels_unknown = (
        set(), set(), set(), set())

    voxels_path = set()

    for vs in voxel_point_cloud_segments.voxel_point_cloud_segment:

        voxels_size = vs.voxels_size
        if len(vs.paths) > 0:
            voxels_path = voxels_path.union(*vs.paths)

        if vs.label == "stem":
            voxels_stem = vs.voxels_center
        if vs.label == "mature_leaf":
            voxels_mature_leaf = voxels_mature_leaf.union(vs.voxels_center)
            nb_mature_leaf += 1
        if vs.label == "cornet_leaf":
            voxels_cornet_leaf = voxels_cornet_leaf.union(vs.voxels_center)
            nb_cornet_leaf += 1
        if vs.label == "unknown":
            voxels_unknown = voxels_mature_leaf.union(vs.voxels_center)

    print("Number of mature leaf : ", nb_mature_leaf)
    print("Number of cornet leaf: ", nb_cornet_leaf)
    print("Size of unknown voxels: ", len(voxels_unknown))
    print("Number of total leaf", (nb_mature_leaf + nb_cornet_leaf))

    list_voxels = [voxels_stem,
                   voxels_mature_leaf,
                   voxels_cornet_leaf,
                   voxels_unknown,
                   voxels_path]

    list_color = [(0.0, 0.0, 0.0),
                  (0.1, 0.1, 0.9),
                  (0.9, 0.1, 0.1),
                  (0.1, 0.9, 0.9),
                  (1.0, 1.0, 1.0)]

    show_list_points_3d(list_voxels,
                        list_color=list_color,
                        scale_factor=voxels_size * 0.5)


def plot_plane(plane, point):

    def get_point_of_planes(normal, node, radius=5):
        a, b, c = normal
        x, y, z = node

        d = a * x + b * y + c * z

        xx = numpy.linspace(x - radius, x + radius, radius * 2)
        yy = numpy.linspace(y - radius, y + radius, radius * 2)

        xv, yv = numpy.meshgrid(xx, yy)

        zz = - (a * xv + b * yv - d) / c

        return xv, yv, zz

    x, y, z = point
    a, b, c, d = plane

    a = float(round(a, 4) * 1000)
    b = float(round(b, 4) * 1000)
    c = float(round(c, 4) * 1000)

    d = float(max(a, b, c, 1))

    mayavi.mlab.quiver3d(float(x), float(y), float(z),
                         a / d, b / d, c /d,
                         line_width=1.0,
                         scale_factor=0.1)

    xx, yy, zz = get_point_of_planes((a, b, c), (x, y, z), radius=40)
    mayavi.mlab.mesh(xx, yy, zz)


def show_segment_voxel(segments, voxel_size):

    voxels_stem = [d["voxel"] for d in segments if d["label"] == "stem"]

    voxels_mature_leafs = [d["voxel"] for d in segments
                           if d["label"].startswith("mature_leaf")]

    voxels_connected_leafs = [d["voxel"] for d in segments
                              if d["label"].startswith("connected_leaf")]

    voxels_cornet_leafs = [d["voxel"] for d in segments
                           if d["label"].startswith("cornet_leaf")]

    print("Number of leaf detected : ", len(voxels_mature_leafs))
    print("Number of leaf connected : ", len(voxels_connected_leafs))
    print("Number of leaf cornet : ", len(voxels_cornet_leafs))
    print("Number of all lea", (len(voxels_mature_leafs) +
                                len(voxels_connected_leafs) +
                                len(voxels_cornet_leafs)))

    mature_leafs = set().union(*voxels_mature_leafs)
    connected_leafs = set().union(*voxels_connected_leafs)
    stem = set().union(*voxels_stem)
    cornet = set().union(*voxels_cornet_leafs)

    list_voxels = [stem,
                   cornet,
                   mature_leafs,
                   connected_leafs]

    list_color = [(0.0, 0.0, 0.0),
                  (0.9, 0.1, 0.1),
                  (0.1, 0.9, 0.9),
                  (0.1, 0.1, 0.9)]

    show_list_points_3d(list_voxels,
                        list_color=list_color,
                        scale_factor=voxel_size)

    show_list_points_3d(voxels_mature_leafs,
                        scale_factor=voxel_size)


def show_labeled_voxel(labeled_voxels, voxel_size):

    voxels_mature_leaf = [v for k, v in labeled_voxels.items()
                          if k.startswith('mature_leaf_')]

    voxels_connected_leaf = [v for k, v in labeled_voxels.items()
                             if k.startswith('connected_leaf_')]

    voxels_cornet_leaf = [v for k, v in labeled_voxels.items()
                          if k.startswith('cornet_leaf_')]

    # print("Number of leaf detected : ", len(voxels_mature_leaf))
    # print("Number of leaf connected : ", len(voxels_connected_leaf))
    # print("Number of leaf cornet : ", len(voxels_cornet_leaf))
    # print("Number of all lea", (len(voxels_mature_leaf) +
    #                             len(voxels_connected_leaf) +
    #                             len(voxels_cornet_leaf)))

    mature_leafs = set().union(*voxels_mature_leaf)
    connected_leafs = set().union(*voxels_connected_leaf)
    stem = labeled_voxels["stem"]
    cornet = set().union(*voxels_cornet_leaf)

    list_voxels = [stem,
                   cornet,
                   mature_leafs,
                   connected_leafs]

    list_color = [(0.0, 0.0, 0.0),
                  (0.9, 0.1, 0.1),
                  (0.1, 0.9, 0.9),
                  (0.1, 0.1, 0.9)]

    show_list_points_3d(list_voxels,
                        list_color=list_color,
                        scale_factor=voxel_size)