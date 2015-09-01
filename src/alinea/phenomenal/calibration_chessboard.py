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
import numpy as np
import pickle
#       =======================================================================
#       Local Import 


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
        self.focal_matrix = None
        self.rotation_vectors = None
        self.translation_vectors = None
        self.distortion_coefficient = None

    def __getitem__(self, item):
        return (self.focal_matrix,
                self.rotation_vectors[item],
                self.translation_vectors[item],
                self.distortion_coefficient)

    def write_calibration(self, filename):
        with open(filename + '.pickle', 'wb') as handle:
            pickle.dump(self, handle)

    @staticmethod
    def read_calibration(filename):
        with open(filename + '.pickle', 'rb') as handle:
            return pickle.load(handle)

    def print_value(self):
        print 'Focal Matrix : ', self.focal_matrix
        print 'Distortion coefficient : ', self.distortion_coefficient

        for angle in self.rotation_vectors.keys():
            if self.rotation_vectors[angle] is not None:
                print 'Angle : %d - rot : %f, %f, %f' % (
                    angle,
                    self.rotation_vectors[angle][0][0],
                    self.rotation_vectors[angle][1][0],
                    self.rotation_vectors[angle][2][0])

        for angle in self.translation_vectors.keys():
            if self.translation_vectors[angle] is not None:
                print 'Angle : %d - trans : %f, %f, %f' % (
                    angle,
                    self.translation_vectors[angle][0][0],
                    self.translation_vectors[angle][1][0],
                    self.translation_vectors[angle][2][0])


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

    my_calibration = Calibration()
    my_calibration.rotation_vectors = dict()
    my_calibration.translation_vectors = dict()

    # Get corners images
    image_points = list()
    for angle in images:
        corners = find_chessboard_corners(images[angle], chessboard.shape)
        print angle
        if corners is not None:
            image_points.append(corners)

            if angle % 30 == 0:

                y_min = min(corners[:, 0, 0])
                y_max = max(corners[:, 0, 0])
                x_min = min(corners[:, 0, 1])
                x_max = max(corners[:, 0, 1])

                range = 50

                img = images[angle]
                img = cv2.drawChessboardCorners(
                    img, chessboard.shape, corners, True)

                img = img[x_min - range:x_max + range,
                          y_min - range:y_max + range]

                cv2.namedWindow(str(angle), cv2.WINDOW_NORMAL)
                cv2.imshow(str(angle), img)
                cv2.waitKey()

        else:
            my_calibration.rotation_vectors[angle] = None
            my_calibration.translation_vectors[angle] = None

    # Clean possibly None corners
    image_points = [corners for corners in image_points if corners is not None]

    object_points = [chessboard.object_points] * len(image_points)

    print images[0].shape[0:2]

    # create initial cameraMatrix and distCoeffs
    cameraMatrix = np.zeros((3, 3), dtype=np.float32)

    distCoeffs = np.zeros((5, 1), np.float32)

    ret, mtx, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
        object_points,
        image_points,
        images[0].shape[0:2],
        cameraMatrix,
        distCoeffs)

        # flags=cv2.CALIB_ZERO_TANGENT_DIST +
        #       cv2.CALIB_FIX_K1 +
        #       cv2.CALIB_FIX_K2 +
        #       cv2.CALIB_FIX_K3)

    my_calibration.focal_matrix = mtx
    my_calibration.distortion_coefficient = dist_coeffs

    i = 0
    for angle in images:

        if angle in my_calibration.rotation_vectors:
            if my_calibration.rotation_vectors[angle] is None:
                print "Not angle : ", angle
                continue

        my_calibration.rotation_vectors[angle] = rvecs[i]
        my_calibration.translation_vectors[angle] = tvecs[i]


        if angle % 30 == 0:
            print object_points[i]
            pts = np.float32([[0, 0, -47]])
            projection_point, _ = cv2.projectPoints(pts,
                                                    rvecs[i],
                                                    tvecs[i],
                                                    mtx,
                                                    dist_coeffs)



            img = images[angle]
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

            projection_point = projection_point.astype(int)
            img[projection_point[:, 0, 1],
                projection_point[:, 0, 0]] = [0, 0, 255]

            import pylab
            f = pylab.figure()
            f.canvas.set_window_title(str(angle))
            pylab.title(str(angle))
            pylab.imshow(img, cmap=pylab.cm.binary)
            pylab.show()

        i += 1

    return my_calibration


    # return image_points, object_points, ret, mtx, dist_coeffs, rvecs, tvecs


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
    # image_points, object_points, ret, mtx, dist_coeffs, rvecs, tvecs = \
    #     calibration_with_chessboard(images, chessboard)

    return calibration_with_chessboard(images, chessboard)


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
