# -*- python -*-
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
""" This module contains a calibration model for phenoarch experiment
where a target is rotating instead of a plant in a picture cabin.
"""
# ==============================================================================
from math import radians, cos, sin, pi
import json
import numpy
import scipy.optimize


from alinea.phenomenal.frame import (
    Frame,
    x_axis,
    y_axis,
    z_axis)

from alinea.phenomenal.transformations import (
    concatenate_matrices,
    rotation_matrix)
# ==============================================================================


class CalibrationCamera(object):
    def __init__(self):
        # Camera Parameters
        self._cam_width_image = None
        self._cam_height_image = None
        self._cam_focal_length_x = None
        self._cam_focal_length_y = None
        self._cam_pos_x = None
        self._cam_pos_y = None
        self._cam_pos_z = None
        self._cam_rot_x = None
        self._cam_rot_y = None
        self._cam_rot_z = None
        self._cam_origin_axis = None

    @staticmethod
    def pixel_coordinates(point_3d,
                          width_image, height_image,
                          focal_length_x, focal_length_y):
        """ Compute image coordinates of a 3d point

        Args:
         - point (float, float, float): a point in space
                    expressed in camera frame coordinates

        return:
         - (int, int): coordinate of point in image in pix
        """
        # if point[2] < 1:
        #     raise UserWarning("point too close to the camera")

        u = point_3d[0] / point_3d[2] * focal_length_x + width_image / 2.0
        v = point_3d[1] / point_3d[2] * focal_length_y + height_image / 2.0

        return u, v

    @staticmethod
    def target_frame(pos_x, pos_y, pos_z,
                     rot_x, rot_y, rot_z,
                     alpha):

        origin = [
            pos_x * cos(alpha) - pos_y * sin(alpha),
            pos_x * sin(alpha) + pos_y * cos(alpha),
            pos_z]

        mat_rot_x = rotation_matrix(rot_x, x_axis)
        mat_rot_y = rotation_matrix(rot_y, y_axis)
        mat_rot_z = rotation_matrix(alpha + rot_z, z_axis)

        rot = concatenate_matrices(mat_rot_z, mat_rot_x, mat_rot_y)

        return Frame(rot[:3, :3].T, origin)

    @staticmethod
    def camera_frame(pos_x, pos_y, pos_z,
                     rot_x, rot_y, rot_z,
                     origin_axis):

        origin = (pos_x, pos_y, pos_z)

        mat_rot_x = rotation_matrix(rot_x, x_axis)
        mat_rot_y = rotation_matrix(rot_y, y_axis)
        mat_rot_z = rotation_matrix(rot_z, z_axis)

        rot = concatenate_matrices(origin_axis,
                                   mat_rot_x, mat_rot_y, mat_rot_z)

        return Frame(rot[:3, :3].T, origin)

    @staticmethod
    def get_ref_points_global_3d(alpha, ref_points_local_3d,
                                 target_pos_x, target_pos_y, target_pos_z,
                                 target_rot_x, target_rot_y, target_rot_z):

        fr_target = CalibrationCamera.target_frame(
            target_pos_x, target_pos_y, target_pos_z,
            target_rot_x, target_rot_y, target_rot_z,
            radians(alpha))

        return map(lambda pt: fr_target.global_point(pt), ref_points_local_3d)

    def get_projection(self, alpha):

        fr_cam = self.camera_frame(
            self._cam_pos_x, self._cam_pos_y, self._cam_pos_z,
            self._cam_rot_x, self._cam_rot_y, self._cam_rot_z,
            self._cam_origin_axis,)

        angle = radians(alpha)

        def projection(pt):
            # -pt[0] = x <=> For inverse X axis orientation
            origin = [-pt[0] * cos(angle) - pt[1] * sin(angle),
                      -pt[0] * sin(angle) + pt[1] * cos(angle),
                      pt[2]]

            return self.pixel_coordinates(fr_cam.local_point(origin),
                                          self._cam_width_image,
                                          self._cam_height_image,
                                          self._cam_focal_length_x,
                                          self._cam_focal_length_y)

        return projection

    @staticmethod
    def load(file_path):
        with open(file_path + '.json', 'r') as input_file:
            save_class = json.load(input_file)

            c = CalibrationCamera()

            c._cam_width_image = save_class['cam_width_image']
            c._cam_height_image = save_class['cam_height_image']
            c._cam_focal_length_x = save_class['cam_focal_length_x']
            c._cam_focal_length_y = save_class['cam_focal_length_y']
            c._cam_pos_x = save_class['cam_pos_x']
            c._cam_pos_y = save_class['cam_pos_y']
            c._cam_pos_z = save_class['cam_pos_z']
            c._cam_rot_x = save_class['cam_rot_x']
            c._cam_rot_y = save_class['cam_rot_y']
            c._cam_rot_z = save_class['cam_rot_z']
            c._cam_origin_axis = numpy.array(
                save_class['cam_origin_axis']).reshape((4, 4)).astype(
                numpy.float32)

        return c

    def dump(self, file_path):
        save_class = dict()

        save_class['cam_width_image'] = self._cam_width_image
        save_class['cam_height_image'] = self._cam_height_image
        save_class['cam_focal_length_x'] = self._cam_focal_length_x
        save_class['cam_focal_length_y'] = self._cam_focal_length_y
        save_class['cam_pos_x'] = self._cam_pos_x
        save_class['cam_pos_y'] = self._cam_pos_y
        save_class['cam_pos_z'] = self._cam_pos_z
        save_class['cam_rot_x'] = self._cam_rot_x
        save_class['cam_rot_y'] = self._cam_rot_y
        save_class['cam_rot_z'] = self._cam_rot_z
        save_class['cam_origin_axis'] = self._cam_origin_axis.reshape(
            (16, )).tolist()

        with open(file_path + '.json', 'w') as output_file:
            json.dump(save_class, output_file,
                      sort_keys=True,
                      indent=4,
                      separators=(',', ': '))


class CalibrationCameraTopWith1Target(CalibrationCamera):

    def __init__(self):
        CalibrationCamera.__init__(self)
        self._verbose = False
        
        self._ref_target_points_local_3d = None
        self._ref_target_points_2d = None
        self._ref_target_points_global_3d = None

        self._ref_number = None

        self._cam_pos_x = 0.0
        self._cam_pos_y = 0.0
        self._cam_origin_axis = numpy.array([[0., -1., 0., 0.],
                                             [1., 0., 0., 0.],
                                             [0., 0., 1., 0.],
                                             [0., 0., 0., 1.]])

    def fit_function(self, x0):
        err = 0

        cam_focal_length_x, cam_focal_length_y, \
            cam_pos_z, \
            cam_rot_x, cam_rot_z, cam_rot_z = x0

        fr_cam = self.camera_frame(
            self._cam_pos_x, self._cam_pos_y, cam_pos_z,
            cam_rot_x, cam_rot_z, cam_rot_z,
            self._cam_origin_axis)

        for alpha, ref_pts in self._ref_target_points_2d.items():
            target_pts = self._ref_target_points_global_3d[alpha]

            pts = map(lambda pt: self.pixel_coordinates(
                fr_cam.local_point(pt),
                self._cam_width_image,
                self._cam_height_image,
                cam_focal_length_x,
                cam_focal_length_y), target_pts)

            err += numpy.linalg.norm(numpy.array(pts) - ref_pts, axis=1).sum()

        if self._verbose:
            print err

        return err

    def find_parameters(self, number_of_repetition):
        best_parameters = None
        min_err = float('inf')
        for i in range(number_of_repetition + 1):

            cam_focal_length_x = numpy.random.uniform(0.0, 10000.0)
            cam_focal_length_y = numpy.random.uniform(0.0, 10000.0)
            cam_pos_z = numpy.random.uniform(0.0, 10000.0)
            cam_rot_x = 0.0
            cam_rot_y = 0.0
            cam_rot_z = 0.0

            parameters = [cam_focal_length_x, cam_focal_length_y,
                          cam_pos_z,
                          cam_rot_x, cam_rot_y, cam_rot_z]

            # Optimization
            parameters = scipy.optimize.minimize(
                self.fit_function, parameters, method='BFGS').x

            # Compute error compare with min_err
            err = self.fit_function(parameters)
            if err < min_err:
                min_err = err
                best_parameters = parameters

            if self._verbose:
                print 'Result : ', parameters
                print 'Err : ', err / self._ref_number

        return best_parameters

    def calibrate(self,
                  ref_target_points_2d,
                  ref_target_points_global_3d,
                  size_image,
                  number_of_repetition=1,
                  verbose=False):

        self._verbose = verbose

        self._ref_target_points_2d = ref_target_points_2d.copy()
        self._ref_number = len(ref_target_points_2d)

        self._ref_target_points_global_3d = ref_target_points_global_3d
        self._cam_width_image = size_image[0]
        self._cam_height_image = size_image[1]

        parameters = self.find_parameters(number_of_repetition)

        for i in [3, 4, 5]:
            parameters[i] %= pi * 2.0

        self._cam_focal_length_x = parameters[0]
        self._cam_focal_length_y = parameters[1]
        self._cam_pos_z = parameters[2]
        self._cam_rot_x = parameters[3]
        self._cam_rot_y = parameters[4]
        self._cam_rot_z = parameters[5]

        if self._verbose:
            err = self.fit_function(parameters)
            print 'Result : ', parameters
            print 'Err : ', err, ' -- ', err / self._ref_number

        self._verbose = False


class CalibrationCameraSideWith1Target(CalibrationCamera):
    def __init__(self):
        CalibrationCamera.__init__(self)
        self._verbose = False
        self._ref_target_points_local_3d = None
        self._ref_number = None
        self._ref_target_points_2d = None

        self._cam_pos_y = 0.0
        self._cam_pos_z = 0.0
        self._cam_origin_axis = numpy.array([[0., 0., 1., 0.],
                                             [1., 0., 0., 0.],
                                             [0., 1., 0., 0.],
                                             [0., 0., 0., 1.]])

        self._target_pos_x = None
        self._target_pos_y = None
        self._target_pos_z = None
        self._target_rot_x = None
        self._target_rot_y = None
        self._target_rot_z = None

    def fit_function(self, x0):
        err = 0

        cam_focal_length_x, cam_focal_length_y, \
            cam_pos_x, \
            cam_rot_x, cam_rot_y, cam_rot_z, \
            target_pos_x, target_pos_y, target_pos_z, \
            target_rot_x, target_rot_y, target_rot_z = x0

        fr_cam = self.camera_frame(
            cam_pos_x, self._cam_pos_y, self._cam_pos_z,
            cam_rot_x, cam_rot_y, cam_rot_z,
            self._cam_origin_axis,)

        for alpha, ref_pts in self._ref_target_points_2d.items():
            fr_target = self.target_frame(
                target_pos_x, target_pos_y, target_pos_z,
                target_rot_x, target_rot_y, target_rot_z,
                radians(alpha))

            target_pts = map(lambda pt: fr_target.global_point(pt),
                             self._ref_target_points_local_3d)

            pts = map(lambda pt: self.pixel_coordinates(
                fr_cam.local_point(pt),
                self._cam_width_image,
                self._cam_height_image,
                cam_focal_length_x,
                cam_focal_length_y), target_pts)

            err += numpy.linalg.norm(numpy.array(pts) - ref_pts, axis=1).sum()

        if self._verbose:
            print err

        return err

    def find_parameters(self, number_of_repetition):

        best_parameters = None
        min_err = float('inf')
        for i in range(number_of_repetition + 1):

            cam_focal_length_x = numpy.random.uniform(1000.0, 10000.0)
            cam_focal_length_y = numpy.random.uniform(1000.0, 10000.0)
            cam_pos_x = numpy.random.uniform(1000.0, 10000.0)
            cam_rot_x = 0.0
            cam_rot_y = 0.0
            cam_rot_z = 0.0

            target_pos_x = numpy.random.uniform(-1000.0, 1000.0)
            target_pos_y = numpy.random.uniform(-1000.0, 1000.0)
            target_pos_z = numpy.random.uniform(0, 1000.0)
            target_rot_x = 0.0
            target_rot_y = 0.0
            target_rot_z = 0.0

            parameters = [cam_focal_length_x, cam_focal_length_y,
                          cam_pos_x,
                          cam_rot_x, cam_rot_y, cam_rot_z,
                          target_pos_x, target_pos_y, target_pos_z,
                          target_rot_x, target_rot_y, target_rot_z]

            parameters = scipy.optimize.minimize(
                self.fit_function, parameters, method='BFGS').x

            err = self.fit_function(parameters)
            if err < min_err:
                min_err = err
                best_parameters = parameters

            if self._verbose:
                err = self.fit_function(parameters)
                print 'Result : ', parameters
                print 'Err : ', err / self._ref_number

        return best_parameters

    def calibrate(self,
                  ref_target_points_2d,
                  ref_target_points_local_3d,
                  size_image,
                  number_of_repetition=1,
                  verbose=False):
        """ Find physical parameters associated with a camera
        (i.e. distances and angles), using pictures of a rotating
        target.

        args:
         - 'target_ref' (target): reference target
         - 'target_corners' dict of (angle, list of pts): for
                        a picture taken with a given angle, list
                        the coordinates of all intersections on
                        the target in the picture
        """
        self._verbose = verbose

        self._ref_target_points_2d = ref_target_points_2d.copy()
        self._ref_target_points_local_3d = ref_target_points_local_3d
        self._ref_number = len(ref_target_points_2d)

        self._cam_width_image = size_image[0]
        self._cam_height_image = size_image[1]

        parameters = self.find_parameters(number_of_repetition)

        for i in [3, 4, 5, 9, 10, 11]:
            parameters[i] %= pi * 2.0

        # Camera Parameters
        self._cam_focal_length_x = parameters[0]
        self._cam_focal_length_y = parameters[1]
        self._cam_pos_x = parameters[2]
        self._cam_rot_x = parameters[3]
        self._cam_rot_y = parameters[4]
        self._cam_rot_z = parameters[5]

        # Target Parameters
        self._target_pos_x = parameters[6]
        self._target_pos_y = parameters[7]
        self._target_pos_z = parameters[8]
        self._target_rot_x = parameters[9]
        self._target_rot_y = parameters[10]
        self._target_rot_z = parameters[11]

        if self._verbose:
            err = self.fit_function(parameters)
            print 'Result : ', parameters
            print 'Err : ', err, ' -- ', err / self._ref_number

        self._verbose = False

    @staticmethod
    def load(file_path):
        with open(file_path + '.json', 'r') as input_file:
            save_class = json.load(input_file)

            c = CalibrationCameraSideWith1Target()

            c._cam_width_image = save_class['cam_width_image']
            c._cam_height_image = save_class['cam_height_image']
            c._cam_focal_length_x = save_class['cam_focal_length_x']
            c._cam_focal_length_y = save_class['cam_focal_length_y']
            c._cam_pos_x = save_class['cam_pos_x']
            c._cam_pos_y = save_class['cam_pos_y']
            c._cam_pos_z = save_class['cam_pos_z']
            c._cam_rot_x = save_class['cam_rot_x']
            c._cam_rot_y = save_class['cam_rot_y']
            c._cam_rot_z = save_class['cam_rot_z']
            c._cam_origin_axis = numpy.array(
                save_class['cam_origin_axis']).reshape((4, 4)).astype(
                numpy.float32)

            c._target_pos_x = save_class['target_pos_x']
            c._target_pos_y = save_class['target_pos_y']
            c._target_pos_z = save_class['target_pos_z']
            c._target_rot_x = save_class['target_rot_x']
            c._target_rot_y = save_class['target_rot_y']
            c._target_rot_z = save_class['target_rot_z']

        return c

    def dump(self, file_path):
        save_class = dict()

        save_class['cam_width_image'] = self._cam_width_image
        save_class['cam_height_image'] = self._cam_height_image
        save_class['cam_focal_length_x'] = self._cam_focal_length_x
        save_class['cam_focal_length_y'] = self._cam_focal_length_y
        save_class['cam_pos_x'] = self._cam_pos_x
        save_class['cam_pos_y'] = self._cam_pos_y
        save_class['cam_pos_z'] = self._cam_pos_z
        save_class['cam_rot_x'] = self._cam_rot_x
        save_class['cam_rot_y'] = self._cam_rot_y
        save_class['cam_rot_z'] = self._cam_rot_z
        save_class['cam_origin_axis'] = self._cam_origin_axis.reshape(
            (16, )).tolist()

        save_class['target_pos_x'] = self._target_pos_x
        save_class['target_pos_y'] = self._target_pos_y
        save_class['target_pos_z'] = self._target_pos_z
        save_class['target_rot_x'] = self._target_rot_x
        save_class['target_rot_y'] = self._target_rot_y
        save_class['target_rot_z'] = self._target_rot_z

        with open(file_path + '.json', 'w') as output_file:
            json.dump(save_class, output_file,
                      sort_keys=True,
                      indent=4,
                      separators=(',', ': '))

    def get_ref_points_global_3d(self, alpha, ref_points_local_3d):

        fr_target = CalibrationCamera.target_frame(
            self._target_pos_x, self._target_pos_y, self._target_pos_z,
            self._target_rot_x, self._target_rot_y, self._target_rot_z,
            radians(alpha))

        return map(lambda pt: fr_target.global_point(pt), ref_points_local_3d)


class CalibrationCameraSideWith2Target(CalibrationCamera):
    def __init__(self):
        CalibrationCamera.__init__(self)
        self._verbose = False
        self._ref_target_1_points_local_3d = None
        self._ref_target_2_points_local_3d = None
        self._ref_number = None
        self._ref_target_1_points_2d = None
        self._ref_target_2_points_2d = None

        self._cam_pos_y = 0.0
        self._cam_pos_z = 0.0
        self._cam_origin_axis = numpy.array([[0., 0., 1., 0.],
                                             [1., 0., 0., 0.],
                                             [0., 1., 0., 0.],
                                             [0., 0., 0., 1.]])

        self._target_1_pos_x = None
        self._target_1_pos_y = None
        self._target_1_pos_z = None
        self._target_1_rot_x = None
        self._target_1_rot_y = None
        self._target_1_rot_z = None

        self._target_2_pos_x = None
        self._target_2_pos_y = None
        self._target_2_pos_z = None
        self._target_2_rot_x = None
        self._target_2_rot_y = None
        self._target_2_rot_z = None

    def fit_function(self, x0):
        err = 0

        cam_focal_length_x, cam_focal_length_y, \
            cam_pos_x, \
            cam_rot_x, cam_rot_y, cam_rot_z, \
            target_1_pos_x, target_1_pos_y, target_1_pos_z,\
            target_1_rot_x, target_1_rot_y, target_1_rot_z,\
            target_2_pos_x, target_2_pos_y, target_2_pos_z,\
            target_2_rot_x, target_2_rot_y, target_2_rot_z = x0

        fr_cam = self.camera_frame(
            cam_pos_x, self._cam_pos_y, self._cam_pos_z,
            cam_rot_x, cam_rot_y, cam_rot_z,
            self._cam_origin_axis)

        for alpha, ref_pts in self._ref_target_1_points_2d.items():

            fr_target = self.target_frame(target_1_pos_x,
                                          target_1_pos_y,
                                          target_1_pos_z,
                                          target_1_rot_x,
                                          target_1_rot_y,
                                          target_1_rot_z,
                                          radians(alpha))

            target_pts = map(lambda pt: fr_target.global_point(pt),
                             self._ref_target_1_points_local_3d)

            pts = map(lambda pt: self.pixel_coordinates(
                fr_cam.local_point(pt),
                self._cam_width_image,
                self._cam_height_image,
                cam_focal_length_x,
                cam_focal_length_y), target_pts)

            err += numpy.linalg.norm(numpy.array(pts) - ref_pts, axis=1).sum()

        for alpha, ref_pts in self._ref_target_2_points_2d.items():

            fr_target = self.target_frame(target_2_pos_x,
                                          target_2_pos_y,
                                          target_2_pos_z,
                                          target_2_rot_x,
                                          target_2_rot_y,
                                          target_2_rot_z,
                                          radians(alpha))

            target_pts = map(lambda pt: fr_target.global_point(pt),
                             self._ref_target_2_points_local_3d)

            pts = map(lambda pt: self.pixel_coordinates(
                fr_cam.local_point(pt),
                self._cam_width_image,
                self._cam_height_image,
                cam_focal_length_x,
                cam_focal_length_y), target_pts)

            err += numpy.linalg.norm(numpy.array(pts) - ref_pts, axis=1).sum()

        if self._verbose:
            print err

        return err

    def find_parameters(self, number_of_repetition):

        best_parameters = None
        min_err = float('inf')
        for i in range(number_of_repetition + 1):

            cam_focal_length_x = numpy.random.uniform(1000.0, 10000.0)
            cam_focal_length_y = numpy.random.uniform(1000.0, 10000.0)
            cam_pos_x = numpy.random.uniform(1000.0, 10000.0)
            cam_rot_x = 0.0
            cam_rot_y = 0.0
            cam_rot_z = 0.0

            target_1_pos_x = numpy.random.uniform(-1000.0, 1000.0)
            target_1_pos_y = numpy.random.uniform(-1000.0, 1000.0)
            target_1_pos_z = numpy.random.uniform(0, 1000.0)
            target_1_rot_x = 0.0
            target_1_rot_y = 0.0
            target_1_rot_z = 0.0

            target_2_pos_x = -target_1_pos_x
            target_2_pos_y = -target_1_pos_y
            target_2_pos_z = numpy.random.uniform(0, 1000.0)
            target_2_rot_x = 0.0
            target_2_rot_y = 0.0
            target_2_rot_z = 0.0

            parameters = [cam_focal_length_x, cam_focal_length_y,
                          cam_pos_x,
                          cam_rot_x, cam_rot_y, cam_rot_z,
                          target_1_pos_x, target_1_pos_y, target_1_pos_z,
                          target_1_rot_x, target_1_rot_y, target_1_rot_z,
                          target_2_pos_x, target_2_pos_y, target_2_pos_z,
                          target_2_rot_x, target_2_rot_y, target_2_rot_z]

            parameters = scipy.optimize.minimize(
                self.fit_function, parameters, method='BFGS').x

            err = self.fit_function(parameters)
            if err < min_err:
                min_err = err
                best_parameters = parameters

            if self._verbose:
                err = self.fit_function(parameters)
                print 'Result : ', parameters
                print 'Err : ', err / self._ref_number

        return best_parameters

    def calibrate(self,
                  ref_target_1_points_2d,
                  ref_target_1_points_local_3d,
                  ref_target_2_points_2d,
                  ref_target_2_points_local_3d,
                  size_image,
                  number_of_repetition=3,
                  verbose=False):
        """ Find physical parameters associated with a camera
        (i.e. distances and angles), using pictures of a rotating
        target.

        args:
         - 'target_ref' (target): reference target
         - 'target_corners' dict of (angle, list of pts): for
                        a picture taken with a given angle, list
                        the coordinates of all intersections on
                        the target in the picture
        """
        self._verbose = verbose

        self._ref_target_1_points_local_3d = ref_target_1_points_local_3d
        self._ref_target_2_points_local_3d = ref_target_2_points_local_3d

        self._ref_number = (len(ref_target_1_points_2d) +
                            len(ref_target_2_points_2d))

        self._ref_target_1_points_2d = ref_target_1_points_2d.copy()
        self._ref_target_2_points_2d = ref_target_2_points_2d.copy()

        self._cam_width_image = size_image[0]
        self._cam_height_image = size_image[1]

        parameters = self.find_parameters(number_of_repetition)

        for i in [3, 4, 5, 9, 10, 11, 15, 16, 17]:
            parameters[i] %= pi * 2.0

        # Camera Parameters
        self._cam_focal_length_x = parameters[0]
        self._cam_focal_length_y = parameters[1]
        self._cam_pos_x = parameters[2]
        self._cam_rot_x = parameters[3]
        self._cam_rot_y = parameters[4]
        self._cam_rot_z = parameters[5]

        # Target 1 Parameters
        self._target_1_pos_x = parameters[6]
        self._target_1_pos_y = parameters[7]
        self._target_1_pos_z = parameters[8]
        self._target_1_rot_x = parameters[9]
        self._target_1_rot_y = parameters[10]
        self._target_1_rot_z = parameters[11]

        # Target 2 Parameters
        self._target_2_pos_x = parameters[12]
        self._target_2_pos_y = parameters[13]
        self._target_2_pos_z = parameters[14]
        self._target_2_rot_x = parameters[15]
        self._target_2_rot_y = parameters[16]
        self._target_2_rot_z = parameters[17]

        if self._verbose:
            err = self.fit_function(parameters)
            print 'Result : ', parameters
            print 'Err : ', err, ' -- ', err / self._ref_number

        self._verbose = False

    def dump(self, file_path):
        save_class = dict()

        save_class['cam_width_image'] = self._cam_width_image
        save_class['cam_height_image'] = self._cam_height_image
        save_class['cam_focal_length_x'] = self._cam_focal_length_x
        save_class['cam_focal_length_y'] = self._cam_focal_length_y
        save_class['cam_pos_x'] = self._cam_pos_x
        save_class['cam_pos_y'] = self._cam_pos_y
        save_class['cam_pos_z'] = self._cam_pos_z
        save_class['cam_rot_x'] = self._cam_rot_x
        save_class['cam_rot_y'] = self._cam_rot_y
        save_class['cam_rot_z'] = self._cam_rot_z
        save_class['cam_origin_axis'] = self._cam_origin_axis.reshape(
            (16, )).tolist()

        save_class['target_1_pos_x'] = self._target_1_pos_x
        save_class['target_1_pos_y'] = self._target_1_pos_y
        save_class['target_1_pos_z'] = self._target_1_pos_z
        save_class['target_1_rot_x'] = self._target_1_rot_x
        save_class['target_1_rot_y'] = self._target_1_rot_y
        save_class['target_1_rot_z'] = self._target_1_rot_z

        save_class['target_2_pos_x'] = self._target_2_pos_x
        save_class['target_2_pos_y'] = self._target_2_pos_y
        save_class['target_2_pos_z'] = self._target_2_pos_z
        save_class['target_2_rot_x'] = self._target_2_rot_x
        save_class['target_2_rot_y'] = self._target_2_rot_y
        save_class['target_2_rot_z'] = self._target_2_rot_z

        with open(file_path + '.json', 'w') as output_file:
            json.dump(save_class, output_file,
                      sort_keys=True,
                      indent=4,
                      separators=(',', ': '))

    @staticmethod
    def load(file_path):
        with open(file_path + '.json', 'r') as input_file:
            save_class = json.load(input_file)

            c = CalibrationCameraSideWith2Target()

            c._cam_width_image = save_class['cam_width_image']
            c._cam_height_image = save_class['cam_height_image']
            c._cam_focal_length_x = save_class['cam_focal_length_x']
            c._cam_focal_length_y = save_class['cam_focal_length_y']
            c._cam_pos_x = save_class['cam_pos_x']
            c._cam_pos_y = save_class['cam_pos_y']
            c._cam_pos_z = save_class['cam_pos_z']
            c._cam_rot_x = save_class['cam_rot_x']
            c._cam_rot_y = save_class['cam_rot_y']
            c._cam_rot_z = save_class['cam_rot_z']
            c._cam_origin_axis = numpy.array(
                save_class['cam_origin_axis']).reshape((4, 4)).astype(
                numpy.float32)

            c._target_1_pos_x = save_class['target_1_pos_x']
            c._target_1_pos_y = save_class['target_1_pos_y']
            c._target_1_pos_z = save_class['target_1_pos_z']
            c._target_1_rot_x = save_class['target_1_rot_x']
            c._target_1_rot_y = save_class['target_1_rot_y']
            c._target_1_rot_z = save_class['target_1_rot_z']

            c._target_2_pos_x = save_class['target_2_pos_x']
            c._target_2_pos_y = save_class['target_2_pos_y']
            c._target_2_pos_z = save_class['target_2_pos_z']
            c._target_2_rot_x = save_class['target_2_rot_x']
            c._target_2_rot_y = save_class['target_2_rot_y']
            c._target_2_rot_z = save_class['target_2_rot_z']


        return c

