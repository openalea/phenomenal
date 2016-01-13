# -*- python -*-
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
# ==============================================================================
import cv2
import numpy
import re

import openalea.deploy.shared_data
import alinea.phenomenal
#  =============================================================================


class Calibration(object):
    def __init__(self):
        self.focal_matrix = None
        self.rotation_vectors = dict()
        self.translation_vectors = dict()
        self.distortion_coefficient = None

    def write_calibration(self, filename, file_is_in_share_directory=True):

        if file_is_in_share_directory is True:
            share_data_directory = openalea.deploy.shared_data.shared_data(
                alinea.phenomenal)

            file_path = share_data_directory / filename + '.calib'
        else:
            file_path = filename + '.calib'

        with open(file_path, 'w') as f:
            f.write('%f %f %f %f %f %f %f %f %f\n' %
                    tuple(self.focal_matrix.reshape((9, )).tolist()))

            f.write('%f %f %f %f %f\n' %
                    tuple(self.distortion_coefficient.reshape((5, )).tolist()))

            for angle in self.rotation_vectors:
                x_rvec, y_rvec, z_rvec = tuple(
                    self.rotation_vectors[angle].reshape((3, )).tolist())

                x_tvec, y_tvec, z_tvec = tuple(
                    self.translation_vectors[angle].reshape((3, )).tolist())

                f.write('%f %f %f %f %f %f %f\n' % (angle,
                                                    x_rvec, y_rvec, z_rvec,
                                                    x_tvec, y_tvec, z_tvec))

        f.close()

    @staticmethod
    def read_calibration(filename, file_is_in_share_directory=True):

        if file_is_in_share_directory is True:
            share_data_directory = openalea.deploy.shared_data.shared_data(
                alinea.phenomenal)

            file_path = share_data_directory / filename + '.calib'
        else:
            file_path = filename + '.calib'

        cal = Calibration()

        with open(file_path, 'r') as f:
            token = re.findall(r'[-0-9.]+', f.readline())
            cal.focal_matrix = numpy.array(
                token).reshape((3, 3)).astype(numpy.float)

            token = re.findall(r'[-0-9.]+', f.readline())
            cal.distortion_coefficient = numpy.array(
                token).reshape((5, 1)).astype(numpy.float)

            cal.rotation_vectors = dict()
            cal.translation_vectors = dict()

            for line in f:
                token = re.findall(r'[-0-9.]+', line)

                angle = float(token[0])
                rvec = numpy.array(token[1:4]).reshape(3, 1).astype(numpy.float)
                tvec = numpy.array(token[4:7]).reshape(3, 1).astype(numpy.float)

                cal.rotation_vectors[angle] = rvec
                cal.translation_vectors[angle] = tvec

        f.close()

        return cal

    def __str__(self):

        my_str = ''
        my_str += 'Focal Matrix : ' + str(self.focal_matrix) + '\n'
        my_str += 'Distortion Coefficient : ' + str(
            self.distortion_coefficient) + '\n'

        for angle in self.rotation_vectors:
            if self.rotation_vectors[angle] is not None:
                my_str += 'Angle : %d - rot : %f, %f, %f \n' % (
                    angle,
                    self.rotation_vectors[angle][0][0],
                    self.rotation_vectors[angle][1][0],
                    self.rotation_vectors[angle][2][0])
            else:
                my_str += 'Angle : %d - rot : None \n' % angle

        for angle in self.translation_vectors:
            if self.translation_vectors[angle] is not None:
                my_str += 'Angle : %d - trans : %f, %f, %f \n' % (
                    angle,
                    self.translation_vectors[angle][0][0],
                    self.translation_vectors[angle][1][0],
                    self.translation_vectors[angle][2][0])
            else:
                my_str += 'Angle : %d - trans : None \n' % angle

        return my_str

    def project_points(self, points, angle):

        projection_point, _ = cv2.projectPoints(numpy.array(points),
                                                self.rotation_vectors[angle],
                                                self.translation_vectors[angle],
                                                self.focal_matrix,
                                                self.distortion_coefficient)
        return projection_point[:, 0, :]

    def project_point(self, point, angle):

        pt = numpy.reshape(point, (1, 3))
        pt = pt.astype(numpy.float32)
        projection_point, _ = cv2.projectPoints(pt,
                                                self.rotation_vectors[angle],
                                                self.translation_vectors[angle],
                                                self.focal_matrix,
                                                self.distortion_coefficient)

        return projection_point[0, 0, 0], projection_point[0, 0, 1]

    def build_object_points(self, chessboard):

        shape = chessboard.shape
        square_size = chessboard.square_size

        object_points = numpy.zeros((shape[0] * shape[1], 3), numpy.float32)

        # Build Chessboard
        grid = numpy.mgrid[0:shape[0], 0:shape[1]].T.reshape(-1, 2)
        object_points[:, :2] = grid * square_size

        # 48 points are stored in an 48x3 array obj
        # choose bottom-left corner as origin, to match australian convention
        object_points = object_points - object_points[40, :]

        return object_points

    def calibrate(self, images, chessboard, verbose=False):

        image_points = list()
        for angle in images:
            print angle
            if angle in chessboard.corners_points:
                corners_2 = chessboard.corners_points[angle].astype(numpy.float32)
                print type(corners_2)

            else:
                corners_2 = None

            if corners_2 is not None:
                image_points.append(corners_2)
            else:
                self.rotation_vectors[angle] = None
                self.translation_vectors[angle] = None

        # Clean possibly None corners
        image_points = [corners for corners in image_points if corners is not None]

        obj_pts = self.build_object_points(chessboard)
        object_points = [obj_pts] * len(image_points)

        # create initial cameraMatrix and distortion coefficient
        camera_matrix = numpy.zeros((3, 3), dtype=numpy.float32)

        distortion_coefficient = numpy.zeros((5, 1), numpy.float32)

        print image_points

        image_points = numpy.array(image_points)

        print image_points

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
