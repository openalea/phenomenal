# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
from __future__ import division, print_function

import math
import numpy

import openalea.phenomenal.calibration as phm_calib
import openalea.phenomenal.data as phm_data
# ==============================================================================


def rotation_point(x, y, z, degree):
    alpha = math.radians(degree)
    origin = [x * math.cos(alpha) - y * math.sin(alpha),
              x * math.sin(alpha) + y * math.cos(alpha),
              z]

    return origin


def compute_frame(origin, x_rotation, y_rotation, z_rotation):

    mat_rot_x = phm_calib.rotation_matrix(math.radians(x_rotation),
                                          phm_calib.x_axis)
    mat_rot_y = phm_calib.rotation_matrix(math.radians(y_rotation),
                                          phm_calib.y_axis)
    mat_rot_z = phm_calib.rotation_matrix(math.radians(z_rotation),
                                          phm_calib.z_axis)

    rot = phm_calib.concatenate_matrices(mat_rot_y, mat_rot_z, mat_rot_x)

    return phm_calib.Frame(rot[:3, :3].T, origin)


def test_chess_frame():

    origin = (0.0, 0.0, 0.0)
    origin_0 = rotation_point(100, 0, 50, 0)
    origin_90 = rotation_point(100, 0, 50, 90)
    print(origin_0)
    print(origin_90)
    print('\n ========================== \n')

    pt_110_0 = rotation_point(110, 0, 50, 0)
    pt_110_90 = rotation_point(110, 0, 50, 90)
    print(pt_110_0)
    print(pt_110_90)
    print('\n ========================== \n')

    f_0 = compute_frame(origin, 0.0, 0.0, 0.0)
    f_1 = compute_frame(origin, 270, 180.0, 90)

    print('TEST')
    print(f_0.local_point((100, 0, 0)))
    print(f_1.local_point((100, 0, 0)))
    print(f_0.local_point((0, 100, 0)))
    print(f_1.local_point((0, 100, 0)))
    print(f_0.local_point((0, 0, 100)))
    print(f_1.local_point((0, 0, 100)))

    f_90 = compute_frame(origin_90, 0, 0, 90)
    f_900 = compute_frame(origin_90, 0, 0, -90)

    camera_0 = compute_frame((500, 0, 0), -numpy.pi / 2., 0, 0)
    camera_90 = compute_frame((0, 500, 0), -numpy.pi / 2., 0, 90)


    print('Point Local :')
    print(f_0.local_point(pt_110_0))
    print(f_90.local_point(pt_110_90))
    print(f_900.local_point(pt_110_90))

    print(camera_0.local_point(pt_110_0))
    print(camera_90.local_point(pt_110_90))

    print('\n ========================== \n')

    print(f_0.global_point((10, 0, 0)))
    print(f_90.global_point((10, 0, 0)))
    print(f_900.global_point((10, 0, 0)))


def test_frame():
    plant_number = 1
    c = phm_data.calibrations(plant_number=plant_number)["side"]

    print(c._cam_pos_x, c._cam_pos_y, c._cam_pos_z)
    print(c._cam_rot_x, c._cam_rot_y, c._cam_rot_z)

    fr_cam = c.camera_frame(c._cam_pos_x,
                            c._cam_pos_y,
                            c._cam_pos_z,
                            c._cam_rot_x,
                            c._cam_rot_y,
                            c._cam_rot_z,
                            c._cam_origin_axis)

    # print fr_cam.global_point((0, 0, 0))
    # print fr_cam.global_point((-50, 0, -2500))
    print(fr_cam.global_point((-100, 0, -5000)))
    print(fr_cam.local_point((0, 0, 0)))
    print(c._cam_focal_length_x, c._cam_focal_length_y)
    print(c._cam_width_image / 2.0, c._cam_height_image / 2.0)

    pt2d = c.pixel_coordinates(fr_cam.local_point((0, 0, 0)),
                               c._cam_width_image,
                               c._cam_height_image,
                               c._cam_focal_length_x,
                               c._cam_focal_length_y)

    print(pt2d)
    # print fr_cam.local_point((5000, 100, 0))


if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
