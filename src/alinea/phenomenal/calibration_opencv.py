# -*- python -*-
#
#       calibration_opencv.py :
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
import numpy
import pickle


#       ========================================================================
#       Local Import
import openalea.deploy.shared_data
import alinea.phenomenal
import alinea.phenomenal.calibration

#       ========================================================================
#       Code


class Calibration(alinea.phenomenal.calibration.Calibration, object):
    def __init__(self, images, chessboard, verbose=False):
        self.focal_matrix = None
        self.rotation_vectors = dict()
        self.translation_vectors = dict()
        self.distortion_coefficient = None

        self.calibrate(images, chessboard, verbose=verbose)

    def write_calibration(self, filename, file_is_in_share_directory=True):

        if file_is_in_share_directory is True:
            share_data_directory = openalea.deploy.shared_data.shared_data(
                alinea.phenomenal)

            file_path = share_data_directory / filename + '.pickle'
        else:
            file_path = filename + '.pickle'

        with open(file_path, 'wb') as handle:
            pickle.dump(self, handle)

    @staticmethod
    def read_calibration(filename, file_is_in_share_directory=True):

        if file_is_in_share_directory is True:
            share_data_directory = openalea.deploy.shared_data.shared_data(
                alinea.phenomenal)

            file_path = share_data_directory / filename + '.pickle'
        else:
            file_path = filename + '.pickle'

        with open(file_path, 'rb') as handle:
            return pickle.load(handle)

    def print_value(self):
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

    def project_points(self, points, angle):

        projection_point, _ = cv2.projectPoints(points,
                                                self.rotation_vectors[angle],
                                                self.translation_vectors[angle],
                                                self.focal_matrix,
                                                self.distortion_coefficient)

        return projection_point

    def project_point(self, point, angle):

        pt = numpy.reshape(point, (1, 3))
        pt = pt.astype(numpy.float32)
        projection_point, _ = cv2.projectPoints(pt,
                                                self.rotation_vectors[angle],
                                                self.translation_vectors[angle],
                                                self.focal_matrix,
                                                self.distortion_coefficient)

        return projection_point[0, 0, 0], projection_point[0, 0, 1]

    def calibrate(self, images, chessboard, verbose=False):
        # Get corners images
        image_points = list()
        for angle in images:
            corners = chessboard.find_corners(images[angle])

            if corners is not None:
                image_points.append(corners)
            else:
                self.rotation_vectors[angle] = None
                self.translation_vectors[angle] = None

        # Clean possibly None corners
        image_points = [corners for corners in image_points if corners is not None]

        object_points = [chessboard.object_points] * len(image_points)

        # create initial cameraMatrix and distortion coefficient
        camera_matrix = numpy.zeros((3, 3), dtype=numpy.float32)

        distortion_coefficient = numpy.zeros((5, 1), numpy.float32)

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

