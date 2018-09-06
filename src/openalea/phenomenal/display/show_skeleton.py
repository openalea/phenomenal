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

from .scene import Scene
# ==============================================================================


def get_actors_from_skeleton(voxel_skeleton,
                             with_voxel=True,
                             voxel_color=(0, 1, 0),
                             skeleton_color=(1, 0, 0),
                             color_segment=None):

    orderer_voxel_segments = sorted(voxel_skeleton.segments,
                                    key=lambda vs: len(vs.voxels_position))

    actors = list()
    for i, vs in enumerate(orderer_voxel_segments):

        if color_segment is not None and color_segment == i:
            actors.append(Scene.get_actor_from_voxels(
                vs.voxels_position,
                voxel_skeleton.voxels_size * 0.50,
                color=(0, 0, 1)))

        elif with_voxel:
            actors.append(Scene.get_actor_from_voxels(
                vs.voxels_position,
                voxel_skeleton.voxels_size * 0.15,
                color=voxel_color))

        actors.append(Scene.get_actor_from_voxels(
            vs.polyline,
            voxel_skeleton.voxels_size * 1.5,
            color=skeleton_color))

        actors.append(Scene.get_actor_from_ball_position(
            vs.polyline[0],
            radius=voxel_skeleton.voxels_size * 4,
            color=(0, 0, 1)))

        actors.append(Scene.get_actor_from_ball_position(
            vs.polyline[-1],
            radius=voxel_skeleton.voxels_size * 4,
            color=(1, 0, 0)))

    return actors


def show_skeleton(voxel_skeleton,
                  with_voxel=True,
                  voxel_color=(0, 1, 0),
                  skeleton_color=(1, 0, 0),
                  color_segment=None,
                  windows_size=(600, 800),
                  screenshot_filename=None,
                  screenshot_magnification=10,
                  record_filename=None,
                  record_quality=2,
                  record_rate=25):

    scene = Scene()
    actors = get_actors_from_skeleton(voxel_skeleton,
                                      with_voxel=with_voxel,
                                      voxel_color=voxel_color,
                                      skeleton_color=skeleton_color,
                                      color_segment=color_segment)
    scene.add_actors(actors)
    scene.show(windows_size=windows_size,
               screenshot_filename=screenshot_filename,
               screenshot_magnification=screenshot_magnification,
               record_filename=record_filename,
               record_quality=record_quality,
               record_rate=record_rate)


# ==============================================================================


def record_skeleton(list_voxel_skeleton, filename,
                    with_voxel=True,
                    voxel_color=(0, 1, 0),
                    skeleton_color=(1, 0, 0),
                    record_elevation=20):
    scene = Scene()

    def func(voxel_skeleton):
        actors = get_actors_from_skeleton(voxel_skeleton,
                                          with_voxel=with_voxel,
                                          voxel_color=voxel_color,
                                          skeleton_color=skeleton_color)
        scene.add_actors(actors)

    scene.set_camera(elevation=record_elevation)
    scene.record_video(filename, list_voxel_skeleton, func)
