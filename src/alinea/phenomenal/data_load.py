# -*- python -*-
#
#       data_load.py : Function for load data
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
import cv2
import glob
import os

#       ========================================================================
#       Local Import
import openalea.deploy.shared_data
import alinea.phenomenal

#       ========================================================================


def test_plant_1_images_binarize():
    shared_directory = openalea.deploy.shared_data.shared_data(
        alinea.phenomenal)

    data_directory = shared_directory + '/test_plant_1/images_binarize/'
    files_path = glob.glob(data_directory + '*.png')
    angles = map(lambda x: int((x.split('\\')[-1]).split('.png')[0]),
                 files_path)

    images = dict()
    for i in range(len(files_path)):
        images[angles[i]] = cv2.imread(files_path[i], cv2.IMREAD_UNCHANGED)

    return images


def test_plant_1_chessboards_path():
    shared_directory = openalea.deploy.shared_data.shared_data(
        alinea.phenomenal)

    data_directory = shared_directory + '/test_plant_1/'

    chessboards_path = list()
    chessboards_path.append(data_directory + 'chessboard_1')
    chessboards_path.append(data_directory + 'chessboard_2')

    return chessboards_path


def test_plant_1_calibration_params_path():
    shared_directory = openalea.deploy.shared_data.shared_data(
        alinea.phenomenal)

    data_directory = shared_directory + '/test_plant_1/'

    params_camera_path = data_directory + 'params_camera'

    params_chessboards_path = list()
    params_chessboards_path.append(data_directory + 'params_chessboard_1')
    params_chessboards_path.append(data_directory + 'params_chessboard_2')

    return params_camera_path, params_chessboards_path


def test_plant_1_points_3d_path(radius=2):
    shared_directory = openalea.deploy.shared_data.shared_data(
        alinea.phenomenal)

    data_directory = shared_directory + '/test_plant_1/'

    if 1 <= int(radius) <= 15:
        return data_directory + 'points_3d_radius_' + str(int(radius))

    return None


def side_blob_test(number=1):
    shared_directory = openalea.deploy.shared_data.shared_data(
        alinea.phenomenal)

    data_directory = shared_directory + '/images/'

    if 1 <= int(number) <= 4:
        return cv2.imread(data_directory + 'side_blob_test_' +
                          str(int(number)) + '.png')

    return None


def illumination_test_image(number=1):
    shared_directory = openalea.deploy.shared_data.shared_data(
        alinea.phenomenal)

    data_directory = shared_directory + '/images/'

    if 1 <= int(number) <= 4:
        return cv2.imread(data_directory + 'illumination_test_image_' +
                          str(int(number)) + '.png')

    return None


def top_blob_test():
    shared_directory = openalea.deploy.shared_data.shared_data(
        alinea.phenomenal)
    return cv2.imread(shared_directory + '/images/' + 'top_blob_test.png')
