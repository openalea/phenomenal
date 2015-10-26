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
import alinea.phenomenal.viewer
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

    # print " find chessboard pts on each image"
    # cv_pts = dict()
    # for alpha, img in images.items():
    #     print alpha
    #     pts = chessboard.find_corners(img)
    #     if pts is not None:
    #         cv_pts[alpha] = pts[:, 0, :]


    # with open('corners_points', 'wb') as corners_points:
    #     pickle.dump(cv_pts, corners_points)

    import pickle
    with open('corners_points', 'rb') as corners_points:
        cv_pts = pickle.load(corners_points)

    #=> 492 to 486
    guess = numpy.array([
        -164.36793985970391,    # x position of chess in world frame
        -184.26982549215279,    # y position of chess in world frame
        1016.2924110974527,     # z position of chess in world frame

        -0.24676783786914835,   # elevation angle around local x axis
        0.033230717529020827,   # rotation angle around local z axis

        # scaling factor between real coordinates and pixel coordinates
        4325.1372442743241,
        # scaling factor between real coordinates and pixel coordinates
        4314.5457485003662,
        5053.3551632860035,     # distance of camera to rotation axis

        -2.4495310698780379,    # offset angle in radians for rotation

        666.05979874456671,     # z position of cam in world frame when alpha=0

        0.021140291507288664,   # azimuth angle of camera (around local y axis)
        # elevation angle of camera (around local x axis)
        0.00042593152159524892,
        # tilt angle of camera (around local z axis)
        -0.0036106966523099557,
        0.85901926301294507])    # rotation offset around z_axis in world frame

    #=> 545 to 435
    guess = numpy.array([1.65469405e+02,
                         1.84542176e+02,
                         -9.34983079e+01,

                         -2.48540532e-01,
                         -3.10804882e+00, #here

                         4.40369110e+03,
                         4.41278698e+03,
                         5.15430960e+03,

                         6.88291474e-01, #here

                         2.93955342e+02,
                         2.17052769e-01,
                         7.98941171e-03,
                         -3.81842421e-03,
                         6.66808730e-01])
    #=> 369
    # guess = numpy.array([-1.65237625e+02,
    #                      -1.84167338e+02,
    #                      9.46592957e+02,
    #                      -2.47695734e-01,
    #                      3.38093081e-02,
    #                      4.55763938e+03,
    #                      4.55723609e+03,
    #                      5.31682341e+03,
    #                      -2.45361180e+00,
    #                      5.62657392e+02,
    #                      9.54936477e-02,
    #                      7.03082714e-03,
    #                      -3.53976811e-03,
    #                      7.88658695e-01]),


# array([ -1.61725390e+02,  -1.82867365e+02,  -4.11811390e-08,
#          3.39820284e+00,   3.45550010e-02,   3.04598591e+03,
#          3.05096267e+03,   3.61252721e+03,   3.83090924e+00,
#          3.17462790e+02,   3.18294830e+00,   3.15020145e+00,
#          3.13892219e+00,   3.98449077e+00])


# array([ -1.77716315e+02,  -1.81087716e+02,   7.17079677e+02,
#         -2.77712973e-01,   3.44009832e-02,   4.34644447e+03,
#          4.36831988e+03,   5.12837533e+03,  -2.46988908e+00,
#          5.13173638e+02,   7.25934401e-01,  -2.91964242e-02,
#         -2.89082501e-03,   1.72917739e-01])

    guess = None

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

    alinea.phenomenal.viewer.show_image(img)


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    example_calibration(
        '../../local/CHESSBOARD/', 'example_calibration_model')

    example_calibration_reprojection(
        '../../local/CHESSBOARD/', 'example_calibration_model')
