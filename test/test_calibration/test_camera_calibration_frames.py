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

""" Test consistency of transformations between frames for the calibration Camera


For these tests, we define a world frame defined by a right handed xyz frame composed of a vertical axis (z+ upward),
x=0 plane and z=0 intercepting a camera pointing to world origin and located twice its focal length far from z-axis
(y+ from camera toward the z-axis).

The camera and image frame are as depicted in
https://docs.opencv.org/2.4/modules/calib3d/doc/camera_calibration_and_3d_reconstruction.html

that is :
    - for camera frame: camera origin is image center, z-axis points toward the scene, x is left-> right along image width, y is
up->down along image height
    - for image frame: origin is top-left, u is left->right along image width, v is up->down along image height

"""

from __future__ import division, print_function
import numpy

from openalea.phenomenal.calibration import CalibrationCamera, origin_axis, CalibrationFrame


def test_image_frame():
    """"test pixel position from point expressed in camera frame coordinates"""
    w, h, fx, fy = 10, 10, 1, 1
    # world origin, situated 2 * f in font of camera (altitude 2f in camera frame)
    w_origin = numpy.array([0, 0, 2 * fx])
    # points located 2 * f unit far from w_origin, along camera x+ and x-
    right = w_origin + [2 * fx, 0, 0]
    left = w_origin + [-2 * fx, 0, 0]
    # points located 2 * f unit far from w_origin, along camera y+ and y-
    down = w_origin + [0, 2 * fx, 0]
    up = w_origin + [0, -2 * fx, 0]

    # expected pixel positions
    i_origin = numpy.array([w / 2, h / 2])
    i_right = i_origin + [1, 0]
    i_left = i_origin - [1, 0]
    i_up = i_origin - [0, 1]
    i_down = i_origin + [0, 1]

    # test one point call
    uo, vo = CalibrationCamera.pixel_coordinates(w_origin, w, h, fx, fy)
    assert (uo, vo) == (w/2, h/2)

    # test array call
    pts = numpy.array((w_origin, right, left, up, down))
    pix = numpy.array((i_origin, i_right, i_left, i_up, i_down))
    pixels = CalibrationCamera.pixel_coordinates(pts, w, h, fx, fy)
    numpy.testing.assert_allclose(pixels, pix)


def test_side_camera_frame():
    """side camera is along world y-axis (on y-), pointing to world origin, x camera and x world being identical"""

    # camera frame axis coordinates expressed in world coordinates
    side_camera_axes = numpy.array([[1., 0., 0.],
                                    [0., 0., -1.],
                                    [0., 1., 0.]])

    # test camera axis frame
    c = CalibrationCamera()
    fx = 1
    c._width_image, c._height_image, c._focal_length_x, c._focal_length_y = 10, 10, fx, fx
    c._pos_x, c._pos_y, c._pos_z = 0, -2 * fx, 0  # side camera defines z=0 and x=0 planes
    c._rot_x, c._rot_y, c._rot_z = -numpy.pi / 2, 0, 0  # make z camera axis points toward world origin
    c._cam_origin_axis = numpy.identity(4)  # no transform
    c._angle_factor = 1  # perfect rotation of world

    f = c.get_frame()
    numpy.testing.assert_allclose(f._axes, side_camera_axes, atol=1e-6)

    # Test projections of corner points in world coordinate system
    # world origin,
    w_origin = [0, 0, 0]
    # points located 2 * f unit far from w_origin, along world x+ and x-
    right = [2 * fx, 0, 0]
    left = [-2 * fx, 0, 0]
    # points located 2 * f unit far from w_origin, along world z+ and z-
    up = [0, 0, 2 * fx]
    down = [0, 0, -2 * fx]
    # Expectations in image frame
    i_origin = numpy.array([c._width_image / 2, c._height_image / 2])
    i_right = i_origin + [1, 0]
    i_left = i_origin - [1, 0]
    i_up = i_origin - [0, 1]
    i_down = i_origin + [0, 1]

    p = c.get_projection(0)
    pts = numpy.array((w_origin, right, left, up, down))
    pix = numpy.array((i_origin, i_right, i_left, i_up, i_down))
    pixels = p(pts)
    numpy.testing.assert_allclose(pixels, pix)

    # test positioning using origin_axis
    c._rot_x, c._rot_y, c._rot_z = 0, 0, 0
    c._cam_origin_axis = origin_axis(side_camera_axes).round()

    p = c.get_projection(0)
    pixels = p(pts)
    numpy.testing.assert_allclose(pixels, pix)
    #test one point call
    pixel = p(pts[0])
    numpy.testing.assert_allclose(pixel, pix[0])


def test_top_camera_frame():
    """top camera is along world z-axis (z+), pointing to world origin,
       side camera (y-) being on the bottom of the image"""

    # camera frame axis coordinates expressed in world coordinates
    top_camera_axes = numpy.array([ [1., 0., 0.],
                                    [0., -1., 0.],
                                    [0., 0., -1.]])

    # test camera axis frame
    c = CalibrationCamera()
    fx = 1
    c._width_image, c._height_image, c._focal_length_x, c._focal_length_y = 10, 10, fx, fx
    c._pos_x, c._pos_y, c._pos_z = 0, 0, 2 * fx  # top camera is on z+
    c._rot_x, c._rot_y, c._rot_z = -numpy.pi, 0, 0  # make z camera axis points toward world origin
    c._cam_origin_axis = numpy.identity(4)  # no transform
    c._angle_factor = 1  # no rotation of world

    f = c.get_frame()
    numpy.testing.assert_allclose(f._axes, top_camera_axes, atol=1e-6)

    # Test projections of corner points in world coordinate system
    # world origin,
    w_origin = [0, 0, 0]
    # points located 2 * f unit far from w_origin, along world x+ and x-
    right = [2 * fx, 0, 0]
    left = [-2 * fx, 0, 0]
    # points located 2 * f unit far from w_origin, along world y+ and y-
    back = [0, 2 * fx, 0]
    front = [0, -2 * fx, 0]
    # Expectations in image frame
    i_origin = numpy.array([c._width_image / 2, c._height_image / 2])
    i_right = i_origin + [1, 0]
    i_left = i_origin - [1, 0]
    i_back = i_origin - [0, 1]
    i_front = i_origin + [0, 1]

    p = c.get_projection(0)
    pts = numpy.array((w_origin, right, left, back, front))
    pix = numpy.array((i_origin, i_right, i_left, i_back, i_front))
    pixels = p(pts)
    numpy.testing.assert_allclose(pixels, pix)

    # test positioning using origin_axis
    c._rot_x, c._rot_y, c._rot_z = 0, 0, 0
    c._cam_origin_axis = origin_axis(top_camera_axes).round()

    p = c.get_projection(0)
    pixels = p(pts)
    numpy.testing.assert_allclose(pixels, pix)


def test_target_frame():
    # target axis coordinates expressed in world coordinates
    target_axis = numpy.identity(3)

    # test target axis frame
    c = CalibrationFrame()
    c._pos_x, c._pos_y, c._pos_z = 0, 0, 0
    c._rot_x, c._rot_y, c._rot_z = 0, 0, 0

    f = c.get_frame()
    numpy.testing.assert_allclose(f._axes, target_axis, atol=1e-6)
    f = c.get_frame()
    expected = numpy.array(((0, 1, 0), (-1, 0, 0), (0, 0, 1)))
    numpy.testing.assert_allclose(f._axes, expected, atol=1e-6)

    # test positioning using rotations
    c = CalibrationFrame()
    c._pos_x, c._pos_y, c._pos_z = 0, 0, 0
    c._rot_x, c._rot_y, c._rot_z = numpy.pi / 2, 0, 0

    expected = numpy.array(((1, 0, 0), (0, 0, 1), (0, -1, 0)))
    f = c.get_frame()
    numpy.testing.assert_allclose(f._axes, expected, atol=1e-6)

    f = c.get_frame()
    expected = numpy.array(((0, 1, 0), (0, 0, 1), (1, 0, 0)))
    numpy.testing.assert_allclose(f._axes, expected, atol=1e-6)

    # test positioning using origin_axis
    expected = numpy.array(((1, 0, 0), (0, 0, 1), (0, -1, 0)))
    c = CalibrationFrame()
    c._pos_x, c._pos_y, c._pos_z = 0, 0, 0
    c._rot_x, c._rot_y, c._rot_z = 0, 0, 0
    f = c.get_frame()
    numpy.testing.assert_allclose(f._axes, expected, atol=1e-6)

    f = c.get_frame()
    expected = numpy.array(((0, 1, 0), (0, 0, 1), (1, 0, 0)))
    numpy.testing.assert_allclose(f._axes, expected, atol=1e-6)