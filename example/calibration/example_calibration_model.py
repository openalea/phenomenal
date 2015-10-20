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
import pickle
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


def example_calibration(data_directory, pickle_name):

    files_sv = glob.glob(data_directory + '*sv*.png')
    angles = map(lambda x: int((x.split('_sv')[1]).split('.png')[0]), files_sv)

    images = dict()
    for i in range(len(files_sv)):
        images[angles[i]] = cv2.imread(files_sv[i], cv2.IMREAD_GRAYSCALE)

    chessboard = alinea.phenomenal.chessboard.Chessboard(47, 8, 6)

    # print " find chessboard pts on each image"
    # cv_pts = {}
    # for alpha, img in images.items():
    #     print alpha
    #     pts = chessboard.find_corners(img)
    #     # pts = cc.find_chessboard_corners(img, chessboard.shape)
    #     if pts is not None:
    #         cv_pts[alpha] = pts[:, 0, :]
    #
    # with open("buffer.pkl", 'wb') as f:
    #     pickle.dump(cv_pts, f)

    with open("buffer.pkl", 'rb') as f:
        cv_pts = pickle.load(f)

    with open("initial guess.pkl", 'rb') as f:
        guess = list(pickle.load(f))

    # cc.plot_calibration(chessboard, cv_pts, guess, 48)
    cal = alinea.phenomenal.calibration_model.Calibration()
    cal.find_model_parameters(chessboard, cv_pts, guess)

    # cal.print_value()
    cal.write_calibration(pickle_name)


def example_calibration_reprojection(data_directory, pickle_name):

    files_sv = glob.glob(data_directory + '*sv*.png')
    angles = map(lambda x: int((x.split('_sv')[1]).split('.png')[0]), files_sv)

    images = dict()
    for i in range(len(files_sv)):
        images[angles[i]] = cv2.imread(files_sv[i], cv2.IMREAD_COLOR)

    calibration = alinea.phenomenal.calibration_model.Calibration.\
        read_calibration(pickle_name, file_is_in_share_directory=True)

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
    # example_calibration('../../local/data/CHESSBOARD/',
    #                     'fitted_result')

    example_calibration_reprojection('../../local/data/CHESSBOARD/',
                                     'fitted_result')
