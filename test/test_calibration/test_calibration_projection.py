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

import numpy

import openalea.phenomenal.data as phm_data
# ==============================================================================


def test_array_pixel_coordinates():
    plant_number = 1
    side_calibration = phm_data.calibrations(plant_number=plant_number)["side"]

    pt3d = (-322.20389648, 162.67521638, -4866.89129462)
    pt_2d = side_calibration.pixel_coordinates(
        pt3d,
        side_calibration._cam_width_image,
        side_calibration._cam_height_image,
        side_calibration._cam_focal_length_x,
        side_calibration._cam_focal_length_y)

    assert pt_2d == (1337.425449561858, 1070.86217103428)

    pts_3d = numpy.array([[-322.20389648, 162.67521638, -4866.89129462],
                          [-322.20389648, 162.67521638, -4866.89129462],
                          [-322.20389648, 162.67521638, -4866.89129462],
                          [-322.20389648, 162.67521638, -4866.89129462]])

    pts_2d = side_calibration.arr_pixel_coordinates(
        pts_3d,
        side_calibration._cam_width_image,
        side_calibration._cam_height_image,
        side_calibration._cam_focal_length_x,
        side_calibration._cam_focal_length_y)

    for pt_2d in pts_2d:
        assert tuple(pt_2d) == (1337.425449561858, 1070.86217103428)

    pts_3d = numpy.array([[-322.20389648, 162.67521638, -4866.89129462]])

    pts_2d = side_calibration.arr_pixel_coordinates(
        pts_3d,
        side_calibration._cam_width_image,
        side_calibration._cam_height_image,
        side_calibration._cam_focal_length_x,
        side_calibration._cam_focal_length_y)

    for pt_2d in pts_2d:
        assert tuple(pt_2d) == (1337.425449561858, 1070.86217103428)


def test_array_camera_frame_local_point():
    plant_number = 1
    side_calibration = phm_data.calibrations(plant_number=plant_number)["side"]
    camera_frame = side_calibration.get_camera_frame()

    pt_3d = (-322.20389648, 162.67521638, -4866.89129462)
    result = camera_frame.local_point(pt_3d)
    result = numpy.round(result.astype(float), 5)

    assert tuple(result) == (95.38307, -4909.59993, -5763.88954)

    pts_3d = [[-322.20389648, 162.67521638, -4866.89129462],
              [-322.20389648, 162.67521638, -4866.89129462],
              [-322.20389648, 162.67521638, -4866.89129462],
              [-322.20389648, 162.67521638, -4866.89129462]]

    result = camera_frame.arr_local_point(pts_3d)
    result = numpy.round(result.astype(float), 5)

    for pt_3d in result:
        assert tuple(pt_3d) == (95.38307, -4909.59993, -5763.88954)

    pts_3d = [[-322.20389648, 162.67521638, -4866.89129462]]

    result = camera_frame.arr_local_point(pts_3d)
    result = numpy.round(result.astype(float), 5)

    for pt_3d in result:
        assert tuple(pt_3d) == (95.38307, -4909.59993, -5763.88954)


def test_projection():
    angle = 0
    plant_number = 1
    side_calibration = phm_data.calibrations(plant_number=plant_number)["side"]
    projection = side_calibration.get_projection(angle)

    pts_3d = numpy.array([[-472, -472, 200],
                          [-472, -472, 200],
                          [-472, -472, 200],
                          [-472, -472, 200]])

    result = projection(pts_3d)

    for pt_2d in result:
        assert tuple(pt_2d) == (1337.425449561377, 1070.8621710384346)


if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
