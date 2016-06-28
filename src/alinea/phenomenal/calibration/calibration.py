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
import json
import math
import numpy
import scipy.optimize

from alinea.phenomenal.calibration.frame import (
    Frame, x_axis, y_axis, z_axis)

from alinea.phenomenal.calibration.transformations import (
    concatenate_matrices, rotation_matrix)
# ==============================================================================

__all__ = ["CalibrationCamera",
           "CalibrationCameraTop",
           "CalibrationCameraSideWith1Target",
           "CalibrationCameraSideWith2Target"]

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
        self._angle_factor = None
        self._cam_origin_axis = None

    def __str__(self):
        out = ''
        out += 'Camera Parameters : \n'
        out += '\tFocal length X : ' + str(self._cam_focal_length_x) + '\n'
        out += '\tFocal length Y : ' + str(self._cam_focal_length_y) + '\n'
        out += '\tOptical Center X : ' + str(self._cam_width_image / 2.0) + '\n'
        out += '\tOptical Center Y : ' + str(self._cam_height_image / 2.0)
        out += '\n\n'

        out += '\tPosition X : ' + str(self._cam_pos_x) + '\n'
        out += '\tPosition Y : ' + str(self._cam_pos_y) + '\n'
        out += '\tPosition Z : ' + str(self._cam_pos_z) + '\n\n'

        out += '\tRotation X : ' + str(self._cam_rot_x) + '\n'
        out += '\tRotation Y : ' + str(self._cam_rot_y) + '\n'
        out += '\tRotation Z : ' + str(self._cam_rot_z) + '\n'

        out += '\t Angle Factor : ' + str(self._angle_factor) + '\n'

        out += '\tOrigin rotation position : \n'
        out += str(self._cam_origin_axis) + '\n\n'

        return out

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
    def pixel_coordinates_2(point_3d, cx, cy, fx, fy):
        """ Compute image coordinates of a 3d point

        Args:
         - point (float, float, float): a point in space
                    expressed in camera frame coordinates

        return:
         - (int, int): coordinate of point in image in pix
        """
        # if point[2] < 1:
        #     raise UserWarning("point too close to the camera")

        u = point_3d[0] / point_3d[2] * fx + cx
        v = point_3d[1] / point_3d[2] * fy + cy

        return u, v

    @staticmethod
    def target_frame(pos_x, pos_y, pos_z,
                     rot_x, rot_y, rot_z,
                     alpha):

        origin = [
            pos_x * math.cos(alpha) - pos_y * math.sin(alpha),
            pos_x * math.sin(alpha) + pos_y * math.cos(alpha),
            pos_z]

        # origin_axis = numpy.array([[1., 0., 0., 0.],
        #                            [0., -1., 0., 0.],
        #                            [0., 0., 1., 0.],
        #                            [0., 0., 0., 1.]])

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

    def get_projection(self, alpha):

        fr_cam = self.camera_frame(
            self._cam_pos_x, self._cam_pos_y, self._cam_pos_z,
            self._cam_rot_x, self._cam_rot_y, self._cam_rot_z,
            self._cam_origin_axis)

        angle = math.radians(alpha * self._angle_factor)

        def projection(pt):
            # -pt[0] = x <=> For inverse X axis orientation
            origin = [-pt[0] * math.cos(angle) - pt[1] * math.sin(angle),
                      -pt[0] * math.sin(angle) + pt[1] * math.cos(angle),
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
            c._angle_factor = save_class['angle_factor']
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
        save_class['angle_factor'] = self._angle_factor
        save_class['cam_origin_axis'] = self._cam_origin_axis.reshape(
            (16, )).tolist()

        with open(file_path + '.json', 'w') as output_file:
            json.dump(save_class, output_file,
                      sort_keys=True,
                      indent=4,
                      separators=(',', ': '))


class CalibrationCameraTopNew(CalibrationCamera):

    def __init__(self):
        CalibrationCamera.__init__(self)
        self._verbose = False
        
        self._ref_target_points_local_3d = None
        self._ref_target_points_2d = None
        self._ref_target_points_3d = None

        self._ref_number = None

        self._cam_origin_axis = numpy.array([[0., -1., 0., 0.],
                                             [1., 0., 0., 0.],
                                             [0., 0., 1., 0.],
                                             [0., 0., 0., 1.]])

        self._cx = None
        self._cy = None
        self._fx = None
        self._fy = None

    def fit_function(self, x0):
        err = 0

        cam_focal_length_x, cam_focal_length_y, \
        cam_pos_x, cam_pos_y, cam_pos_z, \
        cam_rot_x, cam_rot_y, cam_rot_z = x0[0:8]

        res = abs(cam_focal_length_x - cam_focal_length_y)
        if res > 600:
            err += res - 600

        if cam_focal_length_x <= 3000:
            err += 3000 - cam_focal_length_x

        if abs(cam_pos_x) > 100:
            err += abs(cam_pos_x) - 100

        if abs(cam_pos_y) > 100:
            err += abs(cam_pos_y) - 100

        index_init = 8
        for i in xrange(self._ref_number):

            pt = x0[index_init + i * 3:index_init + (i + 1) * 3]

            fr_cam = self.camera_frame(
                cam_pos_x, cam_pos_y, cam_pos_z,
                cam_rot_x, cam_rot_y, cam_rot_z,
                self._cam_origin_axis)

            pts = self.pixel_coordinates(fr_cam.local_point(pt),
                                         self._cam_width_image,
                                         self._cam_height_image,
                                         cam_focal_length_x,
                                         cam_focal_length_y)

            err += numpy.linalg.norm(
                numpy.array(pts) - self._points_top[i]).sum()

            pts = self._side_projection(pt)
            err += numpy.linalg.norm(
                numpy.array(pts) - self._points_side[i]).sum()

        if self._verbose:
            print err

        return err

    def find_parameters(self, number_of_repetition):
        best_parameters = None
        min_err = float('inf')
        for i in range(number_of_repetition + 1):

            cam_focal_length_x = numpy.random.uniform(3000.0, 5000.0)
            cam_focal_length_y = numpy.random.uniform(3000.0, 5000.0)
            cam_pos_x = numpy.random.uniform(-100.0, 100.0)
            cam_pos_y = numpy.random.uniform(-100.0, 100.0)
            cam_pos_z = numpy.random.uniform(1000.0, 3000.0)
            cam_rot_x = 0.0
            cam_rot_y = 0.0
            cam_rot_z = 0.0

            parameters = [cam_focal_length_x, cam_focal_length_y,
                          cam_pos_x, cam_pos_y, cam_pos_z,
                          cam_rot_x, cam_rot_y, cam_rot_z]

            for i in xrange(self._ref_number):
                parameters.append(numpy.random.uniform(-1000.0, 1000.0))
                parameters.append(numpy.random.uniform(-1000.0, 1000.0))
                parameters.append(-1000)

            # Optimization
            parameters = scipy.optimize.minimize(
                self.fit_function, parameters, method='BFGS').x

            # bounds = [(0.0, 10000.0),
            #           (0.0, 10000.0),
            #           (-500.0, 500.0),
            #           (-500.0, 500.0),
            #           (1000.0, 5000.0),
            #           (- 2 * numpy.pi, 2 * numpy.pi),
            #           (- 2 * numpy.pi, 2 * numpy.pi),
            #           (- 2 * numpy.pi, 2 * numpy.pi)]
            #
            # for i in xrange(self._ref_number):
            #     bounds.append((-2000, 2000))
            #     bounds.append((-2000, 2000))
            #     bounds.append((-2000, 0))

            # parameters = scipy.optimize.differential_evolution(
            #     self.fit_function, bounds)[0]
            #
            # print parameters

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
                  points_side,
                  points_top,
                  side_projection,
                  size_image,
                  angle_factor,
                  number_of_repetition=3,
                  verbose=False):

        self._side_projection = side_projection

        self._verbose = verbose
        self._angle_factor = angle_factor

        self._points_side = points_side
        self._points_top = points_top
        self._ref_number = len(points_side)

        self._cam_width_image = size_image[0]
        self._cam_height_image = size_image[1]

        parameters = self.find_parameters(number_of_repetition)

        for i in [5, 6, 7]:
            parameters[i] %= math.pi * 2.0

        self._cam_focal_length_x = parameters[0]
        self._cam_focal_length_y = parameters[1]
        self._cam_pos_x = parameters[2]
        self._cam_pos_y = parameters[3]
        self._cam_pos_z = parameters[4]
        self._cam_rot_x = parameters[5]
        self._cam_rot_y = parameters[6]
        self._cam_rot_z = parameters[7]


        # self._p1 = parameters[6:9]
        # self._p2 = parameters[9:12]
        # self._p3 = parameters[12:15]
        # self._p4 = parameters[15:18]
        # self._p5 = parameters[18:21]
        # self._p6 = parameters[21:]

        err = self.fit_function(parameters)
        if self._verbose:
            print 'Result : ', parameters
            print 'Err : ', err, ' -- ', err / self._ref_number

        self._verbose = False

        return err / self._ref_number


class CalibrationCameraTop(CalibrationCamera):
    def __init__(self):
        CalibrationCamera.__init__(self)
        self._verbose = False

        self._ref_target_points_local_3d = None
        self._ref_target_points_2d = None
        self._ref_target_points_3d = None

        self._ref_number = None

        self._cam_origin_axis = numpy.array([[0., -1., 0., 0.],
                                             [1., 0., 0., 0.],
                                             [0., 0., 1., 0.],
                                             [0., 0., 0., 1.]])

    def fit_function(self, x0):
        err = 0

        cam_focal_length_x, cam_focal_length_y, \
        cam_pos_x, cam_pos_y, cam_pos_z, \
        cam_rot_x, cam_rot_y, cam_rot_z = x0

        fr_cam = self.camera_frame(
            cam_pos_x, cam_pos_y, cam_pos_z,
            cam_rot_x, cam_rot_y, cam_rot_z,
            self._cam_origin_axis)

        for i in xrange(len(self._ref_target_points_2d)):
            pts = map(lambda pt: self.pixel_coordinates(
                fr_cam.local_point(pt),
                self._cam_width_image,
                self._cam_height_image,
                cam_focal_length_x,
                cam_focal_length_y), self._ref_target_points_3d[i])

            err += numpy.linalg.norm(
                numpy.array(pts) - self._ref_target_points_2d[i], axis=1).sum()

        if self._verbose:
            print err

        return err

    def find_parameters(self, number_of_repetition):
        best_parameters = None
        min_err = float('inf')
        for i in range(number_of_repetition + 1):

            cam_focal_length_x = numpy.random.uniform(0.0, 10000.0)
            cam_focal_length_y = numpy.random.uniform(0.0, 10000.0)
            cam_pos_x = numpy.random.uniform(-500.0, 500.0)
            cam_pos_y = numpy.random.uniform(-500.0, 500.0)
            cam_pos_z = numpy.random.uniform(0.0, 10000.0)
            cam_rot_x = 0.0
            cam_rot_y = 0.0
            cam_rot_z = 0.0

            parameters = [cam_focal_length_x, cam_focal_length_y,
                          cam_pos_x, cam_pos_y, cam_pos_z,
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

    def project_points_3d(self, points_3d):

        fr_cam = self.camera_frame(
            self._cam_pos_x, self._cam_pos_y, self._cam_pos_z,
            self._cam_rot_x, self._cam_rot_y, self._cam_rot_z,
            self._cam_origin_axis)

        pts = map(lambda pt: self.pixel_coordinates(
            fr_cam.local_point(pt),
            self._cam_width_image,
            self._cam_height_image,
            self._cam_focal_length_x,
            self._cam_focal_length_y), points_3d)

        return pts

    @staticmethod
    def load(file_path):
        with open(file_path + '.json', 'r') as input_file:
            save_class = json.load(input_file)

            c = CalibrationCameraTop()

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
            c._angle_factor = save_class['angle_factor']
            c._cam_origin_axis = numpy.array(
                save_class['cam_origin_axis']).reshape((4, 4)).astype(
                numpy.float32)

        return c

    def calibrate(self,
                  ref_target_points_2d,
                  ref_target_points_3d,
                  size_image,
                  angle_factor,
                  number_of_repetition=1,
                  verbose=False):

        self._verbose = verbose
        self._angle_factor = angle_factor

        self._ref_target_points_2d = ref_target_points_2d
        self._ref_number = len(ref_target_points_2d)

        self._ref_target_points_3d = ref_target_points_3d
        self._cam_width_image = size_image[0]
        self._cam_height_image = size_image[1]

        parameters = self.find_parameters(number_of_repetition)

        for i in [5, 6, 7]:
            parameters[i] %= math.pi* 2.0

        self._cam_focal_length_x = parameters[0]
        self._cam_focal_length_y = parameters[1]
        self._cam_pos_x = parameters[2]
        self._cam_pos_y = parameters[3]
        self._cam_pos_z = parameters[4]
        self._cam_rot_x = parameters[5]
        self._cam_rot_y = parameters[6]
        self._cam_rot_z = parameters[7]

        err = self.fit_function(parameters)
        if self._verbose:
            print 'Result : ', parameters
            print 'Err : ', err, ' -- ', err / self._ref_number

        self._verbose = False

        return err / self._ref_number


class CalibrationCameraTopNewNew(CalibrationCamera):
    def __init__(self):
        CalibrationCamera.__init__(self)
        self._verbose = False

        self._ref_target_points_local_3d = None
        self._ref_target_points_2d = None
        self._ref_target_points_3d = None

        self._ref_number = None

        self._cam_pos_z = 3695 - 1200

        self._cam_origin_axis = numpy.array([[0., -1., 0., 0.],
                                             [1., 0., 0., 0.],
                                             [0., 0., 1., 0.],
                                             [0., 0., 0., 1.]])

    def fit_function(self, x0):
        err = 0

        cam_focal_length_x, cam_focal_length_y, \
        cam_pos_x, cam_pos_y, \
        cam_rot_x, cam_rot_y, cam_rot_z = x0

        fr_cam = self.camera_frame(
            cam_pos_x, cam_pos_y, self._cam_pos_z,
            cam_rot_x, cam_rot_y, cam_rot_z,
            self._cam_origin_axis)

        for i in xrange(len(self._ref_target_points_2d)):
            pts = map(lambda pt: self.pixel_coordinates(
                fr_cam.local_point(pt),
                self._cam_width_image,
                self._cam_height_image,
                cam_focal_length_x,
                cam_focal_length_y), self._ref_target_points_3d[i])

            err += numpy.linalg.norm(
                numpy.array(pts) - self._ref_target_points_2d[i], axis=1).sum()

        if self._verbose:
            print err

        return err

    def find_parameters(self, number_of_repetition):
        best_parameters = None
        min_err = float('inf')
        for i in range(number_of_repetition + 1):

            cam_focal_length_x = numpy.random.uniform(0.0, 10000.0)
            cam_focal_length_y = numpy.random.uniform(0.0, 10000.0)
            cam_pos_x = numpy.random.uniform(-500.0, 500.0)
            cam_pos_y = numpy.random.uniform(-500.0, 500.0)
            cam_rot_x = 0.0
            cam_rot_y = 0.0
            cam_rot_z = 0.0

            parameters = [cam_focal_length_x, cam_focal_length_y,
                          cam_pos_x, cam_pos_y,
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

    def project_points_3d(self, points_3d):

        fr_cam = self.camera_frame(
            self._cam_pos_x, self._cam_pos_y, self._cam_pos_z,
            self._cam_rot_x, self._cam_rot_y, self._cam_rot_z,
            self._cam_origin_axis)

        pts = map(lambda pt: self.pixel_coordinates(
            fr_cam.local_point(pt),
            self._cam_width_image,
            self._cam_height_image,
            self._cam_focal_length_x,
            self._cam_focal_length_y), points_3d)

        return pts

    @staticmethod
    def load(file_path):
        with open(file_path + '.json', 'r') as input_file:
            save_class = json.load(input_file)

            c = CalibrationCameraTop()

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
            c._angle_factor = save_class['angle_factor']
            c._cam_origin_axis = numpy.array(
                save_class['cam_origin_axis']).reshape((4, 4)).astype(
                numpy.float32)

        return c

    def calibrate(self,
                  ref_target_points_2d,
                  ref_target_points_3d,
                  size_image,
                  angle_factor,
                  number_of_repetition=1,
                  verbose=False):

        self._verbose = verbose
        self._angle_factor = angle_factor

        self._ref_target_points_2d = ref_target_points_2d
        self._ref_number = len(ref_target_points_2d)

        self._ref_target_points_3d = ref_target_points_3d
        self._cam_width_image = size_image[0]
        self._cam_height_image = size_image[1]

        parameters = self.find_parameters(number_of_repetition)

        for i in [4, 5, 6]:
            parameters[i] %= math.pi* 2.0

        self._cam_focal_length_x = parameters[0]
        self._cam_focal_length_y = parameters[1]
        self._cam_pos_x = parameters[2]
        self._cam_pos_y = parameters[3]
        self._cam_rot_x = parameters[4]
        self._cam_rot_y = parameters[5]
        self._cam_rot_z = parameters[6]

        err = self.fit_function(parameters)
        if self._verbose:
            print 'Result : ', parameters
            print 'Err : ', err, ' -- ', err / self._ref_number

        self._verbose = False

        return err / self._ref_number


class CalibrationCameraSideWith1Target(CalibrationCamera):
    def __init__(self):
        CalibrationCamera.__init__(self)
        self._verbose = False
        self._ref_target_points_local_3d = None
        self._ref_number = None
        self._ref_target_points_2d = None

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

    def __str__(self):
        out = ''
        out += CalibrationCamera.__str__(self)

        out += 'Target : \n'
        out += '\tPosition X : ' + str(self._target_pos_x) + '\n'
        out += '\tPosition Y : ' + str(self._target_pos_y) + '\n'
        out += '\tPosition Z : ' + str(self._target_pos_z) + '\n\n'
        out += '\tRotation X : ' + str(self._target_rot_x) + '\n'
        out += '\tRotation Y : ' + str(self._target_rot_y) + '\n'
        out += '\tRotation Z : ' + str(self._target_rot_z) + '\n\n'

        return out

    def fit_function(self, x0):
        err = 0

        cam_focal_length_x, cam_focal_length_y, \
            cam_pos_x, cam_pos_y, \
            cam_rot_x, cam_rot_y, cam_rot_z, \
            angle_factor, \
            target_pos_x, target_pos_y, target_pos_z, \
            target_rot_x, target_rot_y, target_rot_z = x0

        fr_cam = self.camera_frame(
            cam_pos_x, cam_pos_y, self._cam_pos_z,
            cam_rot_x, cam_rot_y, cam_rot_z,
            self._cam_origin_axis)

        for alpha, ref_pts in self._ref_target_points_2d.items():
            fr_target = self.target_frame(
                target_pos_x, target_pos_y, target_pos_z,
                target_rot_x, target_rot_y, target_rot_z,
                math.radians(alpha * angle_factor))

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
            cam_pos_y = 0.0
            cam_rot_x = 0.0
            cam_rot_y = 0.0
            cam_rot_z = 0.0

            angle_factor = 1.0

            target_pos_x = numpy.random.uniform(-1000.0, 1000.0)
            target_pos_y = numpy.random.uniform(-1000.0, 1000.0)
            target_pos_z = numpy.random.uniform(0, 1000.0)
            target_rot_x = 0.0
            target_rot_y = 0.0
            target_rot_z = 0.0

            parameters = [cam_focal_length_x, cam_focal_length_y,
                          cam_pos_x, cam_pos_y,
                          cam_rot_x, cam_rot_y, cam_rot_z,
                          angle_factor,
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

        for i in [4, 5, 6, 11, 12, 13]:
            parameters[i] %= math.pi* 2.0

        # Camera Parameters
        self._cam_focal_length_x = parameters[0]
        self._cam_focal_length_y = parameters[1]
        self._cam_pos_x = parameters[2]
        self._cam_pos_y = parameters[3]
        self._cam_rot_x = parameters[4]
        self._cam_rot_y = parameters[5]
        self._cam_rot_z = parameters[6]

        self._angle_factor = parameters[7]

        # Target Parameters
        self._target_pos_x = parameters[8]
        self._target_pos_y = parameters[9]
        self._target_pos_z = parameters[10]
        self._target_rot_x = parameters[11]
        self._target_rot_y = parameters[12]
        self._target_rot_z = parameters[13]

        err = self.fit_function(parameters)
        if self._verbose:
            print 'Result : ', parameters
            print 'Err : ', err, ' -- ', err / self._ref_number

        self._verbose = False
        return err / self._ref_number

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
            c._angle_factor = save_class['angle_factor']
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
        save_class['angle_factor'] = self._angle_factor
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
            math.radians(alpha * self._angle_factor))

        return map(lambda pt: fr_target.global_point(pt), ref_points_local_3d)

    def get_target_projected(self, alpha, ref_target_1_points_local_3d):

        fr_cam = self.camera_frame(
            self._cam_pos_x, self._cam_pos_y, self._cam_pos_z,
            self._cam_rot_x, self._cam_rot_y, self._cam_rot_z,
            self._cam_origin_axis)

        fr_target = self.target_frame(self._target_pos_x,
                                      self._target_pos_y,
                                      self._target_pos_z,
                                      self._target_rot_x,
                                      self._target_rot_y,
                                      self._target_rot_z,
                                      math.radians(alpha * self._angle_factor))

        target_pts = map(lambda pt: fr_target.global_point(pt),
                         ref_target_1_points_local_3d)

        pts = map(lambda pt: self.pixel_coordinates(
            fr_cam.local_point(pt),
            self._cam_width_image,
            self._cam_height_image,
            self._cam_focal_length_x,
            self._cam_focal_length_y), target_pts)

        return pts


class CalibrationCameraSideWith2Target(CalibrationCamera):
    def __init__(self):
        CalibrationCamera.__init__(self)
        self._verbose = False
        self._ref_target_1_points_local_3d = None
        self._ref_target_2_points_local_3d = None
        self._ref_number = None
        self._ref_target_1_points_2d = None
        self._ref_target_2_points_2d = None

        self._cam_pos_z = 0.0
        self._cam_rot_y = 0.0
        self._cam_origin_axis = numpy.array([[0., 0., 1., 0.],
                                             [1., 0., 0., 0.],
                                             [0., 1., 0., 0.],
                                             [0., 0., 0., 1.]])

        # self._cam_origin_axis = numpy.array([[0., 0., -1., 0.],
        #                                      [1., 0., 0., 0.],
        #                                      [0., 1., 0., 0.],
        #                                      [0., 0., 0., 1.]])

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

    def __str__(self):
        out = ''
        out += CalibrationCamera.__str__(self)

        out += 'Target 1: \n'
        out += '\tPosition X : ' + str(self._target_1_pos_x) + '\n'
        out += '\tPosition Y : ' + str(self._target_1_pos_y) + '\n'
        out += '\tPosition Z : ' + str(self._target_1_pos_z) + '\n\n'
        out += '\tRotation X : ' + str(self._target_1_rot_x) + '\n'
        out += '\tRotation Y : ' + str(self._target_1_rot_y) + '\n'
        out += '\tRotation Z : ' + str(self._target_1_rot_z) + '\n\n'

        out += 'Target 2: \n'
        out += '\tPosition X : ' + str(self._target_2_pos_x) + '\n'
        out += '\tPosition Y : ' + str(self._target_2_pos_y) + '\n'
        out += '\tPosition Z : ' + str(self._target_2_pos_z) + '\n\n'
        out += '\tRotation X : ' + str(self._target_2_rot_x) + '\n'
        out += '\tRotation Y : ' + str(self._target_2_rot_y) + '\n'
        out += '\tRotation Z : ' + str(self._target_2_rot_z) + '\n\n'

        return out

    def fit_function(self, x0):
        err = 0

        cam_focal_length_x, cam_focal_length_y, \
            cam_pos_x, cam_pos_y, \
            cam_rot_x, cam_rot_z, \
            angle_factor, \
            target_1_pos_x, target_1_pos_y, target_1_pos_z,\
            target_1_rot_x, target_1_rot_y, target_1_rot_z,\
            target_2_pos_x, target_2_pos_y, target_2_pos_z,\
            target_2_rot_x, target_2_rot_y, target_2_rot_z = x0

        # angle_factor = abs(angle_factor)

        fr_cam = self.camera_frame(
            cam_pos_x, cam_pos_y, self._cam_pos_z,
            cam_rot_x, self._cam_rot_y, cam_rot_z,
            self._cam_origin_axis)

        for alpha, ref_pts in self._ref_target_1_points_2d.items():

            fr_target = self.target_frame(target_1_pos_x,
                                          target_1_pos_y,
                                          target_1_pos_z,
                                          target_1_rot_x,
                                          target_1_rot_y,
                                          target_1_rot_z,
                                          math.radians(alpha * angle_factor))

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
                                          math.radians(alpha * angle_factor))

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
            cam_pos_y = 0.0
            cam_rot_x = 0.0
            cam_rot_z = 0.0

            angle_factor = 1.0

            target_1_pos_x = numpy.random.uniform(-1000.0, 1000.0)
            target_1_pos_y = numpy.random.uniform(-1000.0, 1000.0)
            target_1_pos_z = numpy.random.uniform(0, 1000.0)
            target_1_rot_x = 0
            target_1_rot_y = 0
            target_1_rot_z = 0

            target_2_pos_x = - target_1_pos_x
            target_2_pos_y = - target_1_pos_y
            target_2_pos_z = numpy.random.uniform(0, 1000.0)
            target_2_rot_x = 0
            target_2_rot_y = 0
            target_2_rot_z = 0

            parameters = [cam_focal_length_x, cam_focal_length_y,
                          cam_pos_x, cam_pos_y,
                          cam_rot_x, cam_rot_z,
                          angle_factor,
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

        for i in [4, 5, 10, 11, 12, 16, 17, 18]:
            parameters[i] %= math.pi * 2.0

        # Camera Parameters
        self._cam_focal_length_x = parameters[0]
        self._cam_focal_length_y = parameters[1]
        self._cam_pos_x = parameters[2]
        self._cam_pos_y = parameters[3]
        self._cam_rot_x = parameters[4]
        self._cam_rot_z = parameters[5]

        self._angle_factor = parameters[6]

        # Target 1 Parameters
        self._target_1_pos_x = parameters[7]
        self._target_1_pos_y = parameters[8]
        self._target_1_pos_z = parameters[9]
        self._target_1_rot_x = parameters[10]
        self._target_1_rot_y = parameters[11]
        self._target_1_rot_z = parameters[12]

        # Target 2 Parameters
        self._target_2_pos_x = parameters[13]
        self._target_2_pos_y = parameters[14]
        self._target_2_pos_z = parameters[15]
        self._target_2_rot_x = parameters[16]
        self._target_2_rot_y = parameters[17]
        self._target_2_rot_z = parameters[18]

        err = self.fit_function(parameters)
        if self._verbose:
            print 'Result : ', parameters
            print 'Err : ', err, ' -- ', err / self._ref_number

        self._verbose = False

        return err / self._ref_number

    def get_target_1_projected(self, alpha, ref_target_1_points_local_3d):

        fr_cam = self.camera_frame(
            self._cam_pos_x, self._cam_pos_y, self._cam_pos_z,
            self._cam_rot_x, self._cam_rot_y, self._cam_rot_z,
            self._cam_origin_axis)

        fr_target = self.target_frame(self._target_1_pos_x,
                                      self._target_1_pos_y,
                                      self._target_1_pos_z,
                                      self._target_1_rot_x,
                                      self._target_1_rot_y,
                                      self._target_1_rot_z,
                                      math.radians(alpha * self._angle_factor))

        target_pts = map(lambda pt: fr_target.global_point(pt),
                         ref_target_1_points_local_3d)

        pts = map(lambda pt: self.pixel_coordinates(
            fr_cam.local_point(pt),
            self._cam_width_image,
            self._cam_height_image,
            self._cam_focal_length_x,
            self._cam_focal_length_y), target_pts)

        return pts

    def get_target_2_projected(self, alpha, ref_target_2_points_local_3d):

        fr_cam = self.camera_frame(
            self._cam_pos_x, self._cam_pos_y, self._cam_pos_z,
            self._cam_rot_x, self._cam_rot_y, self._cam_rot_z,
            self._cam_origin_axis)

        fr_target = self.target_frame(self._target_2_pos_x,
                                      self._target_2_pos_y,
                                      self._target_2_pos_z,
                                      self._target_2_rot_x,
                                      self._target_2_rot_y,
                                      self._target_2_rot_z,
                                      math.radians(alpha * self._angle_factor))

        target_pts = map(lambda pt: fr_target.global_point(pt),
                         ref_target_2_points_local_3d)

        pts = map(lambda pt: self.pixel_coordinates(
            fr_cam.local_point(pt),
            self._cam_width_image,
            self._cam_height_image,
            self._cam_focal_length_x,
            self._cam_focal_length_y), target_pts)

        return pts

    def get_target_1_ref_points_global_3d(self,
                                          alpha,
                                          ref_target_1_points_local_3d):

        fr_target = self.target_frame(self._target_1_pos_x,
                                      self._target_1_pos_y,
                                      self._target_1_pos_z,
                                      self._target_1_rot_x,
                                      self._target_1_rot_y,
                                      self._target_1_rot_z,
                                      math.radians(alpha * self._angle_factor))

        return map(lambda pt: fr_target.global_point(pt),
                   ref_target_1_points_local_3d)

    def get_target_2_ref_points_global_3d(self,
                                          alpha,
                                          ref_target_2_points_local_3d):

        fr_target = self.target_frame(self._target_2_pos_x,
                                      self._target_2_pos_y,
                                      self._target_2_pos_z,
                                      self._target_2_rot_x,
                                      self._target_2_rot_y,
                                      self._target_2_rot_z,
                                      math.radians(alpha * self._angle_factor))

        return map(lambda pt: fr_target.global_point(pt),
                   ref_target_2_points_local_3d)

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
        save_class['angle_factor'] = self._angle_factor
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
            c._angle_factor = save_class['angle_factor']
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


class CalibrationCameraSideWith2TargetYXZ(CalibrationCamera):
    def __init__(self):
        CalibrationCamera.__init__(self)
        self._verbose = False
        self._ref_target_1_points_local_3d = None
        self._ref_target_2_points_local_3d = None
        self._ref_number = None
        self._ref_target_1_points_2d = None
        self._ref_target_2_points_2d = None

        self._cam_pos_z = 0.0

        self._cam_rot_z = 0.0
        self._cam_rot_y = 0.0
        self._cam_origin_axis = numpy.array([[1., 0., 0., 0.],
                                             [0., 0., -1., 0.],
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

    def __str__(self):
        out = ''
        out += CalibrationCamera.__str__(self)

        out += 'Target 1: \n'
        out += '\tPosition X : ' + str(self._target_1_pos_x) + '\n'
        out += '\tPosition Y : ' + str(self._target_1_pos_y) + '\n'
        out += '\tPosition Z : ' + str(self._target_1_pos_z) + '\n\n'
        out += '\tRotation X : ' + str(self._target_1_rot_x) + '\n'
        out += '\tRotation Y : ' + str(self._target_1_rot_y) + '\n'
        out += '\tRotation Z : ' + str(self._target_1_rot_z) + '\n\n'

        out += 'Target 2: \n'
        out += '\tPosition X : ' + str(self._target_2_pos_x) + '\n'
        out += '\tPosition Y : ' + str(self._target_2_pos_y) + '\n'
        out += '\tPosition Z : ' + str(self._target_2_pos_z) + '\n\n'
        out += '\tRotation X : ' + str(self._target_2_rot_x) + '\n'
        out += '\tRotation Y : ' + str(self._target_2_rot_y) + '\n'
        out += '\tRotation Z : ' + str(self._target_2_rot_z) + '\n\n'

        return out

    def fit_function(self, x0):
        err = 0

        cam_focal_length_x, cam_focal_length_y, \
        cam_pos_x, cam_pos_y, \
        cam_rot_x, cam_rot_z, \
        angle_factor, \
        target_1_pos_x, target_1_pos_y, target_1_pos_z, \
        target_1_rot_x, target_1_rot_y, target_1_rot_z, \
        target_2_pos_x, target_2_pos_y, target_2_pos_z, \
        target_2_rot_x, target_2_rot_y, target_2_rot_z = x0

        fr_cam = self.camera_frame(
            cam_pos_x, cam_pos_y, self._cam_pos_z,
            cam_rot_x, self._cam_rot_y, cam_rot_z,
            self._cam_origin_axis)

        for alpha, ref_pts in self._ref_target_1_points_2d.items():
            fr_target = self.target_frame(target_1_pos_x,
                                          target_1_pos_y,
                                          target_1_pos_z,
                                          target_1_rot_x,
                                          target_1_rot_y,
                                          target_1_rot_z,
                                          math.radians(alpha * angle_factor))

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
                                          math.radians(alpha * angle_factor))

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
            cam_pos_x = 0.0
            cam_pos_y = - numpy.random.uniform(10000.0, 1000.0)

            cam_rot_x = 0.0
            cam_rot_z = 0.0

            angle_factor = 1.0

            target_1_pos_x = numpy.random.uniform(-1000.0, 1000.0)
            target_1_pos_y = numpy.random.uniform(-1000.0, 1000.0)
            target_1_pos_z = numpy.random.uniform(-1000, 1000.0)
            target_1_rot_x = 0
            target_1_rot_y = 0
            target_1_rot_z = 0

            target_2_pos_x = -target_1_pos_x
            target_2_pos_y = -target_1_pos_y
            target_2_pos_z = numpy.random.uniform(-1000, 1000.0)
            target_2_rot_x = 0
            target_2_rot_y = 0
            target_2_rot_z = 0

            parameters = [cam_focal_length_x, cam_focal_length_y,
                          cam_pos_x, cam_pos_y,
                          cam_rot_x, cam_rot_z,
                          angle_factor,
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

    def get_target_1_projected(self, alpha, ref_target_1_points_local_3d):

        fr_cam = self.camera_frame(
            self._cam_pos_x, self._cam_pos_y, self._cam_pos_z,
            self._cam_rot_x, self._cam_rot_y, self._cam_rot_z,
            self._cam_origin_axis)

        fr_target = self.target_frame(self._target_1_pos_x,
                                      self._target_1_pos_y,
                                      self._target_1_pos_z,
                                      self._target_1_rot_x,
                                      self._target_1_rot_y,
                                      self._target_1_rot_z,
                                      math.radians(alpha * self._angle_factor))

        target_pts = map(lambda pt: fr_target.global_point(pt),
                         ref_target_1_points_local_3d)

        pts = map(lambda pt: self.pixel_coordinates(
            fr_cam.local_point(pt),
            self._cam_width_image,
            self._cam_height_image,
            self._cam_focal_length_x,
            self._cam_focal_length_y), target_pts)

        return pts

    def get_target_2_projected(self, alpha, ref_target_2_points_local_3d):

        fr_cam = self.camera_frame(
            self._cam_pos_x, self._cam_pos_y, self._cam_pos_z,
            self._cam_rot_x, self._cam_rot_y, self._cam_rot_z,
            self._cam_origin_axis)

        fr_target = self.target_frame(self._target_2_pos_x,
                                      self._target_2_pos_y,
                                      self._target_2_pos_z,
                                      self._target_2_rot_x,
                                      self._target_2_rot_y,
                                      self._target_2_rot_z,
                                      math.radians(alpha * self._angle_factor))

        target_pts = map(lambda pt: fr_target.global_point(pt),
                         ref_target_2_points_local_3d)

        pts = map(lambda pt: self.pixel_coordinates(
            fr_cam.local_point(pt),
            self._cam_width_image,
            self._cam_height_image,
            self._cam_focal_length_x,
            self._cam_focal_length_y), target_pts)

        return pts

    def get_target_1_ref_points_global_3d(self,
                                          alpha,
                                          ref_target_1_points_local_3d):

        fr_target = self.target_frame(self._target_1_pos_x,
                                      self._target_1_pos_y,
                                      self._target_1_pos_z,
                                      self._target_1_rot_x,
                                      self._target_1_rot_y,
                                      self._target_1_rot_z,
                                      math.radians(alpha * self._angle_factor))

        return map(lambda pt: fr_target.global_point(pt),
                   ref_target_1_points_local_3d)

    def get_target_2_ref_points_global_3d(self,
                                          alpha,
                                          ref_target_2_points_local_3d):

        fr_target = self.target_frame(self._target_2_pos_x,
                                      self._target_2_pos_y,
                                      self._target_2_pos_z,
                                      self._target_2_rot_x,
                                      self._target_2_rot_y,
                                      self._target_2_rot_z,
                                      math.radians(alpha * self._angle_factor))

        return map(lambda pt: fr_target.global_point(pt),
                   ref_target_2_points_local_3d)

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

        for i in [4, 6, 10, 11, 12, 16, 17, 18]:
            parameters[i] %= math.pi * 2.0

        # Camera Parameters
        self._cam_focal_length_x = parameters[0]
        self._cam_focal_length_y = parameters[1]
        self._cam_pos_x = parameters[2]
        self._cam_pos_y = parameters[3]
        self._cam_rot_x = parameters[4]
        self._cam_rot_z = parameters[5]

        self._angle_factor = parameters[6]

        # Target 1 Parameters
        self._target_1_pos_x = parameters[7]
        self._target_1_pos_y = parameters[8]
        self._target_1_pos_z = parameters[9]
        self._target_1_rot_x = parameters[10]
        self._target_1_rot_y = parameters[11]
        self._target_1_rot_z = parameters[12]

        # Target 2 Parameters
        self._target_2_pos_x = parameters[13]
        self._target_2_pos_y = parameters[14]
        self._target_2_pos_z = parameters[15]
        self._target_2_rot_x = parameters[16]
        self._target_2_rot_y = parameters[17]
        self._target_2_rot_z = parameters[18]

        err = self.fit_function(parameters)
        if self._verbose:
            print 'Result : ', parameters
            print 'Err : ', err, ' -- ', err / self._ref_number

        self._verbose = False

        return err / self._ref_number

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
        save_class['angle_factor'] = self._angle_factor
        save_class['cam_origin_axis'] = self._cam_origin_axis.reshape(
            (16,)).tolist()

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
            c._angle_factor = save_class['angle_factor']
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


class CalibrationCameraSideCameraTopWith2Target(object):
    def __init__(self):

        self._verbose = False

        self._ref_target_1_points_local_3d = None
        self._ref_target_2_points_local_3d = None

        self._ref_number = None

        self._ref_target_1_side_points_2d = None
        self._ref_target_2_side_points_2d = None
        self._ref_target_1_top_points_2d = None
        self._ref_target_2_top_points_2d = None

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

        self._cam_side_width_image = None
        self._cam_side_height_image = None
        self._cam_side_focal_length_x = None
        self._cam_side_focal_length_y = None
        self._cam_side_pos_x = None
        self._cam_side_pos_y = None
        self._cam_side_pos_z = 0.0
        self._cam_side_rot_x = None
        self._cam_side_rot_y = 0.0
        self._cam_side_rot_z = None
        self._cam_side_origin_axis = numpy.array([[0., 0., 1., 0.],
                                                  [1., 0., 0., 0.],
                                                  [0., 1., 0., 0.],
                                                  [0., 0., 0., 1.]])

        self._cam_top_width_image = None
        self._cam_top_height_image = None
        self._cam_top_focal_length_x = None
        self._cam_top_focal_length_y = None
        self._cam_top_pos_x = None
        self._cam_top_pos_y = None
        self._cam_top_pos_z = None
        self._cam_top_rot_x = None
        self._cam_top_rot_y = None
        self._cam_top_rot_z = None
        self._cam_top_origin_axis = numpy.array([[0., -1., 0., 0.],
                                                 [1., 0., 0., 0.],
                                                 [0., 0., 1., 0.],
                                                 [0., 0., 0., 1.]])

        self._angle_factor = None

    def fit_function(self, x0):
        err = 0

        cam_side_focal_length_x, cam_side_focal_length_y, \
        cam_side_pos_x, cam_side_pos_y, \
        cam_side_rot_x, cam_side_rot_z, \
        cam_top_focal_length_x, cam_top_focal_length_y, \
        cam_top_pos_x, cam_top_pos_y, cam_top_pos_z, \
        cam_top_rot_x, cam_top_rot_y, cam_top_rot_z, \
        angle_factor, \
        target_1_pos_x, target_1_pos_y, target_1_pos_z, \
        target_1_rot_x, target_1_rot_y, target_1_rot_z, \
        target_2_pos_x, target_2_pos_y, target_2_pos_z, \
        target_2_rot_x, target_2_rot_y, target_2_rot_z = x0

        # cam_pos_y = max(min(cam_pos_y, 500), -500)

        fr_cam_side = CalibrationCamera.camera_frame(
            cam_side_pos_x, cam_side_pos_y, self._cam_side_pos_z,
            cam_side_rot_x, self._cam_side_rot_y, cam_side_rot_z,
            self._cam_side_origin_axis)

        for alpha, ref_pts in self._ref_target_1_points_2d.items():
            fr_target = CalibrationCamera.target_frame(target_1_pos_x,
                                                       target_1_pos_y,
                                                       target_1_pos_z,
                                                       target_1_rot_x,
                                                       target_1_rot_y,
                                                       target_1_rot_z,
                                                       math.radians(
                                                           alpha * angle_factor))

            target_pts = map(lambda pt: fr_target.global_point(pt),
                             self._ref_target_1_points_local_3d)

            pts = map(lambda pt: CalibrationCamera.pixel_coordinates(
                fr_cam_side.local_point(pt),
                self._cam_side_width_image,
                self._cam_side_height_image,
                cam_side_focal_length_x,
                cam_side_focal_length_y), target_pts)

            err += numpy.linalg.norm(numpy.array(pts) - ref_pts, axis=1).sum()

        for alpha, ref_pts in self._ref_target_2_points_2d.items():
            fr_target = CalibrationCamera.target_frame(target_2_pos_x,
                                                       target_2_pos_y,
                                                       target_2_pos_z,
                                                       target_2_rot_x,
                                                       target_2_rot_y,
                                                       target_2_rot_z,
                                                       math.radians(
                                                           alpha * angle_factor))

            target_pts = map(lambda pt: fr_target.global_point(pt),
                             self._ref_target_2_points_local_3d)

            pts = map(lambda pt: CalibrationCamera.pixel_coordinates(
                fr_cam_side.local_point(pt),
                self._cam_side_width_image,
                self._cam_side_height_image,
                cam_side_focal_length_x,
                cam_side_focal_length_y), target_pts)

            err += numpy.linalg.norm(numpy.array(pts) - ref_pts, axis=1).sum()





        if self._verbose:
            print err

        return err

    def find_parameters(self, number_of_repetition):

        best_parameters = None
        min_err = float('inf')
        for i in range(number_of_repetition + 1):

            cam_side_focal_length_x = numpy.random.uniform(1000.0, 10000.0)
            cam_side_focal_length_y = numpy.random.uniform(1000.0, 10000.0)
            cam_side_pos_x = numpy.random.uniform(4000.0, 10000.0)
            cam_side_pos_y = 0.0
            cam_side_rot_x = 0.0
            cam_side_rot_z = 0.0

            angle_factor = 1.0

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

            parameters = [cam_side_focal_length_x, cam_side_focal_length_y,
                          cam_side_pos_x, cam_side_pos_y,
                          cam_side_rot_x, cam_side_rot_z,
                          angle_factor,
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

        self._cam_side_width_image = size_image[0]
        self._cam_side_height_image = size_image[1]

        parameters = self.find_parameters(number_of_repetition)

        for i in [4, 5, 10, 11, 12, 16, 17, 18]:
            parameters[i] %= math.pi* 2.0

        # Camera Parameters
        self._cam_side_focal_length_x = parameters[0]
        self._cam_side_focal_length_y = parameters[1]
        self._cam_side_pos_x = parameters[2]
        self._cam_side_pos_y = parameters[3]
        self._cam_side_rot_x = parameters[4]
        self._cam_side_rot_z = parameters[5]

        self._angle_factor = parameters[6]

        # Target 1 Parameters
        self._target_1_pos_x = parameters[7]
        self._target_1_pos_y = parameters[8]
        self._target_1_pos_z = parameters[9]
        self._target_1_rot_x = parameters[10]
        self._target_1_rot_y = parameters[11]
        self._target_1_rot_z = parameters[12]

        # Target 2 Parameters
        self._target_2_pos_x = parameters[13]
        self._target_2_pos_y = parameters[14]
        self._target_2_pos_z = parameters[15]
        self._target_2_rot_x = parameters[16]
        self._target_2_rot_y = parameters[17]
        self._target_2_rot_z = parameters[18]

        err = self.fit_function(parameters)
        if self._verbose:
            print 'Result : ', parameters
            print 'Err : ', err, ' -- ', err / self._ref_number

        self._verbose = False

        return err / self._ref_number

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
        save_class['angle_factor'] = self._angle_factor
        save_class['cam_origin_axis'] = self._cam_origin_axis.reshape(
            (16,)).tolist()

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
            c._angle_factor = save_class['angle_factor']
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


class CalibrationCameraSideWith2TargetInver(CalibrationCamera):
    def __init__(self):
        CalibrationCamera.__init__(self)
        self._verbose = False
        self._ref_target_1_points_local_3d = None
        self._ref_target_2_points_local_3d = None
        self._ref_number = None
        self._ref_target_1_points_2d = None
        self._ref_target_2_points_2d = None

        self._cam_pos_z = 0.0
        self._cam_origin_axis = numpy.array([[1., 0., 1., 0.],
                                             [0., 0., 0., 0.],
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

    def __str__(self):
        out = ''
        out += CalibrationCamera.__str__(self)

        out += 'Target 1: \n'
        out += '\tPosition X : ' + str(self._target_1_pos_x) + '\n'
        out += '\tPosition Y : ' + str(self._target_1_pos_y) + '\n'
        out += '\tPosition Z : ' + str(self._target_1_pos_z) + '\n\n'
        out += '\tRotation X : ' + str(self._target_1_rot_x) + '\n'
        out += '\tRotation Y : ' + str(self._target_1_rot_y) + '\n'
        out += '\tRotation Z : ' + str(self._target_1_rot_z) + '\n\n'

        out += 'Target 2: \n'
        out += '\tPosition X : ' + str(self._target_2_pos_x) + '\n'
        out += '\tPosition Y : ' + str(self._target_2_pos_y) + '\n'
        out += '\tPosition Z : ' + str(self._target_2_pos_z) + '\n\n'
        out += '\tRotation X : ' + str(self._target_2_rot_x) + '\n'
        out += '\tRotation Y : ' + str(self._target_2_rot_y) + '\n'
        out += '\tRotation Z : ' + str(self._target_2_rot_z) + '\n\n'

        return out

    def fit_function(self, x0):
        err = 0

        cam_focal_length_x, cam_focal_length_y, \
        cam_pos_x, cam_pos_y, \
        cam_rot_x, cam_rot_y, cam_rot_z, \
        angle_factor, \
        target_1_pos_x, target_1_pos_y, target_1_pos_z, \
        target_1_rot_x, target_1_rot_y, target_1_rot_z, \
        target_2_pos_x, target_2_pos_y, target_2_pos_z, \
        target_2_rot_x, target_2_rot_y, target_2_rot_z = x0

        # cam_pos_y = max(min(cam_pos_y, 500), -500)

        fr_cam = self.camera_frame(
            cam_pos_x, cam_pos_y, self._cam_pos_z,
            cam_rot_x, cam_rot_y, cam_rot_z,
            self._cam_origin_axis)

        for alpha, ref_pts in self._ref_target_1_points_2d.items():
            fr_target = self.target_frame(target_1_pos_x,
                                          target_1_pos_y,
                                          target_1_pos_z,
                                          target_1_rot_x,
                                          target_1_rot_y,
                                          target_1_rot_z,
                                          math.radians(alpha * angle_factor))

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
                                          math.radians(alpha * angle_factor))

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
            cam_pos_y = 0.0
            cam_rot_x = 0.0
            cam_rot_y = 0.0
            cam_rot_z = 0.0

            angle_factor = 1.0

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
                          cam_pos_x, cam_pos_y,
                          cam_rot_x, cam_rot_y, cam_rot_z,
                          angle_factor,
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

    def get_target_1_projected(self, alpha, ref_target_1_points_local_3d):

        fr_cam = self.camera_frame(
            self._cam_pos_x, self._cam_pos_y, self._cam_pos_z,
            self._cam_rot_x, self._cam_rot_y, self._cam_rot_z,
            self._cam_origin_axis)

        fr_target = self.target_frame(self._target_1_pos_x,
                                      self._target_1_pos_y,
                                      self._target_1_pos_z,
                                      self._target_1_rot_x,
                                      self._target_1_rot_y,
                                      self._target_1_rot_z,
                                      math.radians(alpha * self._angle_factor))

        target_pts = map(lambda pt: fr_target.global_point(pt),
                         ref_target_1_points_local_3d)

        pts = map(lambda pt: self.pixel_coordinates(
            fr_cam.local_point(pt),
            self._cam_width_image,
            self._cam_height_image,
            self._cam_focal_length_x,
            self._cam_focal_length_y), target_pts)

        return pts

    def get_target_2_projected(self, alpha, ref_target_2_points_local_3d):

        fr_cam = self.camera_frame(
            self._cam_pos_x, self._cam_pos_y, self._cam_pos_z,
            self._cam_rot_x, self._cam_rot_y, self._cam_rot_z,
            self._cam_origin_axis)

        fr_target = self.target_frame(self._target_2_pos_x,
                                      self._target_2_pos_y,
                                      self._target_2_pos_z,
                                      self._target_2_rot_x,
                                      self._target_2_rot_y,
                                      self._target_2_rot_z,
                                      math.radians(alpha * self._angle_factor))

        target_pts = map(lambda pt: fr_target.global_point(pt),
                         ref_target_2_points_local_3d)

        pts = map(lambda pt: self.pixel_coordinates(
            fr_cam.local_point(pt),
            self._cam_width_image,
            self._cam_height_image,
            self._cam_focal_length_x,
            self._cam_focal_length_y), target_pts)

        return pts

    def get_target_1_ref_points_global_3d(self,
                                          alpha,
                                          ref_target_1_points_local_3d):

        fr_target = self.target_frame(self._target_1_pos_x,
                                      self._target_1_pos_y,
                                      self._target_1_pos_z,
                                      self._target_1_rot_x,
                                      self._target_1_rot_y,
                                      self._target_1_rot_z,
                                      math.radians(alpha * self._angle_factor))

        return map(lambda pt: fr_target.global_point(pt),
                   ref_target_1_points_local_3d)

    def get_target_2_ref_points_global_3d(self,
                                          alpha,
                                          ref_target_2_points_local_3d):

        fr_target = self.target_frame(self._target_2_pos_x,
                                      self._target_2_pos_y,
                                      self._target_2_pos_z,
                                      self._target_2_rot_x,
                                      self._target_2_rot_y,
                                      self._target_2_rot_z,
                                      math.radians(alpha * self._angle_factor))

        return map(lambda pt: fr_target.global_point(pt),
                   ref_target_2_points_local_3d)

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

        for i in [4, 5, 6, 11, 12, 13, 17, 18, 19]:
            parameters[i] %= math.pi * 2.0

        # Camera Parameters
        self._cam_focal_length_x = parameters[0]
        self._cam_focal_length_y = parameters[1]
        self._cam_pos_x = parameters[2]
        self._cam_pos_y = parameters[3]
        self._cam_rot_x = parameters[4]
        self._cam_rot_y = parameters[5]
        self._cam_rot_z = parameters[6]

        self._angle_factor = parameters[7]

        # Target 1 Parameters
        self._target_1_pos_x = parameters[8]
        self._target_1_pos_y = parameters[9]
        self._target_1_pos_z = parameters[10]
        self._target_1_rot_x = parameters[11]
        self._target_1_rot_y = parameters[12]
        self._target_1_rot_z = parameters[13]

        # Target 2 Parameters
        self._target_2_pos_x = parameters[14]
        self._target_2_pos_y = parameters[15]
        self._target_2_pos_z = parameters[16]
        self._target_2_rot_x = parameters[17]
        self._target_2_rot_y = parameters[18]
        self._target_2_rot_z = parameters[19]

        err = self.fit_function(parameters)
        if self._verbose:
            print 'Result : ', parameters
            print 'Err : ', err, ' -- ', err / self._ref_number

        self._verbose = False

        return err / self._ref_number

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
        save_class['angle_factor'] = self._angle_factor
        save_class['cam_origin_axis'] = self._cam_origin_axis.reshape(
            (16,)).tolist()

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
            c._angle_factor = save_class['angle_factor']
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

