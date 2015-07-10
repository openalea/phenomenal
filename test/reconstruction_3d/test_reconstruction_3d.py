# -*- python -*-
#
#       test_octree: Module Description
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
#       =======================================================================

"""
Write the doc here...
"""

__revision__ = ""

#       =======================================================================
#       External Import 
import cv2
import numpy as np
import glob


#       =======================================================================
#       Local Import 

import alinea.phenomenal.reconstruction_3d as reconstruction_3d
import alinea.phenomenal.calibration_chessboard as calibration_chessboard
import tools_test

#       =======================================================================


def get_chessboard():
    # mm is the unit of australian pipeline
    square_size = 47

    objp = np.zeros((8 * 6, 3), np.float32)
    objp[:, :2] = np.mgrid[0:8, 0:6].T.reshape(-1, 2) * square_size

    # 48 points are stored in an 48x3 array objp
    # print objp, np.shape(objp)

    # choose bottom-left corner as origin, to match australian convention
    objp = objp - objp[40, :]

    return objp


def initialize_tvecs_rvecs(angles, angle_rvec_tvec):
    tvecs = list()
    rvecs = list()

    for angle in angles:
        tvecs.append(
            np.ndarray(shape=(3, 1), buffer=np.array(
                [[angle_rvec_tvec[angle][1][0][0],
                  angle_rvec_tvec[angle][1][1][0],
                  angle_rvec_tvec[angle][1][2][0]]])))

        rvecs.append(
            np.ndarray(shape=(3, 1), buffer=np.array(
                [[angle_rvec_tvec[angle][0][0][0],
                  angle_rvec_tvec[angle][0][1][0],
                  angle_rvec_tvec[angle][0][2][0]]])))

    return tvecs, rvecs


def test_reconstruction_3d():

    #   =======================================================================

    images_path = ['../../share/data/Samples_binarization_2/0.png',
                   '../../share/data/Samples_binarization_2/1.png',
                   '../../share/data/Samples_binarization_2/2.png',
                   '../../share/data/Samples_binarization_2/3.png']

    images = []
    for image_name in images_path:
        im = cv2.imread(image_name, cv2.CV_LOAD_IMAGE_GRAYSCALE)
        images.append(im)

    #   =======================================================================

    directory = '../../share/CHESSBOARD/'
    files = glob.glob(directory + '*.png')

    angles = map(lambda x: int((x.split('_sv')[1]).split('.png')[0]), files)

    chessboard = get_chessboard()
    size_chessboard = (8, 6)

    mtx, angle_rvec_tvec, origin = calibration_chessboard.calibrate(
        files, angles, chessboard, size_chessboard)

    #   =======================================================================

    mtx = np.ndarray(shape=(3, 3), buffer=np.array(mtx))

    tvecs, rvecs = initialize_tvecs_rvecs(angles, angle_rvec_tvec)

    print rvecs, mtx, tvecs

    octree_result = reconstruction_3d.reconstruction_3d(images, rvecs, mtx, tvecs, 1)

    tools_test.show_cube(octree_result)


def test_reconstruction_3d_fast():

    images_path = ['../../share/data/Samples_binarization_2/0.png',
                   '../../share/data/Samples_binarization_2/30.png',
                   '../../share/data/Samples_binarization_2/60.png',
                   '../../share/data/Samples_binarization_2/90.png']

    images = tools_test.load_images(images_path)

    #
    # =======================================================================4

    rvecs = [
        np.ndarray(shape=(3, 1), buffer=np.array(
            [[-0.27402718, -0.87116086, -0.05985117]])),    # 0

        np.ndarray(shape=(3, 1), buffer=np.array(
            [[-0.28180665, -0.35137834, -0.00166627]])),    # 30

        np.ndarray(shape=(3, 1), buffer=np.array(
            [[-0.2752881, 0.17236049, 0.05475218]])),       # 60

        np.ndarray(shape=(3, 1), buffer=np.array(
            [[-0.25698405, 0.69616722, 0.10967995]]))]      # 90

    tvecs = [
        np.ndarray(shape=(3, 1), buffer=np.array(
            [[83.119002438165367, 7.0562545266974652, 5302.8162746685748]])),
        np.ndarray(shape=(3, 1), buffer=np.array(
            [[-69.78217007915454, 6.3708794194138729, 5301.9661983221804]])),
        np.ndarray(shape=(3, 1), buffer=np.array(
            [[-202.56927805892792, 8.4271016681049211, 5380.8695577886356]])),
        np.ndarray(shape=(3, 1), buffer=np.array(
            [[-278.78287741730423, 12.48355197043308, 5513.1481414823902]]))]

    mtx = np.ndarray(shape=(3, 3), buffer=np.array(
        [[4802.63017, 0.0, 1015.41022],
         [0.0, 4801.35696, 1111.48747],
         [0.0, 0.0, 1.0]]))

    # tvec = np.ndarray(
    #     shape=(3, 1),
    #     buffer=np.array([[-147.763327299, 8.84099491093, 5387.66421516]]))

    #   =======================================================================

    octree_result = reconstruction_3d.reconstruction_3d(images, rvecs, mtx, tvecs, 1)

    tools_test.show_cube(octree_result, 5)



test_reconstruction_3d_fast()
