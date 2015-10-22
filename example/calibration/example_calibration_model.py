# -*- python -*-
#
#       example_calibration_model.py :
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       File author(s): Simon Artzet <simon.artzet@gmail.com>
#
#       File contributor(s):
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
#       ========================================================================

#       ========================================================================
#       External Import
import glob
import math
import numpy
import cv2


#       ========================================================================
#       Local Import
import alinea.phenomenal.chessboard
import alinea.phenomenal.misc
import alinea.phenomenal.result_viewer
import alinea.phenomenal.multi_view_reconstruction
import alinea.phenomenal.calibration_model
#       ========================================================================
#       Code


def example_calibration(data_directory, calib_name):

    files_sv = glob.glob(data_directory + '*sv*.png')
    angles = map(lambda x: int((x.split('_sv')[1]).split('.png')[0]), files_sv)

    images = dict()
    for i in range(len(files_sv)):
        images[angles[i]] = cv2.imread(files_sv[i], cv2.IMREAD_GRAYSCALE)

    chessboard = alinea.phenomenal.chessboard.Chessboard(47, 8, 6)

    print " find chessboard pts on each image"
    cv_pts = dict()
    for alpha, img in images.items():
        print alpha
        pts = chessboard.find_corners(img)
        if pts is not None:
            cv_pts[alpha] = pts[:, 0, :]

    guess = [
        -164.36793985970391,    # x position of chess in world frame
        -184.26982549215279,    # y position of chess in world frame
        1016.2924110974527,     # z position of chess in world frame

        -0.24676783786914835,   # elevation angle around local x axis
        0.033230717529020827,   # rotation angle around local z axis

        4325.1372442743241,
        # scaling factor between real coordinates and pixel coordinates
        4314.5457485003662,
        # scaling factor between real coordinates and pixel coordinates

        5053.3551632860035,     # distance of camera to rotation axis
        -2.4495310698780379,    # offset angle in radians for rotation
        666.05979874456671,     # z position of cam in world frame when alpha=0
        0.021140291507288664,   # azimuth angle of camera (around local y axis)
        0.00042593152159524892,
        # elevation angle of camera (around local x axis)
        -0.0036106966523099557,
        # tilt angle of camera (around local z axis)
        0.85901926301294507]    # rotation offset around z_axis in world frame

    # cc.plot_calibration(chessboard, cv_pts, guess, 48)
    cal = alinea.phenomenal.calibration_model.Calibration()
    cal.find_model_parameters(chessboard, cv_pts, guess)

    # cal.print_value()
    cal.write_calibration(calib_name)


def example_calibration_reprojection(data_directory, calib_name):

    files_sv = glob.glob(data_directory + '*sv*.png')
    angles = map(lambda x: int((x.split('_sv')[1]).split('.png')[0]), files_sv)

    images = dict()
    for i in range(len(files_sv)):
        images[angles[i]] = cv2.imread(files_sv[i], cv2.IMREAD_COLOR)

    calibration = alinea.phenomenal.calibration_model.Calibration.\
        read_calibration(calib_name)

    # img = alinea.phenomenal.multi_view_reconstruction.project_points_on_image(
    #     [(0.0, 0.0, 0.0)], 1.0, images[0], calibration, 0.0)

    chessboard = alinea.phenomenal.chessboard.Chessboard(47, 8, 6)
    print chessboard.object_points
    #
    # point = (0.0, 0.0, 0.0)
    #
    # x, y, z, elev, tilt = (-1.64416314e+02,
    #                        -1.84270911e+02,
    #                        1.01638704e+03,
    #                        -2.46772091e-01,
    #                        3.32209616e-02)

    point = (-164.41631426, -184.27091086, 1016.38703925)

    radius = 1
    angle = 45
    img = images[angle]
    height_image, length_image, _ = numpy.shape(img)

    x_min, x_max, y_min, y_max = alinea.phenomenal.multi_view_reconstruction.\
        bbox_projection(point, radius, calibration, angle)

    print x_min, x_max, y_min, y_max

    x_min = min(max(math.floor(x_min), 0), length_image - 1)
    x_max = min(max(math.ceil(x_max), 0), length_image - 1)
    y_min = min(max(math.floor(y_min), 0), height_image - 1)
    y_max = min(max(math.ceil(y_max), 0), height_image - 1)

    print x_min, x_max, y_min, y_max

    img[y_min:y_max + 1, x_min:x_max + 1] = [255, 0, 0]

    alinea.phenomenal.result_viewer.show_image(img)


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    example_calibration(
        '../../local/CHESSBOARD/', 'example_calibration_model')

    example_calibration_reprojection(
        '../../local/CHESSBOARD/', 'example_calibration_model')
