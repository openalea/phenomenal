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
from math import radians, cos, pi, sin

import numpy
import numpy.random

from scipy.optimize import leastsq
import scipy.optimize
import multiprocessing

#       ========================================================================
#       Local Import
import openalea.deploy.shared_data
import alinea.phenomenal

from frame import Frame, x_axis, y_axis, z_axis
from transformations import concatenate_matrices, rotation_matrix
from camera import Camera

#       ========================================================================
#       Code


class Calibration(object):
    def __init__(self):

        self._chessboard_x = None
        self._chessboard_y = None
        self._chessboard_z = None
        self._chessboard_elev = None
        self._chessboard_tilt = None

        self._sca_x = None
        self._sca_y = None
        self._dist_cam = None
        self._offset = None

        self._azim_cam = None
        self._elev_cam = None
        self._tilt_cam = None

        self._offset_angle = None
        self._camera = None
        self._frame = None

        self._size_image = None

    def initialize_camera_frame(self):

        self._frame = dict()

        for angle in range(0, 360, 1):
            self._frame[angle] = camera_frame(
                self._dist_cam,
                self._offset,
                self._azim_cam,
                self._elev_cam,
                self._tilt_cam,
                self._offset_angle,
                radians(angle))

    def project_point(self, point, angle):
        return self._camera.pixel_coordinates(
            self._frame[angle].local_point(point))

    def write_calibration(self, filename, write_in_share_directory=True):

        if write_in_share_directory is True:
            share_data_directory = openalea.deploy.shared_data.shared_data(
                alinea.phenomenal)

            file_path = share_data_directory / filename + '.calib'
        else:
            file_path = filename + '.calib'

        with open(file_path, 'w') as f:
            f.write('%f\n' % self._sca_x)
            f.write('%f\n' % self._sca_y)
            f.write('%f\n' % self._dist_cam)
            f.write('%f\n' % self._offset)
            f.write('%f\n' % self._azim_cam)
            f.write('%f\n' % self._elev_cam)
            f.write('%f\n' % self._tilt_cam)
            f.write('%f\n' % self._offset_angle)

            f.write('%f\n' % self._chessboard_x)
            f.write('%f\n' % self._chessboard_y)
            f.write('%f\n' % self._chessboard_z)
            f.write('%f\n' % self._chessboard_elev)
            f.write('%f\n' % self._chessboard_tilt)

            f.write('%f\n' % self._size_image[0])
            f.write('%f\n' % self._size_image[1])

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
            cal._sca_x = float(f.readline())
            cal._sca_y = float(f.readline())
            cal._dist_cam = float(f.readline())
            cal._offset = float(f.readline())
            cal._azim_cam = float(f.readline())
            cal._elev_cam = float(f.readline())
            cal._tilt_cam = float(f.readline())
            cal._offset_angle = float(f.readline())

            cal._chessboard_x = float(f.readline())
            cal._chessboard_y = float(f.readline())
            cal._chessboard_z = float(f.readline())
            cal._chessboard_elev = float(f.readline())
            cal._chessboard_tilt = float(f.readline())

            x = float(f.readline())
            y = float(f.readline())

            cal._size_image = (x, y)

        f.close()

        cal._camera = Camera(cal._size_image, (cal._sca_x, cal._sca_y))
        cal.initialize_camera_frame()

        return cal

    def __str__(self):

        description = 'Description :\n'
        description += 'Focal X : ' + str(self._sca_x) + '\n'
        description += 'Focal Y : ' + str(self._sca_y) + '\n'
        description += 'Distance camera : ' + str(self._dist_cam) + '\n'
        description += 'Offset : ' + str(self._offset) + '\n'
        description += 'Azim Cam : ' + str(self._azim_cam) + '\n'
        description += 'Elev Cam : ' + str(self._elev_cam) + '\n'
        description += 'Tilt Cam : ' + str(self._tilt_cam) + '\n'
        description += 'Offset Angle : ' + str(self._offset_angle) + '\n'

        description += 'Chessboard x : ' + str(self._chessboard_x) + '\n'
        description += 'Chessboard y : ' + str(self._chessboard_y) + '\n'
        description += 'Chessboard z : ' + str(self._chessboard_z) + '\n'
        description += 'Chessboard elev : ' + str(self._chessboard_elev) + '\n'
        description += 'Chessboard tilt : ' + str(self._chessboard_tilt) + '\n'

        return description

    def find_model_parameters(self, chessboard, size_image):
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

        number_ref = len(chessboard.corners_points)
        chessboard_pts = chessboard.local_corners_position_3d()

        cv_pts = chessboard.corners_points.copy()
        for angle in cv_pts:
            cv_pts[angle] = cv_pts[angle][:, 0, :]

        def fit_function_light(x0):
            err = list()
            fr_chess = chess_frame(*x0[0:5])
            cam = Camera(size_image, x0[5:7])
            dist_cam, offset, offset_angle = x0[7:10]

            for alpha, ref_pts in cv_pts.items():
                fr_cam = camera_frame(dist_cam, offset,
                                      0, 0, 0,
                                      offset_angle, radians(alpha))

                pts = [
                    cam.pixel_coordinates(
                        fr_cam.local_point(
                            fr_chess.global_point(pt))) for pt in
                    chessboard_pts]

                err.append(
                    numpy.linalg.norm(numpy.array(pts) - ref_pts, axis=1).sum())

            print sum(err)
            return err

        def sum_fit_function_light(x0):
            return sum(fit_function_light(x0))

        def fit_function(x0):
            err = []
            fr_chess = chess_frame(*x0[0:5])
            cam = Camera(size_image, x0[5:7])
            dist_cam, offset, azim_cam, elev_cam, \
            tilt_cam, offset_angle = x0[7:13]

            for alpha, ref_pts in cv_pts.items():
                fr_cam = camera_frame(dist_cam, offset,
                                      azim_cam, elev_cam, tilt_cam,
                                      offset_angle, radians(alpha))

                pts = [
                    cam.pixel_coordinates(
                        fr_cam.local_point(
                            fr_chess.global_point(pt))) for pt in
                    chessboard_pts]

                err.append(
                    numpy.linalg.norm(numpy.array(pts) - ref_pts, axis=1).sum())

            print sum(err)
            return err

        pi2 = 2 * numpy.pi
        bounds = [(-1000, 0),
                  (-1000, 0),
                  (-1000, 1000),
                  (-pi2, pi2),
                  (-pi2, pi2),

                  (1000, 10000),
                  (1000, 10000),
                  (1000, 10000),
                  (-pi2, pi2),
                  (-pi2, pi2)]

        popsize = max(60 - number_ref, 10)
        print popsize

        res = scipy.optimize.differential_evolution(
            sum_fit_function_light,
            bounds,
            strategy='best1bin',
            init='latinhypercube',
            tol=0.01,
            popsize=popsize,
            polish=True)

        guess = res.x
        print guess

        g = list()
        g[0:9] = guess[0:9]
        g[9:13] = [0, 0, 0, guess[9]]
        guess = g

        if number_ref >= 13:
            res = leastsq(fit_function, guess, maxfev=2000)
            guess = res[0]

            while sum(fit_function(guess)) > number_ref * 15:
                res = leastsq(fit_function, guess, maxfev=2000)
                guess = res[0]
                print guess

        chess_x, chess_y, chess_z, chess_elev, chess_tilt = guess[0:5]
        sca_x, sca_y, = guess[5:7]
        dist_cam, offset, azim_cam, elev_cam, tilt_cam, offset_angle = \
            guess[7:14]

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

    def find_model_parameters_2(self, chessboard_1, chessboard_2, size_image):
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

        popsize = max(60 - number_ref, 10)
        print popsize

        # res = scipy.optimize.differential_evolution(
        #     sum_fit_function_light,
        #     bounds,
        #     strategy='best1bin',
        #     init='latinhypercube',
        #     tol=0.01,
        #     popsize=popsize,
        #     polish=True)

        # minimizer_kwargs = {"method": "BFGS", "bounds": bounds}
        #
        # res = scipy.optimize.basinhopping(
        #     sum_fit_function_light,
        #     guess,
        #     minimizer_kwargs=minimizer_kwargs,
        #     T=2.0,
        #     stepsize=10,
        #     niter=10)

        res = scipy.optimize.minimize(
            sum_fit_function_light,
            guess,
            method="L-BFGS-B",
            bounds=bounds)

        guess = res.x
        print guess

        if number_ref >= 15:
            while sum_fit_function_light(guess) > number_ref * 15:
                res = leastsq(fit_function_light, guess, maxfev=10000)
                guess = res[0]
                print guess

        g = list()
        g[0:14] = guess[0:14]
        g[14:18] = [0, 0, 0, guess[17]]
        guess = g

        if number_ref >= 13:
            res = leastsq(fit_function, guess, maxfev=2000)
            guess = res[0]

            while sum(fit_function(guess)) > number_ref * 15:
                res = leastsq(fit_function, guess, maxfev=2000)
                guess = res[0]
                print guess

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

    # shift = rotation_matrix(-pi / 2., x_axis)

    mat_elev = rotation_matrix(elev, x_axis)
    mat_tilt = rotation_matrix(tilt, z_axis)
    # rot = concatenate_matrices(shift, mat_elev, mat_tilt)

    rot = concatenate_matrices(mat_elev, mat_tilt)

    return Frame(rot[:3, :3].T, origin)


def camera_frame(dist, offset, azim, elev, tilt, offset_angle, alpha):
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

    mat_azim = rotation_matrix(azim, y_axis)
    mat_elev = rotation_matrix(elev, x_axis)
    mat_tilt = rotation_matrix(tilt, z_axis)

    rot = concatenate_matrices(shift, rot_y, mat_azim, mat_elev, mat_tilt)

    # rot = concatenate_matrices(rot_y, mat_azim, mat_elev, mat_tilt)

    return Frame(rot[:3, :3].T, origin)

#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    do_nothing = None
