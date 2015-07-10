# -*- python -*-
#
#       test_calibration: Module Description
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
import numpy as np
import alinea.phenomenal.calibration_chessboard as calibration_chessboard
import glob


#       =======================================================================
#       Local Import

#       =======================================================================
#       Code


def get_chessboard():
    """
    Return chessboard position in real world (arbitrary data)

    :return:
    """
    # mm is the unit of australian pipeline
    square_size = 47

    object_points = np.zeros((8 * 6, 3), np.float32)
    object_points[:, :2] = np.mgrid[0:8, 0:6].T.reshape(-1, 2) * square_size

    # 48 points are stored in an 48x3 array objp
    # print objp, np.shape(objp)

    # choose bottom-left corner as origin, to match australian convention
    object_points = object_points - object_points[40, :]

    return object_points


def get_parameters():
    directory = '../../share/CHESSBOARD/'
    files = glob.glob(directory + '*.png')
    angles = map(lambda x: int((x.split('_sv')[1]).split('.png')[0]), files)

    chessboard = get_chessboard()
    size_chessboard = (8, 6)

    return files, angles, chessboard, size_chessboard


def test_calibrate():
    files, angles, chessboard, size_chessboard = get_parameters()

    mtx, angle_rvec_tvec, global_tvec = calibration_chessboard.calibrate(
        files, angles, chessboard, size_chessboard)

    print "Mtx : ", mtx
    print "Angles - rvec - tvec : ", angle_rvec_tvec
    print "Global tvec : ", global_tvec


def test_get_calibration():
    files, angles, chessboard, size_chessboard = get_parameters()

    image_points, object_points, ret, mtx, dists, rvecs, tvecs = \
        calibration_chessboard.get_calibration(files,
                                               chessboard,
                                               size_chessboard)

    reprojection_error = calibration_chessboard.get_reprojection_error(
        image_points,
        object_points,
        mtx,
        rvecs,
        tvecs)

    print "reprojection_error : ", reprojection_error
