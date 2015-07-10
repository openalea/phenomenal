# -*- python -*-
#
#       calibration_camera: Module Description
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
import cv2

#       =======================================================================
#       Local Import 


#       =======================================================================
#       Code

def get_chessboard_corners(image, size_chessboard):
    """
    Return position x, y of chessboard corners

    :param image:
    :param size_chessboard:
    :return:
    """
    try:

        found, corners = cv2.findChessboardCorners(
            image, size_chessboard)

        if found:
            cv2.cornerSubPix(
                image,
                corners,
                (11, 11),
                (-1, -1),
                criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
                          30,
                          0.001))
        else:
            print "Error corners not find"
            return None

    except cv2.error:
        print "cv2 error get_corners, calibration.py"
        return None

    return corners


def get_global_tvec(tvecs):
    """
    Compute the tvec mean and return it

    :param tvecs:
    :return:
    """
    x = [t[0][0] for t in tvecs]
    y = [t[1][0] for t in tvecs]
    z = [t[2][0] for t in tvecs]

    x_mean = np.mean(x)
    y_mean = np.mean(y)
    z_mean = np.mean(z)

    return x_mean, y_mean, z_mean


def get_global_tvec_2(tvecs, angles):
    """
    Compute the global tvec with Christian methods

    :param tvecs:
    :param angles:
    :return:
    """
    x = [t[0][0] for t in tvecs]
    y = [t[1][0] for t in tvecs]
    z = [t[2][0] for t in tvecs]

    # fit circle
    points = dict(zip(angles, zip(x, y, z)))
    A, B, C = [np.array(points[k]) for k in [21, 45, 69]]
    a = np.linalg.norm(C - B)
    b = np.linalg.norm(C - A)
    c = np.linalg.norm(B - A)
    s = (a + b + c) / 2
    R = a * b * c / 4 / np.sqrt(s * (s - a) * (s - b) * (s - c))

    b1 = a * a * (b * b + c * c - a * a)
    b2 = b * b * (a * a + c * c - b * b)
    b3 = c * c * (a * a + b * b - c * c)
    P = np.column_stack((A, B, C)).dot(np.hstack((b1, b2, b3)))
    P /= b1 + b2 + b3

    return P


def get_calibration(files_name, chessboard, size_chessboard):
    """
    1. Load images files in grayscale
    2. Find chessboard corners
    3. Compute calibrate camera parameters
    4. Return this paremeters

    :param files: image files names
    :param chessboard:
    :param size_chessboard:
    :return:
    """

    # Read images
    images = map(lambda img: cv2.imread(img, cv2.CV_LOAD_IMAGE_GRAYSCALE),
                 files_name)

    # Get corners images
    image_points = map(lambda img: get_chessboard_corners(
        img, size_chessboard), images)

    # Clean possibly None corners
    image_points = [corners for corners in image_points if corners is not None]
    object_points = [chessboard] * len(image_points)

    ret, mtx, dists, rvecs, tvecs = cv2.calibrateCamera(
        object_points,
        image_points,
        images[0].shape[0:2],
        flags=(cv2.cv.CV_CALIB_ZERO_TANGENT_DIST +
               cv2.cv.CV_CALIB_FIX_K1 +
               cv2.cv.CV_CALIB_FIX_K2 +
               cv2.cv.CV_CALIB_FIX_K3))

    return image_points, object_points, ret, mtx, dists, rvecs, tvecs


def calibrate(files, angles, chessboard, size_chessboard):
    """
    Calibrate camera and return matrix (focal, image center) parameters and
    dict of rvec, tvec value for each angle key.

    Return also the global_tvec compute.

    :param files:
    :param angles:
    :param chessboard:
    :param size_chessboard:
    :return:
    """
    image_points, object_points, ret, mtx, dists, rvecs, tvecs = \
        get_calibration(files, chessboard, size_chessboard)

    global_tvec = get_global_tvec(tvecs)

    angle_rvec_tvec = dict()
    for i in range(len(angles)):
        angle_rvec_tvec[angles[i]] = (rvecs[i], tvecs[i])

    return mtx, angle_rvec_tvec, global_tvec


def get_reprojection_error(image_points, object_points, mtx, rvecs, tvecs):
    """
    Return mean reprojection error

    :param image_points:
    :param object_points:
    :param mtx:
    :param rvecs:
    :param tvecs:
    :return:
    """

    mean_error = 0
    for i in range(len(object_points)):
        image_points_2, _ = cv2.projectPoints(object_points[i],
                                              rvecs[i],
                                              tvecs[i],
                                              mtx,
                                              None)

        error = cv2.norm(image_points[i], image_points_2, cv2.NORM_L2) / len(
            image_points_2)

        mean_error += error

    return mean_error / len(object_points)
