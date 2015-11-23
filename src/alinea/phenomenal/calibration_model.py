# -*- python -*-
#
#       calibration_model.py :
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
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
""" This module contains a calibration model for phenoarch experiment
where a chessboard is rotating instead of a plant in a picture cabin.
"""
#       ========================================================================
#       External Import

import json
from math import radians, cos, pi, sin

import numpy
import numpy.random
import scipy.optimize













#       ========================================================================
#       Local Import

from frame import Frame, x_axis, y_axis, z_axis
from transformations import concatenate_matrices, rotation_matrix
from camera import Camera

#       ========================================================================
#       Code


class ChessboardModelParameters(object):
    def __init__(self):
        self._x = None
        self._y = None
        self._z = None
        self._elev = None
        self._tilt = None

    def random_initialization(self):
        pi2 = 2 * numpy.pi
        self._x = numpy.random.uniform(-1000, 1000)
        self._y = numpy.random.uniform(-1000, 1000)
        self._z = numpy.random.uniform(-1000, 1000)
        self._elev = numpy.random.uniform(0, pi2)
        self._tilt = numpy.random.uniform(0, pi2)

    def get_parameters(self):
        return [self._x, self._y, self._z, self._elev, self._tilt]

    def set_parameters(self, x, y, z, elev, tilt):
        self._x = x
        self._y = y
        self._z = z
        self._elev = elev
        self._tilt = tilt

    def __str__(self):
        description = 'Chessboard :\n'
        description += 'Position x : ' + str(self._x) + '\n'
        description += 'Position y : ' + str(self._y) + '\n'
        description += 'Position z : ' + str(self._z) + '\n'
        description += 'Angle elev (rad): ' + str(self._elev) + '\n'
        description += 'Angle tilt (rad): ' + str(self._tilt) + '\n'
        return description

    def write(self, file_path):
        save_class = dict()
        save_class['x'] = self._x
        save_class['y'] = self._y
        save_class['z'] = self._z
        save_class['elev'] = self._elev
        save_class['tilt'] = self._tilt

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
                                                       save_class['elev'],
                                                       save_class['tilt'])

        return chessboard_model_parameters


class CameraModelParameters(object):
    def __init__(self, size_image):
        self._size_image = size_image

        self._focal_length_x = None
        self._focal_length_y = None
        self._distance_to_rotation_axe = None
        self._zero_offset = None
        self._angle_offset = None
        self._elev = None
        self._tilt = None

    def get_parameters(self):
        return [self._size_image,
                self._focal_length_x,
                self._focal_length_y,
                self._distance_to_rotation_axe,
                self._zero_offset,
                self._angle_offset,
                self._elev,
                self._tilt]

    def set_parameters(self,
                       focal_length_x,
                       focal_length_y,
                       distance_to_rotation_axe,
                       zero_offset,
                       angle_offset,
                       elev,
                       tilt):

        self._focal_length_x = focal_length_x
        self._focal_length_y = focal_length_y
        self._distance_to_rotation_axe = distance_to_rotation_axe
        self._zero_offset = zero_offset
        self._angle_offset = angle_offset
        self._elev = elev
        self._tilt = tilt

    def __str__(self):
        description = 'Camera :\n'
        description += 'Size image : ' + str(self._size_image) + '\n'
        description += 'Focal X : ' + str(self._focal_length_x) + '\n'
        description += 'Focal Y : ' + str(self._focal_length_y) + '\n'
        description += 'Distance camera : '
        description += str(self._distance_to_rotation_axe) + '\n'
        description += 'Offset : ' + str(self._zero_offset) + '\n'
        description += 'Offset angle : ' + str(self._angle_offset) + '\n'
        description += 'Elev Cam : ' + str(self._elev) + '\n'
        description += 'Tilt Cam : ' + str(self._tilt) + '\n'
        return description

    def random_initialization(self):
        pi2 = 2 * numpy.pi
        self._focal_length_x = numpy.random.uniform(1000, 10000)
        self._focal_length_y = numpy.random.uniform(1000, 10000)
        self._distance_to_rotation_axe = numpy.random.uniform(1000, 10000)
        self._zero_offset = numpy.random.uniform(0, pi2)
        self._angle_offset = 0.0
        self._elev = 0.0
        self._tilt = 0.0

    def write(self, file_path):
        save_class = dict()
        save_class['size_image'] = self._size_image
        save_class['focal_length_x'] = self._focal_length_x
        save_class['focal_length_y'] = self._focal_length_y
        save_class['distance_to_rotation_axe'] = self._distance_to_rotation_axe
        save_class['zero_offset'] = self._zero_offset
        save_class['angle_offset'] = self._angle_offset
        save_class['elev'] = self._elev
        save_class['tilt'] = self._tilt

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
                save_class['angle_offset'],
                save_class['elev'],
                save_class['tilt'])

        return camera_model_parameters


class ModelProjection(object):
    def __init__(self, camera_model_parameters):

        parameters = camera_model_parameters.get_parameters()

        size_image = parameters[0]
        focal_length_x = parameters[1]
        focal_length_y = parameters[2]
        distance_to_rotation_axe = parameters[3]
        zero_offset = parameters[4]
        angle_offset = parameters[5]
        elev = parameters[6]
        tilt = parameters[7]

        self._camera = Camera(size_image, (focal_length_x, focal_length_y))

        self._frame = dict()
        for angle in range(0, 360, 1):
            self._frame[angle] = camera_frame(
                distance_to_rotation_axe,
                zero_offset,
                elev,
                tilt,
                angle_offset,
                radians(angle))

    def project_point(self, point, angle):
        return self._camera.pixel_coordinates(
            self._frame[angle].local_point(point))


class Calibration(object):
    def __init__(self, chessboards, size_image, verbose=False):
        self._size_image = size_image
        self._verbose = verbose

        number_of_chessboard = len(chessboards)
        if number_of_chessboard == 1:
            chessboard = chessboards[0]

            # Compute number of reference from chessboard corners points
            self._number_ref = len(chessboard.corners_points)
            if self._verbose:
                print 'Number of ref points : ', self._number_ref

            self._chessboard_pts = chessboard.local_corners_position_3d()
            self._cv_pts = chessboard.corners_points.copy()
            for angle in self._cv_pts:
                self._cv_pts[angle] = self._cv_pts[angle][:, 0, :]

        elif number_of_chessboard == 2:
            chessboard_1 = chessboards[0]
            chessboard_2 = chessboards[0]

            self._number_ref = len(chessboard_1.corners_points) + len(
                chessboard_2.corners_points)
            if self._verbose:
                print 'Number of ref points : ', self._number_ref

            self._chessboard_pts_1 = chessboard_1.local_corners_position_3d()
            self._cv_pts_1 = chessboard_1.corners_points.copy()
            for angle in self._cv_pts_1:
                self._cv_pts_1[angle] = self._cv_pts_1[angle][:, 0, :]

            self._chessboard_pts_2 = chessboard_2.local_corners_position_3d()
            self._cv_pts_2 = chessboard_2.corners_points.copy()
            for angle in self._cv_pts_2:
                self._cv_pts_2[angle] = self._cv_pts_2[angle][:, 0, :]

    def fit_function_light(self, x0):
        err = 0
        fr_chess = chess_frame(*x0[0:5])
        cam = Camera(self._size_image, x0[5:7])
        dist_cam, offset, offset_angle = x0[7:10]

        chess_pts = map(lambda pt: fr_chess.global_point(pt),
                        self._chessboard_pts)

        for alpha, ref_pts in self._cv_pts.items():
            fr_cam = camera_frame_light(
                dist_cam, offset, offset_angle, radians(alpha))

            pts = map(lambda pt: cam.pixel_coordinates(fr_cam.local_point(pt)),
                      chess_pts)

            err += numpy.linalg.norm(numpy.array(pts) - ref_pts, axis=1).sum()

        if self._verbose:
            print err

        return err

    def fit_function(self, x0):
        err = 0
        fr_chess = chess_frame(*x0[0:5])
        cam = Camera(self._size_image, x0[5:7])
        dist_cam, offset, offset_angle = x0[7:10]
        elev_cam, tilt_cam, = x0[10:12]

        chess_pts = map(lambda pt: fr_chess.global_point(pt),
                        self._chessboard_pts)

        for alpha, ref_pts in self._cv_pts.items():
            fr_cam = camera_frame(dist_cam, offset,
                                  elev_cam, tilt_cam,
                                  offset_angle, radians(alpha))

            pts = map(lambda pt: cam.pixel_coordinates(fr_cam.local_point(pt)),
                      chess_pts)

            err += numpy.linalg.norm(numpy.array(pts) - ref_pts, axis=1).sum()

        if self._verbose:
            print err

        return err

    def first_guess_estimation(self,
                               chess_params,
                               cam_params,
                               number_of_repetition):
        final_guess = None
        min_err = float('inf')
        for i in range(number_of_repetition + 1):

            chess_params.random_initialization()
            cam_params.random_initialization()

            guess = list()
            guess[0:5] = chess_params.get_parameters()
            guess[5:10] = cam_params.get_parameters()[1:6]

            guess = scipy.optimize.minimize(
                self.fit_function_light, guess, method='BFGS').x

            for j in [3, 4, 8, 9]:
                guess[j] %= 2 * numpy.pi

            err = self.fit_function_light(guess)

            if err < min_err:
                min_err = err
                final_guess = guess

            if self._verbose:
                err = self.fit_function_light(guess)
                print 'Result : ', guess
                print 'Err : ', err / self._number_ref

        return final_guess

    def secondly_guess_estimation(self,
                                  cam_params,
                                  first_guess,
                                  number_of_repetition):

        guess = list()
        guess[0:10] = first_guess[0:10]
        guess[10:12] = cam_params.get_parameters()[6:8]

        guess = scipy.optimize.minimize(
                self.fit_function, guess, method='BFGS').x

        if self._verbose:
            err = self.fit_function(guess)
            print 'Result : ', guess
            print 'Err : ', err / self._number_ref

        guess = scipy.optimize.basinhopping(
            self.fit_function,
            guess,
            minimizer_kwargs={"method": "BFGS"},
            T=1.0,
            niter=number_of_repetition + 1).x

        for i in [3, 4, 8, 9, 10, 11]:
            guess[i] %= 2 * numpy.pi

        if self._verbose:
            err = self.fit_function(guess)
            print 'Result : ', guess
            print 'Err : ', err / self._number_ref

        return guess

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
        - 'guess' (): initial guess for calibration model
        """

        chess_params = ChessboardModelParameters()
        cam_params = CameraModelParameters(self._size_image)

        guess = self.first_guess_estimation(
            chess_params, cam_params, number_of_repetition)

        guess = self.secondly_guess_estimation(
            cam_params, guess, number_of_repetition)

        chess_params.set_parameters(*guess[0:5])
        cam_params.set_parameters(*guess[5:])

        if self._verbose:
            print chess_params
            print cam_params

        return cam_params, chess_params

    def fit_function_light_2(self, x0):
        err = list()
        fr_chess_1 = chess_frame(*x0[0:5])
        fr_chess_2 = chess_frame(*x0[5:10])

        cam = Camera(self._size_image, x0[10:12])
        dist_cam, offset, offset_angle = x0[12:15]

        for alpha, ref_pts in self._cv_pts_1.items():
            fr_cam = camera_frame_light(
                dist_cam, offset, offset_angle, radians(alpha))

            pts = [
                cam.pixel_coordinates(
                    fr_cam.local_point(
                        fr_chess_1.global_point(pt))) for pt in
                self._chessboard_pts_1]

            err.append(
                numpy.linalg.norm(numpy.array(pts) - ref_pts, axis=1).sum())

        for alpha, ref_pts in self._cv_pts_2.items():
            fr_cam = camera_frame_light(
                dist_cam, offset, offset_angle, radians(alpha))

            pts = [
                cam.pixel_coordinates(
                    fr_cam.local_point(
                        fr_chess_2.global_point(pt))) for pt in
                self._chessboard_pts_2]

            err.append(
                numpy.linalg.norm(numpy.array(pts) - ref_pts, axis=1).sum())

        sum_err = sum(err)
        if self._verbose:
            print sum_err
        return sum_err

    def fit_function_2(self, x0):
        err = list()
        fr_chess_1 = chess_frame(*x0[0:5])
        fr_chess_2 = chess_frame(*x0[5:10])

        cam = Camera(self._size_image, x0[10:12])
        dist_cam, offset, offset_angle = x0[12:15]
        elev_cam, tilt_cam = x0[15:18]

        for alpha, ref_pts in self._cv_pts_1.items():
            fr_cam = camera_frame(
                dist_cam, offset,
                elev_cam, tilt_cam,
                offset_angle, radians(alpha))

            pts = [
                cam.pixel_coordinates(
                    fr_cam.local_point(
                        fr_chess_1.global_point(pt))) for pt in
                self._chessboard_pts_1]

            err.append(
                numpy.linalg.norm(numpy.array(pts) - ref_pts, axis=1).sum())

        for alpha, ref_pts in self._cv_pts_2.items():
            fr_cam = camera_frame(
                dist_cam, offset,
                elev_cam, tilt_cam,
                offset_angle, radians(alpha))

            pts = [
                cam.pixel_coordinates(
                    fr_cam.local_point(
                        fr_chess_2.global_point(pt))) for pt in
                self._chessboard_pts_2]

            err.append(
                numpy.linalg.norm(numpy.array(pts) - ref_pts, axis=1).sum())

        sum_err = sum(err)
        if self._verbose:
            print sum_err
        return sum_err

    def first_guess_estimation_2(self,
                                 chess_params_1,
                                 chess_params_2,
                                 cam_params,
                                 number_of_repetition):
        final_guess = None
        min_err = float('inf')
        for i in range(number_of_repetition + 1):

            chess_params_1.random_initialization()
            chess_params_2.random_initialization()
            cam_params.random_initialization()

            guess = list()
            guess[0:5] = chess_params_1.get_parameters()
            guess[5:10] = chess_params_2.get_parameters()
            guess[10:15] = cam_params.get_parameters()[1:6]

            guess = scipy.optimize.minimize(
                self.fit_function_light_2, guess, method='BFGS').x

            for j in [3, 4, 8, 9, 13, 14]:
                guess[j] %= 2 * numpy.pi

            err = self.fit_function_light_2(guess)

            if err < min_err:
                min_err = err
                final_guess = guess

            if self._verbose:
                err = self.fit_function_light_2(guess)
                print 'Result : ', guess
                print 'Err : ', err / self._number_ref

        return final_guess

    def secondly_guess_estimation_2(self,
                                    cam_params,
                                    first_guess,
                                    number_of_repetition):

        guess = list()
        guess[0:15] = first_guess[0:15]
        guess[15:17] = cam_params.get_parameters()[6:8]

        guess = scipy.optimize.minimize(
            self.fit_function_2, guess, method='BFGS').x

        if self._verbose:
            err = self.fit_function_2(guess)
            print 'Result : ', guess
            print 'Err : ', err / self._number_ref

        guess = scipy.optimize.basinhopping(
            self.fit_function_2,
            guess,
            minimizer_kwargs={"method": "BFGS"},
            T=1.0,
            niter=number_of_repetition + 1).x

        for i in [3, 4, 8, 9, 13, 14, 15, 16]:
            guess[i] %= 2 * numpy.pi

        if self._verbose:
            err = self.fit_function_2(guess)
            print 'Result : ', guess
            print 'Err : ', err / self._number_ref

        return guess

    def find_model_parameters_2_chess(self, number_of_repetition=1):
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

        chess_params_1 = ChessboardModelParameters()
        chess_params_2 = ChessboardModelParameters()
        cam_params = CameraModelParameters(self._size_image)

        guess = self.first_guess_estimation_2(
            chess_params_1, chess_params_2, cam_params, number_of_repetition)

        guess = self.secondly_guess_estimation_2(
            cam_params, guess, number_of_repetition)

        chess_params_1.set_parameters(*guess[0:5])
        chess_params_1.set_parameters(*guess[5:10])
        cam_params.set_parameters(*guess[10:])

        if self._verbose:
            print chess_params_1
            print chess_params_2
            print cam_params

        return cam_params, chess_params_1, chess_params_2

    def find_model_parameters_2(self,
                                chessboard_1,
                                chessboard_2,
                                size_image,
                                verbose=False):
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

        # Number of image used to fit factor calibration
        number_ref = (len(chessboard_1.corners_points) +
                      len(chessboard_2.corners_points))
        if verbose:
            print 'Number of ref points : ', number_ref

        # Generate local position of corner for each chessboard according
        # world chessboard representation
        local_corners_chessboard_1 = chessboard_1.local_corners_position_3d()
        local_corners_chessboard_2 = chessboard_2.local_corners_position_3d()

        # Convert chessboard corners position to 2d array
        cv_pts_1 = chessboard_1.corners_points.copy()
        for angle in cv_pts_1:
            cv_pts_1[angle] = cv_pts_1[angle][:, 0, :]

        # Convert chessboard corners position to 2d array
        cv_pts_2 = chessboard_2.corners_points.copy()
        for angle in cv_pts_2:
            cv_pts_2[angle] = cv_pts_2[angle][:, 0, :]

        def fit_function_light(x0):
            err = list()
            fr_chess_1 = chess_frame(*x0[0:5])
            fr_chess_2 = chess_frame(*x0[5:10])

            cam = Camera(size_image, x0[10:12])
            dist_cam, offset, offset_angle = x0[12:15]

            for alpha, ref_pts in cv_pts_1.items():
                fr_cam = camera_frame(dist_cam, offset,
                                      0, 0, 0,
                                      offset_angle, radians(alpha))

                pts = [
                    cam.pixel_coordinates(
                        fr_cam.local_point(
                            fr_chess_1.global_point(pt))) for pt in
                    local_corners_chessboard_1]

                err.append(
                    numpy.linalg.norm(numpy.array(pts) - ref_pts, axis=1).sum())

            for alpha, ref_pts in cv_pts_2.items():
                fr_cam = camera_frame(dist_cam, offset,
                                      0, 0, 0,
                                      offset_angle, radians(alpha))

                pts = [
                    cam.pixel_coordinates(
                        fr_cam.local_point(
                            fr_chess_2.global_point(pt))) for pt in
                    local_corners_chessboard_2]

                err.append(
                    numpy.linalg.norm(numpy.array(pts) - ref_pts, axis=1).sum())

            print sum(err)
            return err

        def sum_fit_function_light(x0):
            return sum(fit_function_light(x0))

        def fit_function(x0):
            err = list()
            fr_chess_1 = chess_frame(*x0[0:5])
            fr_chess_2 = chess_frame(*x0[5:10])

            cam = Camera(size_image, x0[10:12])
            dist_cam, offset, azim_cam, elev_cam, \
            tilt_cam, offset_angle = x0[12:18]

            for alpha, ref_pts in cv_pts_1.items():
                fr_cam = camera_frame(dist_cam, offset,
                                      azim_cam, elev_cam, tilt_cam,
                                      offset_angle, radians(alpha))

                pts = [
                    cam.pixel_coordinates(
                        fr_cam.local_point(
                            fr_chess_1.global_point(pt))) for pt in
                    local_corners_chessboard_1]

                err.append(
                    numpy.linalg.norm(numpy.array(pts) - ref_pts, axis=1).sum())

            for alpha, ref_pts in cv_pts_2.items():
                fr_cam = camera_frame(dist_cam, offset,
                                      0, 0, 0,
                                      offset_angle, radians(alpha))

                pts = [
                    cam.pixel_coordinates(
                        fr_cam.local_point(
                            fr_chess_2.global_point(pt))) for pt in
                    local_corners_chessboard_2]

                err.append(
                    numpy.linalg.norm(numpy.array(pts) - ref_pts, axis=1).sum())

            print sum(err)
            return err

        def sum_fit_function(x0):
            return sum(fit_function(x0))

        pi2 = 2 * numpy.pi

        guess = [numpy.random.uniform(-1000, 1000),
                 numpy.random.uniform(-1000, 1000),
                 numpy.random.uniform(-1000, 1000),
                 numpy.random.uniform(-pi2, pi2),
                 numpy.random.uniform(-pi2, pi2),

                 numpy.random.uniform(-1000, 1000),
                 numpy.random.uniform(-1000, 1000),
                 numpy.random.uniform(-1000, 1000),
                 numpy.random.uniform(-pi2, pi2),
                 numpy.random.uniform(-pi2, pi2),

                 numpy.random.uniform(1000, 10000),
                 numpy.random.uniform(1000, 10000),
                 numpy.random.uniform(1000, 10000),
                 numpy.random.uniform(-pi2, pi2),
                 numpy.random.uniform(-pi2, pi2)]

        bounds = [(-1000, 1000),
                  (-1000, 1000),
                  (-1000, 1000),
                  (-pi2, pi2),
                  (-pi2, pi2),

                  (-1000, 1000),
                  (-1000, 1000),
                  (-1000, 1000),
                  (-pi2, pi2),
                  (-pi2, pi2),

                  (1000, 10000),
                  (1000, 10000),
                  (1000, 10000),
                  (-pi2, pi2),
                  (-pi2, pi2)]

        minimizer_kwargs = {"method": "BFGS"}

        res = scipy.optimize.basinhopping(
            sum_fit_function_light,
            guess,
            minimizer_kwargs=minimizer_kwargs,
            T=2.0,
            niter=5)

        guess = res.x

        for i in [3, 4, 8, 9, 13, 14]:
            guess[i] = guess[i] % pi2

        if verbose:
            err = sum_fit_function_light(guess)
            print 'Result : ', guess
            print 'Err : ', err / number_ref

        g = list()
        g[0:14] = guess[0:14]
        g[14:18] = [0, 0, 0, guess[14]]
        guess = g

        minimizer_kwargs = {"method": "BFGS"}

        res = scipy.optimize.basinhopping(
            sum_fit_function,
            guess,
            minimizer_kwargs=minimizer_kwargs,
            T=2.0,
            niter=5)

        guess = res.x

        for i in [3, 4, 8, 9, 13, 14]:
            guess[i] = guess[i] % pi2

        if verbose:
            err = sum_fit_function(guess)
            print 'Result : ', guess
            print 'Err : ', err / number_ref


        chess_x, chess_y, chess_z, chess_elev, chess_tilt = guess[0:5]
        sca_x, sca_y, = guess[10:12]
        dist_cam, offset, azim_cam, elev_cam, tilt_cam, offset_angle = \
            guess[12:18]

        self._sca_x = sca_x
        self._sca_y = sca_y
        self._dist_cam = dist_cam
        self._offset = offset
        self._azim_cam = azim_cam
        self._elev_cam = elev_cam
        self._tilt_cam = tilt_cam
        self._offset_angle = offset_angle

        self._chessboard_x = chess_x
        self._chessboard_y = chess_y
        self._chessboard_z = chess_z
        self._chessboard_elev = chess_elev
        self._chessboard_tilt = chess_tilt

        self._size_image = size_image

        self._camera = Camera(size_image, (self._sca_x, self._sca_y))
        self.initialize_camera_frame()


def chess_frame(x, y, z, elev, tilt):
    """ Compute local frame associated to chessboard

    Args:
     - x (float): x position of chess in world frame
     - y (float): y position of chess in world frame
     - z (float): z position of chess in world frame
     - elev (float): elevation angle around local x axis
     - tilt (float): rotation angle around local z axis
    """
    origin = [x, y, z]
    mat_elev = rotation_matrix(elev, x_axis)
    mat_tilt = rotation_matrix(tilt, z_axis)

    rot = concatenate_matrices(mat_elev, mat_tilt)

    return Frame(rot[:3, :3].T, origin)


def camera_frame(dist, offset, elev, tilt, offset_angle, alpha):
    """ Compute local frame associated to the camera

    Args:
     - dist (float): distance of camera to rotation axis
     - offset (float): offset angle in radians for rotation
     - z (float): z position of cam in world frame when alpha=0
     - azim (float): azimuth angle of camera (around local y axis)
     - elev (float): elevation angle of camera (around local x axis)
     - tilt (float): tilt angle of camera (around local z axis)
     - offset_angle (float): rotation offset around z_axis in world frame
                              (i.e. rotation angle of camera when alpha=0)
     - alpha (float): rotation angle around z_axis in world frame
    """
    origin = (dist * cos(alpha + offset),
              dist * sin(alpha + offset),
              0.0)

    shift = rotation_matrix(-pi / 2., x_axis)
    rot_y = rotation_matrix(-alpha + offset_angle, y_axis)

    mat_elev = rotation_matrix(elev, x_axis)
    mat_tilt = rotation_matrix(tilt, z_axis)

    rot = concatenate_matrices(shift, rot_y, mat_elev, mat_tilt)

    return Frame(rot[:3, :3].T, origin)


def camera_frame_light(dist, offset, offset_angle, alpha):
    """ Compute local frame associated to the camera

    Args:
     - dist (float): distance of camera to rotation axis
     - offset (float): offset angle in radians for rotation
     - z (float): z position of cam in world frame when alpha=0
     - azim (float): azimuth angle of camera (around local y axis)
     - elev (float): elevation angle of camera (around local x axis)
     - tilt (float): tilt angle of camera (around local z axis)
     - offset_angle (float): rotation offset around z_axis in world frame
                              (i.e. rotation angle of camera when alpha=0)
     - alpha (float): rotation angle around z_axis in world frame
    """
    origin = (dist * cos(alpha + offset),
              dist * sin(alpha + offset),
              0.0)

    shift = rotation_matrix(-pi / 2., x_axis)
    rot_y = rotation_matrix(-alpha + offset_angle, y_axis)

    rot = concatenate_matrices(shift, rot_y)

    return Frame(rot[:3, :3].T, origin)

#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    do_nothing = None
