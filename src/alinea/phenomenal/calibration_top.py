# -*- python -*-
#
#       calibration_model.py :
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
""" This module contains a calibration model for phenoarch experiment
where a chessboard is rotating instead of a plant in a picture cabin.
"""
# ==============================================================================
import json
from math import radians, cos, sin

import numpy
import numpy.random
import scipy.optimize

from frame import Frame, x_axis, y_axis, z_axis
from transformations import concatenate_matrices, rotation_matrix
from camera import Camera


# ==============================================================================


class ChessboardModelParameters(object):
    def __init__(self):
        self._x = None
        self._y = None
        self._z = None
        self._x_rotation = None
        self._y_rotation = None
        self._z_rotation = None

    def random_initialization(self):
        pi2 = 2.0 * numpy.pi
        self._x = numpy.random.uniform(-1000.0, 1000.0)
        self._y = numpy.random.uniform(-1000.0, 1000.0)
        self._z = numpy.random.uniform(-1000.0, 1000.0)
        self._x_rotation = numpy.random.uniform(0.0, pi2)
        self._y_rotation = numpy.random.uniform(0.0, pi2)
        self._z_rotation = numpy.random.uniform(0.0, pi2)

    def get_parameters(self):
        return [self._x, self._y, self._z,
                self._x_rotation, self._y_rotation, self._z_rotation]

    def set_parameters(self,
                       x, y, z,
                       x_rotation, y_rotation, z_rotation):
        self._x = x
        self._y = y
        self._z = z
        self._x_rotation = x_rotation
        self._y_rotation = y_rotation
        self._z_rotation = z_rotation

    def __str__(self):
        description = 'Chessboard :\n'
        description += 'Position x : ' + str(self._x) + '\n'
        description += 'Position y : ' + str(self._y) + '\n'
        description += 'Position z : ' + str(self._z) + '\n'
        description += 'Angle x (rad): ' + str(self._x_rotation) + '\n'
        description += 'Angle y (rad): ' + str(self._y_rotation) + '\n'
        description += 'Angle z (rad): ' + str(self._z_rotation) + '\n'
        return description

    def write(self, file_path):
        save_class = dict()
        save_class['x'] = self._x
        save_class['y'] = self._y
        save_class['z'] = self._z
        save_class['x_rotation'] = self._x_rotation
        save_class['y_rotation'] = self._y_rotation
        save_class['z_rotation'] = self._z_rotation

        with open(file_path + '.json', 'w') as output_file:
            json.dump(save_class, output_file)

    @staticmethod
    def read(file_path):
        with open(file_path + '.json', 'r') as input_file:
            save_class = json.load(input_file)

            chessboard_model_parameters = ChessboardModelParameters()
            chessboard_model_parameters.set_parameters(save_class['x'],
                                                       save_class['y'],
                                                       save_class['z'],
                                                       save_class['x_rotation'],
                                                       save_class['y_rotation'],
                                                       save_class['z_rotation'])

        return chessboard_model_parameters


class CameraModelParameters(object):
    def __init__(self, size_image):
        self._size_image = size_image

        self._focal_length_x = None
        self._focal_length_y = None
        self._distance_to_rotation_axe = None
        self._zero_offset = None
        self._x_rotation = None
        self._y_rotation = None
        self._z_rotation = None

    def get_parameters(self):
        return [self._size_image,
                self._focal_length_x,
                self._focal_length_y,
                self._distance_to_rotation_axe,
                self._zero_offset,
                self._x_rotation,
                self._y_rotation,
                self._z_rotation]

    def set_parameters(self,
                       focal_length_x,
                       focal_length_y,
                       distance_to_rotation_axe,
                       zero_offset,
                       x_rotation,
                       y_rotation,
                       z_rotation):

        self._focal_length_x = focal_length_x
        self._focal_length_y = focal_length_y
        self._distance_to_rotation_axe = distance_to_rotation_axe
        self._zero_offset = zero_offset
        self._x_rotation = x_rotation
        self._y_rotation = y_rotation
        self._z_rotation = z_rotation

    def __str__(self):
        description = 'Camera :\n'
        description += 'Size image : ' + str(self._size_image) + '\n'
        description += 'Focal X : ' + str(self._focal_length_x) + '\n'
        description += 'Focal Y : ' + str(self._focal_length_y) + '\n'
        description += 'Distance camera : '
        description += str(self._distance_to_rotation_axe) + '\n'
        description += 'Zero offset : ' + str(self._zero_offset) + '\n'
        description += 'Angle x (rad) : ' + str(self._x_rotation) + '\n'
        description += 'Angle y (rad) : ' + str(self._y_rotation) + '\n'
        description += 'Angle z (rad) : ' + str(self._z_rotation) + '\n'
        return description

    def random_initialization(self):
        pi2 = 2.0 * numpy.pi
        self._focal_length_x = numpy.random.uniform(1000.0, 10000.0)
        self._focal_length_y = numpy.random.uniform(1000.0, 10000.0)
        self._distance_to_rotation_axe = numpy.random.uniform(1000.0, 10000.0)
        self._zero_offset = numpy.random.uniform(0.0, pi2)
        self._x_rotation = 0.0
        self._y_rotation = 0.0
        self._z_rotation = 0.0

    def write(self, file_path):
        save_class = dict()
        save_class['size_image'] = self._size_image
        save_class['focal_length_x'] = self._focal_length_x
        save_class['focal_length_y'] = self._focal_length_y
        save_class['distance_to_rotation_axe'] = self._distance_to_rotation_axe
        save_class['zero_offset'] = self._zero_offset
        save_class['x_rotation'] = self._x_rotation
        save_class['y_rotation'] = self._y_rotation
        save_class['z_rotation'] = self._z_rotation

        with open(file_path + '.json', 'w') as output_file:
            json.dump(save_class, output_file)

    @staticmethod
    def read(file_path):
        with open(file_path + '.json', 'r') as input_file:
            save_class = json.load(input_file)

            camera_model_parameters = CameraModelParameters(
                tuple(save_class['size_image']))
            camera_model_parameters.set_parameters(
                save_class['focal_length_x'],
                save_class['focal_length_y'],
                save_class['distance_to_rotation_axe'],
                save_class['zero_offset'],
                save_class['x_rotation'],
                save_class['y_rotation'],
                save_class['z_rotation'])

        return camera_model_parameters


class ModelProjection(object):
    def __init__(self, camera_model_parameters):

        parameters = camera_model_parameters.get_parameters()

        size_image = parameters[0]
        focal_length_x = parameters[1]
        focal_length_y = parameters[2]
        distance_to_rotation_axe = parameters[3]
        zero_offset = parameters[4]
        x_rotation = parameters[5]
        y_rotation = parameters[6]
        z_rotation = parameters[7]

        self._camera = Camera(size_image, (focal_length_x, focal_length_y))

        self._frame = dict()
        for angle in range(0, 360, 1):
            self._frame[angle] = camera_frame(
                distance_to_rotation_axe,
                zero_offset,
                radians(angle),
                x_rotation,
                y_rotation,
                z_rotation)

    def compute_point(self, point, angle):
        return self._frame[angle].local_point(point)

    def project_points(self, points, angle):
        pts_2d = self._camera.pixel_coordinates(
            self._frame[angle].local_points(points))

        return numpy.transpose(pts_2d)

    def project_point(self, point, angle):
        return self._camera.pixel_coordinates(
            self._frame[angle].local_point(point))


def get_function_projection(camera_model_parameters, angle):
        parameters = camera_model_parameters.get_parameters()

        size_image = parameters[0]
        focal_length_x = parameters[1]
        focal_length_y = parameters[2]
        distance_to_rotation_axe = parameters[3]
        zero_offset = parameters[4]
        x_rotation = parameters[5]
        y_rotation = parameters[6]
        z_rotation = parameters[7]

        camera = Camera(size_image, (focal_length_x, focal_length_y))

        frame = camera_frame(distance_to_rotation_axe,
                             zero_offset,
                             radians(angle),
                             x_rotation,
                             y_rotation,
                             z_rotation)

        return lambda pt3d: camera.pixel_coordinates(frame.local_point(pt3d))


class Calibration(object):
    def __init__(self, chessboard, size_image, verbose=False):
        # Size image
        self._size_image = size_image
        # Plot result
        self._verbose = verbose

        self._chessboard_pts = list()
        self._cv_pts = list()
        self._number_ref = 0

        self._number_ref += len(chessboard.corners_points)
        self._chessboard_pts = chessboard.local_corners_position_3d()
        pts = chessboard.corners_points.copy()
        for angle in pts:
            pts[angle] = pts[angle][:, 0, :]
        self._cv_pts = pts

    def fit_function(self, x0):
        err = 0

        # chess_x, chess_y, chess_z, \
        # chess_x_rotation, \
        # chess_y_rotation, \
        # chess_z_rotation, \
        # focal_length_x, focal_length_y, \
        # distance_to_rotation_axe, \
        # zero_offset, \
        # x_rotation, y_rotation, z_rotation = x0

        chess_x, chess_y, chess_z, \
            chess_x_rotation, \
            chess_y_rotation, \
            chess_z_rotation, \
            focal_length_x, focal_length_y, \
            distance_to_rotation_axe, \
            zero_offset, \
            x_rotation, y_rotation, z_rotation = x0

        cam = Camera(self._size_image, (focal_length_x, focal_length_y))

        fr_cam = camera_frame(distance_to_rotation_axe,
                              x_rotation, y_rotation, z_rotation)

        for alpha, ref_pts in self._cv_pts.items():

            fr_chess = chess_frame(
                chess_x, chess_y, chess_z,
                chess_x_rotation, chess_y_rotation, chess_z_rotation,
                zero_offset, radians(alpha))

            chess_pts = map(lambda pt: fr_chess.global_point(pt),
                            self._chessboard_pts)

            pts = map(
                lambda pt: cam.pixel_coordinates(fr_cam.local_point(pt)),
                chess_pts)

            err += numpy.linalg.norm(
                numpy.array(pts) - ref_pts, axis=1).sum()

        if self._verbose:
            print err

        return err

    def guess_estimation(self,
                         chess_params,
                         cam_params,
                         number_of_repetition):

        final_guess = None
        min_err = float('inf')
        for i in range(number_of_repetition + 1):

            chess_params.random_initialization()
            chess_x, chess_y, chess_z, \
            chess_x_rotation, chess_y_rotation, chess_z_rotation = \
                chess_params.get_parameters()

            cam_params.random_initialization()
            size_image, \
            focal_length_x, focal_length_y, \
            distance_to_rotation_axe, \
            zero_offset, \
            x_rotation, y_rotation, z_rotation = cam_params.get_parameters()

            guess = [chess_x, chess_y, chess_z,
                     chess_x_rotation,
                     chess_y_rotation,
                     chess_z_rotation,
                     focal_length_x, focal_length_y,
                     distance_to_rotation_axe,
                     zero_offset,
                     x_rotation, y_rotation, z_rotation]

            # Optimization
            guess = scipy.optimize.minimize(
                self.fit_function, guess, method='BFGS').x

            chess_x, chess_y, chess_z, \
                chess_x_rotation, \
                chess_y_rotation, \
                chess_z_rotation, \
                focal_length_x, focal_length_y, \
                distance_to_rotation_axe, \
                zero_offset, \
                x_rotation, y_rotation, z_rotation = guess

            chess_x_rotation %= 2 * numpy.pi
            chess_y_rotation %= 2 * numpy.pi
            chess_z_rotation %= 2 * numpy.pi
            zero_offset %= 2 * numpy.pi
            x_rotation %= 2 * numpy.pi
            y_rotation %= 2 * numpy.pi
            z_rotation %= 2 * numpy.pi

            guess = [chess_x, chess_y, chess_z,
                     chess_x_rotation,
                     chess_y_rotation,
                     chess_z_rotation,
                     focal_length_x, focal_length_y,
                     distance_to_rotation_axe,
                     zero_offset,
                     x_rotation, y_rotation, z_rotation]

            # Compute error compare with min_err
            err = self.fit_function(guess)
            if err < min_err:
                min_err = err
                final_guess = guess

            if self._verbose:
                err = self.fit_function(guess)
                print 'Result 1: ', guess
                print 'Err : ', err / self._number_ref

        return final_guess

    def find_model_parameters(self, number_of_repetition=1):
        """ Find physical parameters associated with a camera
        (i.e. distances and angles), using pictures of a rotating
        chessboard.

        args:
         - 'chessboard_ref' (Chessboard): reference chessboard
         - 'chessboard_corners' dict of (angle, list of pts): for
                        a picture taken with a given angle, list
                        the coordinates of all intersections on
                        the chessboard in the picture
        """

        # Creation chessboard model parameters objects
        chess_params = ChessboardModelParameters()

        # Creation Camera model parameters object
        cam_params = CameraModelParameters(self._size_image)

        # Estimation of chessboard parameters and focal of camera
        guess = self.guess_estimation(
            chess_params, cam_params, number_of_repetition)

        return guess


def compute_error_projection(cam_params, chessboards, chessboards_params):
    err = 0
    projection = ModelProjection(cam_params)

    for i in range(len(chessboards)):
        chess_pts = chessboards[i].global_corners_position_3d(
            *chessboards_params[i].get_parameters())

        cv_pts = chessboards[i].corners_points.copy()
        for angle in cv_pts:
            cv_pts[angle] = cv_pts[angle][:, 0, :]

        for angle, ref_pts in cv_pts.items():
            pts = [projection.project_point(pt, angle) for pt in chess_pts]
            err += numpy.linalg.norm(numpy.array(pts) - ref_pts, axis=1).sum()

    return err

def chess_frame(x, y, z, x_rotation, y_rotation, z_rotation, zero_offset, alpha):
    """ Compute local frame associated to chessboard

    Args:
     - x (float): x position of chess in world frame
     - y (float): y position of chess in world frame
     - z (float): z position of chess in world frame
     - x_rotation (float): elevation angle around local x axis
     - y_rotation (float): rotation angle around local y axis
     - z_rotation (float): rotation angle around local z axis

    """
    origin = [x * cos(alpha + zero_offset) - y * sin(alpha + zero_offset),
              x * sin(alpha + zero_offset) + y * cos(alpha + zero_offset),
              z]

    mat_rot_x = rotation_matrix(x_rotation, x_axis)
    mat_rot_y = rotation_matrix(y_rotation, y_axis)
    mat_rot_z = rotation_matrix((alpha + zero_offset) + z_rotation, z_axis)

    rot = concatenate_matrices(mat_rot_z, mat_rot_x, mat_rot_y)

    return Frame(rot[:3, :3].T, origin)


def camera_frame(dist, x_rotation, y_rotation, z_rotation):
    """ Compute local frame associated to the camera

    Args:
     - dist (float): distance of camera to rotation axis
     - offset (float): offset angle in radians for rotation
     - z (float): z position of cam in world frame when alpha=0

     - x_rotation (float): elevation angle of camera (around local x axis)
     - y_rotation (float): azimuth angle of camera (around local y axis)
     - z_rotation (float): tilt angle of camera (around local z axis)
     - offset_angle (float): rotation offset around z_axis in world frame
                              (i.e. rotation angle of camera when alpha=0)
     - alpha (float): rotation angle around z_axis in world frame
    """
    origin = (dist, 0.0, 0.0)

    mat_rot_x = rotation_matrix(x_rotation, x_axis)
    mat_rot_y = rotation_matrix(y_rotation, y_axis)
    mat_rot_z = rotation_matrix(z_rotation, z_axis)

    # rot = concatenate_matrices(mat_rot_x, mat_rot_y, mat_rot_z)
    rot = concatenate_matrices(mat_rot_y, mat_rot_x, mat_rot_z)
    return Frame(rot[:3, :3].T, origin)



def chess_frame_2(x, y, z, x_rotation, y_rotation, z_rotation):
    """ Compute local frame associated to chessboard

    Args:
     - x (float): x position of chess in world frame
     - y (float): y position of chess in world frame
     - z (float): z position of chess in world frame
     - x_rotation (float): elevation angle around local x axis
     - y_rotation (float): rotation angle around local y axis
     - z_rotation (float): rotation angle around local z axis

    """
    origin = [x, y, z]

    mat_rot_x = rotation_matrix(x_rotation, x_axis)
    mat_rot_y = rotation_matrix(y_rotation, y_axis)
    mat_rot_z = rotation_matrix(z_rotation, z_axis)

    rot = concatenate_matrices(mat_rot_x, mat_rot_y, mat_rot_z)

    return Frame(rot[:3, :3].T, origin)


def camera_frame_2(dist, x_rotation, y_rotation, z_rotation, zero_offset, alpha):
    """ Compute local frame associated to the camera

    Args:
     - dist (float): distance of camera to rotation axis
     - offset (float): offset angle in radians for rotation
     - z (float): z position of cam in world frame when alpha=0

     - x_rotation (float): elevation angle of camera (around local x axis)
     - y_rotation (float): azimuth angle of camera (around local y axis)
     - z_rotation (float): tilt angle of camera (around local z axis)
     - offset_angle (float): rotation offset around z_axis in world frame
                              (i.e. rotation angle of camera when alpha=0)
     - alpha (float): rotation angle around z_axis in world frame
    """
    origin = [dist * cos(alpha + zero_offset),
              dist * sin(alpha + zero_offset),
              0]

    shift = rotation_matrix(-numpy.pi / 2., x_axis)
    mat_rot_x = rotation_matrix(x_rotation, x_axis)
    mat_rot_y = rotation_matrix(-alpha + y_rotation, y_axis)
    mat_rot_z = rotation_matrix(z_rotation, z_axis)

    rot = concatenate_matrices(shift, mat_rot_y, mat_rot_x, mat_rot_z)
    return Frame(rot[:3, :3].T, origin)

