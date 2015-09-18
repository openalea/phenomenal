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
import cv2
from math import radians
import numpy as np
import pickle
from scipy.optimize import leastsq

#       =======================================================================
#       Local Import 

from calibration_model import camera_frame, chess_corners, chess_frame
from camera import Camera

#       =======================================================================
#       Code

class Chessboard(object):
    def __init__(self, square_size, length, height):
        self.square_size = square_size
        self.shape = (length, height)
        self.object_points = np.zeros((length * height, 3), np.float32)
        self.initialize_chessboard()

    def initialize_chessboard(self):
        self.object_points[:, :2] = np.mgrid[0:8, 0:6].T.reshape(
            -1, 2) * self.square_size

        # 48 points are stored in an 48x3 array objp
        # print objp, np.shape(objp)
        # choose bottom-left corner as origin, to match australian convention
        self.object_points = self.object_points - self.object_points[40, :]


class Calibration(object):
    def __init__(self):
        self._sca_x = None
        self._sca_y = None
        self._dist_cam = None
        self._offset = None
        self._z_cam = None
        self._azim_cam = None
        self._elev_cam = None
        self._tilt_cam = None
        self._offset_angle = None

    def __getitem__(self, alpha):
        cam = Camera((2056, 2454), (self._sca_x, self._sca_y))

        fr = camera_frame(self._dist_cam, self._offset, self._z_cam,
                          self._azim_cam, self._elev_cam, self._tilt_cam,
                          self._offset_angle, radians(alpha))

        return cam, fr

    def write_calibration(self, filename):
        cal_params = (self._sca_x, self._sca_y,
                      self._dist_cam, self._offset, self._z_cam,
                      self._azim_cam, self._elev_cam, self._tilt_cam,
                      self._offset_angle)
        with open(filename + '.pickle', 'wb') as handle:
            pickle.dump(cal_params, handle)

    @staticmethod
    def read_calibration(filename):
        with open(filename + '.pickle', 'rb') as handle:
            params = pickle.load(handle)
            print params
            sca_x, sca_y = params[0:2]
            dist_cam, offset, z_cam = params[2:5]
            azim_cam, elev_cam, tilt_cam, offset_angle = params[5:9]

            cal = Calibration()
            cal._sca_x = sca_x
            cal._sca_y = sca_y
            cal._dist_cam = dist_cam
            cal._offset = offset
            cal._z_cam = z_cam
            cal._azim_cam = azim_cam
            cal._elev_cam = elev_cam
            cal._tilt_cam = tilt_cam
            cal._offset_angle = offset_angle

            return cal


    def print_value(self):
        for angle in (0, 30, 60, 90):
            print "angle", angle
            print self[angle]


def find_chessboard_corners(image, size_chessboard):
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


def calibration_with_chessboard(images, chessboard):
    """
    1. Find chessboard corners
    2. Compute calibrate camera parameters
    3. Return this paremeters

    :param files: image files names
    :param chessboard:
    :param size_chessboard:
    :return:
    """

    # Get corners images
    image_points = list()
    for angle in images.keys():
        image_points.append(find_chessboard_corners(images[angle],
                                                    chessboard.shape))

    # Clean possibly None corners
    image_points = [corners for corners in image_points if corners is not None]

    object_points = [chessboard.object_points] * len(image_points)

    ret, mtx, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
        object_points,
        image_points,
        images[0].shape[0:2])
        # flags=(cv2.cv.CV_CALIB_ZERO_TANGENT_DIST +
        #        cv2.cv.CV_CALIB_FIX_K1 +
        #        cv2.cv.CV_CALIB_FIX_K2 +
        #        cv2.cv.CV_CALIB_FIX_K3))

    return image_points, object_points, ret, mtx, dist_coeffs, rvecs, tvecs


def calibration(images, chessboard):
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
    image_points, object_points, ret, mtx, dist_coeffs, rvecs, tvecs = \
        calibration_with_chessboard(images, chessboard)

    my_calibration = Calibration()
    my_calibration.focal_matrix = mtx
    my_calibration.distortion_coefficient = dist_coeffs
    my_calibration.rotation_vectors = dict()
    my_calibration.translation_vectors = dict()

    i = 0
    for angle in images.keys():
        my_calibration.rotation_vectors[angle] = rvecs[i]
        my_calibration.translation_vectors[angle] = tvecs[i]
        i += 1

    return my_calibration


def compute_reprojection_error(image_points, object_points, mtx, rvecs, tvecs):
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
        print(image_points_2)

        error = cv2.norm(image_points[i], image_points_2, cv2.NORM_L2) / len(
            image_points_2)

        mean_error += error

    return mean_error / len(object_points)


def project(pt, fr_chess, fr_cam, cam):
    return cam.pixel_coordinates(fr_cam.local_point(fr_chess.global_point(pt)))


def find_calibration_model_parameters(chessboard_ref, chessboard_corners, guess):
    """ Find physical parameters associated with a camera
    (i.e. distances and angles), using pictures of a rotating
    chessboard.

    args:
     - 'chessboard_ref' (Chessboard): reference chessboard
     - 'chessboard_corners' dict of (angle, list of pts): for
                    a picture taken with a given angle, list
                    the coordinates of all intersections on
                    the chessboard in the picture
    - 'guess' (): initial guess for calibration model
    """
    img_size = (2056, 2454)  # TODO: GRUUIK hardcoded

    chessboard_pts = chess_corners(chessboard_ref)
    cv_pts = chessboard_corners

    print " fit model on computed points"
    def fit(params):
        err = []
        fr_chess = chess_frame(*params[0:5])
        cam = Camera(img_size, params[5:7])
        dist_cam, offset, z_cam, azim_cam, elev_cam, tilt_cam, offset_angle = params[7:14]

        for alpha, ref_pts in cv_pts.items():
            fr_cam = camera_frame(dist_cam, offset, z_cam, azim_cam, elev_cam, tilt_cam, offset_angle, radians(alpha))
            pts = [project(pt, fr_chess, fr_cam, cam) for pt in chessboard_pts]

            err.append(np.linalg.norm(np.array(pts) - ref_pts, axis=1).sum())

        print sum(err)
        return err

    # print fit(guess)
    res = leastsq(fit, guess, maxfev=5000)

    with open("fitted - step.pkl", 'wb') as f:
        pickle.dump(res[0], f)

    sca_x, sca_y, = res[0][5:7]
    dist_cam, offset, z_cam, azim_cam, elev_cam, tilt_cam, offset_angle = res[0][7:14]

    cal = Calibration()
    cal._sca_x = sca_x
    cal._sca_y = sca_y
    cal._dist_cam = dist_cam
    cal._offset = offset
    cal._z_cam = z_cam
    cal._azim_cam = azim_cam
    cal._elev_cam = elev_cam
    cal._tilt_cam = tilt_cam
    cal._offset_angle = offset_angle

    return cal


def plot_calibration(chessboard, cv_pts, guess, alpha):
    import matplotlib.pyplot as plt

    img = plt.imread('../../local/data/CHESSBOARD/2013-07-11 15_49_42vis_sv%.3d.png' % alpha)
    plt.imshow(img)
    print cv_pts[alpha].shape

    plt.plot(cv_pts[alpha][:,0], cv_pts[alpha][:,1], 'r+')
    plt.show()
