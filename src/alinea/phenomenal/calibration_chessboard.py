# -*- python -*-
#
#       calibration_chessboard.py :
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

""" Include Chessboard object and class """

#       ========================================================================
#       External Import

import pickle
import pylab
import cv2
import numpy as np


#       ========================================================================
#       Code

class Chessboard(object):
    def __init__(self, square_size, length, height):

        # Initialization
        self.square_size = square_size
        self.shape = (length, height)
        self.object_points = np.zeros((length * height, 3), np.float32)

        # Build Chessboard
        self.object_points[:, :2] = \
            np.mgrid[0:length, 0:height].T.reshape(-1, 2) * self.square_size

        # 48 points are stored in an 48x3 array obj
        # choose bottom-left corner as origin, to match australian convention
        self.object_points = self.object_points - self.object_points[40, :]

    def print_value(self):
        print 'Chessboard Object Values :'
        print 'Square size : ', self.square_size
        print 'Shape : ', self.shape
        print 'Object points : ', self.object_points

    def find_corners(self, image):
        try:

            found, corners = cv2.findChessboardCorners(
                image,
                self.shape,
                flags=cv2.CALIB_CB_ADAPTIVE_THRESH +
                      cv2.CALIB_CB_NORMALIZE_IMAGE)

            if found:
                cv2.cornerSubPix(image, corners, (11, 11), (-1, -1),
                                 criteria=(cv2.TERM_CRITERIA_EPS +
                                           cv2.TERM_CRITERIA_MAX_ITER,
                                           30,
                                           0.001))
            else:
                print "Error : Corners not find"
                return None

        except cv2.error:
            print "Error : cv2, get_corners, calibration.py"
            return None

        return corners

    def plot_corners(self, corners, image, figure_name='Image'):

        y_min = min(corners[:, 0, 0])
        y_max = max(corners[:, 0, 0])
        x_min = min(corners[:, 0, 1])
        x_max = max(corners[:, 0, 1])
        r = 50

        image = cv2.drawChessboardCorners(image, self.shape, corners, True)
        image = image[x_min - r:x_max + r, y_min - r:y_max + r]

        cv2.namedWindow(figure_name, cv2.WINDOW_NORMAL)
        cv2.imshow(figure_name, image)
        cv2.waitKey()

    def plot_points(self, projection_points, image, figure_name='Image'):

        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        projection_points = projection_points.astype(int)
        image[projection_points[:, 0, 1],
              projection_points[:, 0, 0]] = [0, 0, 255]

        f = pylab.figure()
        f.canvas.set_window_title(figure_name)
        pylab.title(figure_name)
        pylab.imshow(image)
        pylab.show()

        f.clf()
        pylab.close()


class Calibration(object):
    def __init__(self, images, chessboard, verbose=False):
        self.focal_matrix = None
        self.rotation_vectors = dict()
        self.translation_vectors = dict()
        self.distortion_coefficient = None

        self.calibrate(images, chessboard, verbose=verbose)

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

        for angle in self.rotation_vectors:
            if self.rotation_vectors[angle] is not None:
                print 'Angle : %d - rot : %f, %f, %f' % (
                    angle,
                    self.rotation_vectors[angle][0][0],
                    self.rotation_vectors[angle][1][0],
                    self.rotation_vectors[angle][2][0])
            else:
                print 'Angle : %d - rot : None' % angle

        for angle in self.translation_vectors:
            if self.translation_vectors[angle] is not None:
                print 'Angle : %d - trans : %f, %f, %f' % (
                    angle,
                    self.translation_vectors[angle][0][0],
                    self.translation_vectors[angle][1][0],
                    self.translation_vectors[angle][2][0])
            else:
                print 'Angle : %d - trans : None' % angle

    def project_point(self, point, angle):

        projection_point, _ = cv2.projectPoints(point,
                                                self.rotation_vectors[angle],
                                                self.translation_vectors[angle],
                                                self.focal_matrix,
                                                self.distortion_coefficient)

        return projection_point[:, 0, 1], projection_point[:, 0, 0]

    def project_points(self, points, angle):

        projection_point, _ = cv2.projectPoints(points,
                                                self.rotation_vectors[angle],
                                                self.translation_vectors[angle],
                                                self.focal_matrix,
                                                self.distortion_coefficient)

        return projection_point

    def calibrate(self, images, chessboard, verbose=False):
        # Get corners images
        image_points = list()
        for angle in images:
            corners = chessboard.find_corners(images[angle])

            if corners is not None:
                image_points.append(corners)

                # if verbose is True:
                #     chessboard.plot_corners(corners, images[angle], str(angle))

            else:
                self.rotation_vectors[angle] = None
                self.translation_vectors[angle] = None

        # Clean possibly None corners
        image_points = [corners for corners in image_points if corners is not None]

        object_points = [chessboard.object_points] * len(image_points)

        # create initial cameraMatrix and distortion coefficient
        camera_matrix = np.zeros((3, 3), dtype=np.float32)

        distortion_coefficient = np.zeros((5, 1), np.float32)

        ret, focal_matrix, distortion_coefficient, rvecs, tvecs = \
            cv2.calibrateCamera(object_points,
                                image_points,
                                images[0].shape[0:2],
                                camera_matrix,
                                distortion_coefficient)

        self.focal_matrix = focal_matrix
        self.distortion_coefficient = distortion_coefficient

        i = 0
        for angle in images:

            if (angle in self.rotation_vectors and
                    self.rotation_vectors[angle] is None):
                continue

            self.rotation_vectors[angle] = rvecs[i]
            self.translation_vectors[angle] = tvecs[i]

            if verbose is True:
                projection_points = self.project_points(
                    chessboard.object_points, angle)

                chessboard.plot_points(
                    projection_points, images[angle], figure_name=str(angle))

            i += 1

    def projection_error(self, image_points, object_points, angle):
        """ Return mean projection error """

        mean_error = 0
        for angle in object_points:
            project_point, _ = cv2.projectPoints(
                object_points[angle],
                self.rotation_vectors[angle],
                self.translation_vectors[angle],
                self.focal_matrix,
                self.distortion_coefficient)

            error = cv2.norm(image_points[angle],
                             project_point,
                             cv2.NORM_L2) / len(project_point)

            mean_error += error

        return mean_error / len(object_points)

    def project_position(self, point, angle):

        projection_point, _ = cv2.projectPoints(point,
                                                self.rotation_vectors[angle],
                                                self.translation_vectors[angle],
                                                self.focal_matrix,
                                                self.distortion_coefficient)

        return projection_point[0, 0, 0], projection_point[0, 0, 1]
