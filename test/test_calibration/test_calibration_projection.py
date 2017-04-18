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

from alinea.phenomenal.data_access.plant_1 import (
    plant_1_calibration_camera_side)

from alinea.phenomenal.calibration.calibration import CalibrationCamera
# ==============================================================================


def test_projection_1():

    calibration = plant_1_calibration_camera_side()

    angle = 0
    pt_3d = (-472, -472, 200)
    projection = calibration.get_projection(angle)
    pt_2d = projection(pt_3d)
    assert pt_2d == (1337.425449561377, 1070.8621710384346)

    angle = 0
    projection = calibration.get_projection(angle)
    pt_3d = (0.0, 0.0, 0.0)
    pt_2d = projection(pt_3d)
    assert pt_2d == (1021.5504552422917, 1261.7274393727464)

    pt_3d = (100.0, 100.0, 0.0)
    pt_2d = projection(pt_3d)
    assert pt_2d == (963.19212737191492, 1261.5234983629146)

    angle = 90
    projection = calibration.get_projection(angle)
    pt_2d = projection(pt_3d)
    assert pt_2d == (1125.9214666496891, 1262.0921778812051)


def test_array_pixel_coordinates():

    calibration = plant_1_calibration_camera_side()

    pt3d = (-322.20389648, 162.67521638, -4866.89129462)
    pt_2d = calibration.pixel_coordinates(pt3d,
                                          calibration._cam_width_image,
                                          calibration._cam_height_image,
                                          calibration._cam_focal_length_x,
                                          calibration._cam_focal_length_y)

    assert pt_2d == (1337.425449561858, 1070.86217103428)

    pts_3d = numpy.array([[-322.20389648, 162.67521638, -4866.89129462],
                          [-322.20389648, 162.67521638, -4866.89129462],
                          [-322.20389648, 162.67521638, -4866.89129462],
                          [-322.20389648, 162.67521638, -4866.89129462]])

    pts_2d = calibration.arr_pixel_coordinates(pts_3d,
                                              calibration._cam_width_image,
                                              calibration._cam_height_image,
                                              calibration._cam_focal_length_x,
                                              calibration._cam_focal_length_y)

    for pt_2d in pts_2d:
        assert tuple(pt_2d) == (1337.425449561858, 1070.86217103428)

    pts_3d = numpy.array([[-322.20389648, 162.67521638, -4866.89129462]])

    pts_2d = calibration.arr_pixel_coordinates(pts_3d,
                                              calibration._cam_width_image,
                                              calibration._cam_height_image,
                                              calibration._cam_focal_length_x,
                                              calibration._cam_focal_length_y)

    for pt_2d in pts_2d:
        assert tuple(pt_2d) == (1337.425449561858, 1070.86217103428)


def test_array_camera_frame_local_point():

    calibration = plant_1_calibration_camera_side()
    camera_frame = calibration.get_camera_frame()

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

def test_array_get_projection():
    calibration = plant_1_calibration_camera_side()

    angle = 0
    pt_3d = (-472, -472, 200)
    projection = calibration.get_projection(angle)
    pt_2d = projection(pt_3d)
    assert pt_2d == (1337.425449561377, 1070.8621710384346)

    projection = calibration.get_arr_projection(angle)

    pts_3d = numpy.array([[-472, -472, 200],
                          [-472, -472, 200],
                          [-472, -472, 200],
                          [-472, -472, 200]])

    result = projection(pts_3d)

    for pt_2d in result:
        assert tuple(pt_2d) == (1337.425449561377, 1070.8621710384346)

# ==============================================================================

if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()
