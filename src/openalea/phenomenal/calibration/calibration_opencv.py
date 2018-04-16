# -*- python -*-
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
from __future__ import division, print_function, absolute_import

import json
import cv2
import numpy
#  =============================================================================

__all__ = ["CalibrationCameraOpenCv"]

# ==============================================================================


class CalibrationCameraOpenCv(object):
    def __init__(self):
        self.focal_matrix = numpy.zeros((3, 3))
        self.distortion_coefficient = numpy.zeros((5, 1))

        self.rotation_vectors = dict()
        self.translation_vectors = dict()

    def __str__(self):
        my_str = ''
        my_str += 'Focal Matrix : \n' + str(self.focal_matrix) + '\n\n'
        my_str += 'Distortion Coefficient : \n' + str(
            self.distortion_coefficient) + '\n\n'

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

    def calibrate(self,
                  ref_target_points_2d,
                  ref_target_points_local_3d,
                  ref_target_points_2d_2,
                  ref_target_points_local_3d_2,
                  size_image):

        image_points = list()
        object_points = list()
        for angle in ref_target_points_2d:
            corners = ref_target_points_2d[angle].astype(numpy.float32)
            image_points.append(corners)
            pts_3d = numpy.array(ref_target_points_local_3d)
            pts_3d = pts_3d.astype(numpy.float32)
            object_points.append(pts_3d)

        for angle in ref_target_points_2d_2:
            corners = ref_target_points_2d_2[angle].astype(numpy.float32)
            image_points.append(corners)
            pts_3d = numpy.array(ref_target_points_local_3d_2)
            pts_3d = pts_3d.astype(numpy.float32)
            object_points.append(pts_3d)

        # create initial cameraMatrix and distortion coefficient
        camera_matrix = numpy.zeros((3, 3), dtype=numpy.float32)

        distortion_coefficient = numpy.zeros((5, 1), numpy.float32)

        # Convert list to numpy array
        image_points = numpy.array(image_points)
        object_points = numpy.array(object_points)
        ret, focal_matrix, distortion_coefficient, rvecs, tvecs = \
            cv2.calibrateCamera(object_points,
                                image_points,
                                size_image,
                                camera_matrix,
                                distortion_coefficient,
                                flags=cv2.CALIB_ZERO_TANGENT_DIST +
                                cv2.CALIB_FIX_K1 + cv2.CALIB_FIX_K2 +
                                cv2.CALIB_FIX_K3 + cv2.CALIB_FIX_K4 +
                                cv2.CALIB_FIX_K5 + cv2.CALIB_FIX_K6)

        # cv2.CALIB_FIX_PRINCIPAL_POINT +

        self.focal_matrix = focal_matrix
        self.distortion_coefficient = distortion_coefficient

        i = 0
        for angle in ref_target_points_2d:
            self.rotation_vectors[angle] = rvecs[i]
            self.translation_vectors[angle] = tvecs[i]
            i += 1

    def get_projection(self, angle):
        def project_point(point):
            pt = numpy.reshape(point, (1, 3))
            pt = pt.astype(numpy.float32)

            projection_point, _ = cv2.projectPoints(
                pt,
                self.rotation_vectors[angle],
                self.translation_vectors[angle],
                self.focal_matrix,
                self.distortion_coefficient)

            return projection_point[0, 0, 0], projection_point[0, 0, 1]

        return lambda pt3d: project_point(pt3d)

    def dump(self, file_path):
        save_class = dict()

        fm = self.focal_matrix.reshape((9, )).tolist()
        save_class['focal_matrix'] = fm

        dc = self.distortion_coefficient.reshape((5, )).tolist()
        save_class['distortion_coefficient'] = dc

        rv = dict()
        for angle in self.rotation_vectors:
            rv[angle] = self.rotation_vectors[angle].reshape((3, )).tolist()
        save_class['rotation_vectors'] = rv

        tv = dict()
        for angle in self.translation_vectors:
            tv[angle] = self.translation_vectors[angle].reshape((3, )).tolist()
        save_class['translation_vectors'] = tv

        with open(file_path + '.json', 'w') as output_file:
            json.dump(save_class, output_file)

    @staticmethod
    def load(file_path):
        with open(file_path + '.json', 'r') as input_file:
            save_class = json.load(input_file)

            fm = numpy.array(save_class['focal_matrix']).reshape(
                (3, 3)).astype(numpy.float32)

            dc = numpy.array(save_class['distortion_coefficient']).reshape(
                (5, 1)).astype(numpy.float32)

            rv = dict()
            for angle in save_class['rotation_vectors']:
                rv[float(angle)] = numpy.array(
                    save_class['rotation_vectors'][angle]).reshape(
                        (3, 1)).astype(numpy.float32)

            tv = dict()
            for angle in save_class['translation_vectors']:
                tv[float(angle)] = numpy.array(
                    save_class['translation_vectors'][angle]).reshape(
                        (3, 1)).astype(numpy.float32)

            c = CalibrationCameraOpenCv()
            c.focal_matrix = fm
            c.rotation_vectors = rv
            c.translation_vectors = tv
            c.distortion_coefficient = dc

        return c
