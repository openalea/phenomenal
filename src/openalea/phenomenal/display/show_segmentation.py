# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
from __future__ import division, print_function, absolute_import

import numpy

from ._order_color_map import order_color_map
from .scene import Scene
# ==============================================================================


def get_color(label,
              info):
    if label == "stem":
        return 0.5, 0.5, 0.5
    elif label == "unknown":
        return 1, 1, 1
    elif 'pm_leaf_number' in info:
        color_map = order_color_map()
        return color_map[info['pm_leaf_number']]
    else:
        if label == "growing_leaf":
            return 1, 0, 0
        else:
            return None


def get_actors_from_voxel_organ(voxel_organ,
                                voxels_size,
                                plot_number=True):

    actors, text_actors = list(), list()

    # voxels_position = numpy.array(
    #     map(tuple, list(voxel_organ.voxels_position())))

    actors.append(Scene.get_actor_from_voxels(
        voxel_organ.voxels_position(),
        voxels_size,
        color=get_color(voxel_organ.label, voxel_organ.info)))

    if ((voxel_organ.label == "mature_leaf" or
                 voxel_organ.label == "growing_leaf") and
                len(voxel_organ.voxel_segments) > 0 and "pm_position_tip" in
        voxel_organ.info):

        pos = voxel_organ.info['pm_position_base']

        actors.append(Scene.get_actor_from_ball_position(
            voxel_organ.info['pm_position_tip'],
            radius=voxels_size * 2,
            color=(1, 0, 0)))

        actors.append(Scene.get_actor_from_ball_position(
            pos, radius=voxels_size * 2, color=(0, 0, 1)))

        r, g, b = (0, 0, 1)
        pos = voxel_organ.info['pm_position_tip']
        pos = (pos[0] - 10, pos[1] - 10, pos[2])

        if plot_number and 'pm_leaf_number' in voxel_organ.info:
            order = str(voxel_organ.info['pm_leaf_number'])
            text_actors.append(Scene.get_actor_from_text(
                order,
                position=pos,
                scale=40,
                color=(r, g, b)))

    return actors, text_actors

# ==============================================================================


def get_actors_from_segmentation_classic_mode(vmsi):

    actors, text_actors = list(), list()
    for voxel_organ in vmsi.get_leafs():
        organ_actors, organ_text_actors = get_actors_from_voxel_organ(
            voxel_organ,
            vmsi.voxels_size)
        actors += organ_actors
        text_actors += organ_text_actors

    organ_actors, organ_text_actors = get_actors_from_voxel_organ(
        vmsi.get_stem(),
        vmsi.voxels_size)
    actors += organ_actors
    text_actors += organ_text_actors

    return actors, text_actors


def get_actors_from_segmentation_stem_mode(vmsi):

    actors, text_actors = list(), list()
    for vo in vmsi.voxel_organs:

            color = (0.1, 0.8, 0.1)
            if vo.label == "stem":
                color = (0, 0, 0)

            actors.append(Scene.get_actor_from_voxels(
                vo.voxels_position(),
                vmsi.voxels_size,
                color=color))

    return actors, text_actors


def get_actors_from_segmentation_skeleton_mode(vmsi,
                                               order=None):

    actors, text_actors = list(), list()
    for vo in vmsi.get_leafs():
        actors.append(Scene.get_actor_from_voxels(
            vo.voxels_position(), vmsi.voxels_size * 0.25, color=(0, 1, 0)))

        polyline = vo.get_longest_segment().polyline
        actors.append(Scene.get_actor_from_voxels(
            polyline, vmsi.voxels_size * 1, color=(1, 0, 0)))

        actors.append(Scene.get_actor_from_ball_position(
            polyline[0], radius=5, color=(0, 0, 1)))

        actors.append(Scene.get_actor_from_ball_position(
            polyline[-1], radius=5, color=(1, 0, 0)))

        if order is not None:
            for vo in vmsi.get_leafs():
                if 'order' in vo.info and vo.info['order'] == order:
                    vs = vo.get_highest_polyline()
                    actors.append(Scene.get_actor_from_voxels(
                        vs.polyline,
                        vmsi.voxels_size * 1.5,
                        color=(0, 0, 1)))

    return actors, text_actors


def get_actors_from_segmentation_split_mode(vmsi):

    actors, text_actors = list(), list()

    vo_stem = vmsi.get_stem()
    actors.append(Scene.get_actor_from_voxels(
        vo_stem.voxels_position(),
        vmsi.voxels_size,
        color=get_color(vo_stem.label, vo_stem.info)))

    for vo in vmsi.get_leafs():

        voxels_position = numpy.array(
            map(tuple, list(vo.voxels_position())))

        if "pm_position_tip" in vo.info:

            vm = numpy.array(vo.info['pm_vector_mean'])
            pos = vo.info['pm_position_base']

            # if vo.label == "growing_leaf":
            #     pos = pos_stem
            #     vm = vm * 2
            #
            #     closest_nodes = vo.get_longest_segment().closest_nodes
            #
            #     i = vo.get_longest_segment().polyline.index(
            #         vo.info['pm_position_base'])
            #
            #     v_base = set.union(*[set(nodes) for nodes in
            #                          closest_nodes[:i]])
            #
            #     v_leaf = set.union(*[set(nodes) for nodes in
            #                          closest_nodes[i:]])
            #
            #     v_base = v_base - v_leaf
            #     if len(v_base) > 0:
            #         voxels = numpy.array(map(tuple, list(v_base)))
            #
            #         actors.append(Scene.get_actor_from_voxels(
            #             voxels + vm,
            #             vmsi.voxels_size * 0.20,
            #             color=(0, 0, 0)))
            #
            #     voxels_position = numpy.array(map(tuple, list(v_leaf)))

            actors.append(Scene.get_actor_from_voxels(
                voxels_position + vm,
                vmsi.voxels_size,
                color=get_color(vo.label, vo.info)))

            actors.append(Scene.get_actor_from_ball_position(
                vo.info['pm_position_tip'] + vm,
                radius=vmsi.voxels_size * 2,
                color=(1, 0, 0)))

            actors.append(Scene.get_actor_from_ball_position(
                pos + vm,
                radius=vmsi.voxels_size * 2,
                color=(0, 0, 1)))

            xa, ya, za = pos
            xb, yb, zb = tuple(vm)
            xc, yc, zc = (xa + xb, ya + yb, za + zb)

            actors.append(Scene.get_actor_from_arrow_vector(
                (xa, ya, za),
                (xc, yc, zc),
                color=(0, 0, 0),
                line_width=40))

            r, g, b = (0, 0, 1)
            pos = vo.info['pm_position_tip'] + vm
            pos = (pos[0] - 10, pos[1] - 10, pos[2])

            if 'pm_leaf_number' in vo.info:
                order = str(vo.info['pm_leaf_number'])
                text_actors.append(Scene.get_actor_from_text(
                    order,
                    position=pos,
                    scale=40,
                    color=(r, g, b)))

    return actors, text_actors

# ==============================================================================


def show_segmentation(vmsi,
                      mode="classic",
                      windows_size=(600, 800),
                      screenshot_filename=None,
                      screenshot_magnification=10,
                      record_filename=None,
                      record_quality=2,
                      record_rate=25):

    actors, text_actors = list(), list()
    if mode == "classic":
        actors, text_actors = get_actors_from_segmentation_classic_mode(vmsi)
    if mode == "only_stem_colored":
        actors, text_actors = get_actors_from_segmentation_stem_mode(
            vmsi)
    if mode == "only_skeleton":
        actors, text_actors = get_actors_from_segmentation_skeleton_mode(
            vmsi)
    if mode == "separated_leaf":
        actors, text_actors = get_actors_from_segmentation_split_mode(
            vmsi)

    scene = Scene()
    scene.add_actors(actors)
    scene.add_text_actors(text_actors)
    scene.show(windows_size=windows_size,
               screenshot_filename=screenshot_filename,
               screenshot_magnification=screenshot_magnification,
               record_filename=record_filename,
               record_quality=record_quality,
               record_rate=record_rate)


def record_segmentation(vmsis, filename, record_elevation=20):

    scene = Scene()

    def func(vmsi):
        actors, text_actors = get_actors_from_segmentation_classic_mode(vmsi)
        scene.add_actors(actors)
        scene.add_text_actors(text_actors)

    scene.set_camera(elevation=record_elevation)
    scene.record_video(filename, vmsis, func)
