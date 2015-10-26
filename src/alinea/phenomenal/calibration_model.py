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
        self._sca_x = None
        self._sca_y = None
        self._dist_cam = None
        self._offset = None
        self._z_cam = None
        self._azim_cam = None
        self._elev_cam = None
        self._tilt_cam = None
        self._offset_angle = None
        self._camera = None

    def __getitem__(self, alpha):
        cam = Camera((2056, 2454), (self._sca_x, self._sca_y))

        fr = camera_frame(self._dist_cam, self._offset, self._z_cam,
                          self._azim_cam, self._elev_cam, self._tilt_cam,
                          self._offset_angle, radians(alpha))

        return cam, fr

    def initialize_camera_frame(self):

        self.frame = dict()

        for angle in range(0, 360, 1):
            self.frame[angle] = camera_frame(
                self._dist_cam,
                self._offset,
                self._z_cam,
                self._azim_cam,
                self._elev_cam,
                self._tilt_cam,
                self._offset_angle,
                radians(angle))

    def project_point(self, point, angle):
        return self._camera.pixel_coordinates(
            self.frame[angle].local_point(point))

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
            f.write('%f\n' % self._z_cam)
            f.write('%f\n' % self._azim_cam)
            f.write('%f\n' % self._elev_cam)
            f.write('%f\n' % self._tilt_cam)
            f.write('%f\n' % self._offset_angle)
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
            cal._z_cam = float(f.readline())
            cal._azim_cam = float(f.readline())
            cal._elev_cam = float(f.readline())
            cal._tilt_cam = float(f.readline())
            cal._offset_angle = float(f.readline())

        f.close()

        cal._camera = Camera((2056, 2454), (cal._sca_x, cal._sca_y))
        cal.initialize_camera_frame()

        return cal

    def print_value(self):
        print self._sca_x
        print self._sca_y
        print self._dist_cam
        print self._offset
        print self._z_cam
        print self._azim_cam
        print self._elev_cam
        print self._tilt_cam
        print self._offset_angle
        print self._camera

    def find_model_parameters(self,
                              chessboard_ref,
                              chessboard_corners,
                              guess):
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
        img_size = (2056, 2454)  # TODO: GRUUIK hardcoded

        chessboard_pts = chess_corners(chessboard_ref)
        cv_pts = chessboard_corners

        print " fit model on computed points"

        def fit(params):
            err = []
            fr_chess = chess_frame(*params[0:5])
            cam = Camera(img_size, params[5:7])
            dist_cam, offset, z_cam, azim_cam, elev_cam, \
            tilt_cam, offset_angle = params[7:14]

            for alpha, ref_pts in cv_pts.items():
                fr_cam = camera_frame(dist_cam, offset, z_cam, azim_cam,
                                      elev_cam, tilt_cam, offset_angle,
                                      radians(alpha))

                pts = [
                    cam.pixel_coordinates(
                        fr_cam.local_point(
                            fr_chess.global_point(pt))) for pt in
                    chessboard_pts]

                err.append(
                    numpy.linalg.norm(numpy.array(pts) - ref_pts, axis=1).sum())

            print sum(err)
            return err

        def fit_2(params):
            err = []
            fr_chess = chess_frame(*params[0:5])
            cam = Camera(img_size, params[5:7])
            dist_cam, offset, z_cam, azim_cam, elev_cam, \
            tilt_cam, offset_angle = params[7:14]

            for alpha, ref_pts in cv_pts.items():
                fr_cam = camera_frame(dist_cam, offset, z_cam, azim_cam,
                                      elev_cam, tilt_cam, offset_angle,
                                      radians(alpha))

                pts = [
                    cam.pixel_coordinates(
                        fr_cam.local_point(
                            fr_chess.global_point(pt))) for pt in
                    chessboard_pts]

                err.append(
                    numpy.linalg.norm(numpy.array(pts) - ref_pts, axis=1).sum())

            err = sum(err)
            print err
            return err

        if guess is None:

            pi = numpy.pi

            bounds = [(-200, -1),
                      (-200, -1),
                      (500, 1250),
                      (-pi, 0),
                      (0, pi),
                      (3000, 4500),
                      (3000, 4500),
                      (4000, 6000),
                      (-pi, 0),
                      (500, 1250),
                      (0, pi),
                      (0, pi),
                      (-pi, 0),
                      (0, pi)]

            # res = scipy.optimize.differential_evolution(
            #     fit_2,
            #     bounds,
            #     strategy='best1bin',
            #     init='latinhypercube',
            #     tol=0.1,
            #     popsize=10)
            #
            # print res

            guess = numpy.array([
                numpy.random.uniform(-200, 0),
                numpy.random.uniform(-200, 0),
                numpy.random.uniform(500, 1250), # 50cm to 1.5m
                numpy.random.uniform(-pi, 0),
                numpy.random.uniform(0, pi),

                numpy.random.uniform(3000, 4500),
                numpy.random.uniform(3000, 4500),

                numpy.random.uniform(4000, 6000),
                numpy.random.uniform(-pi, 0),
                numpy.random.uniform(100, 1250),

                numpy.random.uniform(0, pi),
                numpy.random.uniform(0, pi),
                numpy.random.uniform(-pi, 0),
                numpy.random.uniform(0, pi)])

            # guess = numpy.array([
            #     -150,
            #     -150,
            #     1000, # 50cm to 1.5m
            #     0,
            #     0,
            #
            #     numpy.random.uniform(3000, 4500),
            #     numpy.random.uniform(3000, 4500),
            #
            #     numpy.random.uniform(4000, 6000),
            #
            #     numpy.random.uniform(-pi, 0),
            #     numpy.random.uniform(100, 1250),
            #
            #     numpy.random.uniform(0, pi),
            #     numpy.random.uniform(0, pi),
            #     numpy.random.uniform(-pi, 0),
            #     numpy.random.uniform(0, pi)])



            # guess = numpy.array([-100.0, -100.0, 750.0,
            #                      0.0, 0.0,
            #                      4000.0, 4000.0,
            #                      5053.0, 0.0, 500.0,
            #                      0.0, 0.0,
            #                      0.0, 0.0])

            minimizer_kwargs = dict(method="L-BFGS-B", bounds=bounds)

            res = scipy.optimize.basinhopping(
                fit_2,
                guess,
                T=2.,
                niter=20,
                minimizer_kwargs=minimizer_kwargs)

            print res
            print res.x
            guess = res.x

            # res = leastsq(fit, guess, maxfev=2000)
            #
            # guess = res[0]

        # print fit(guess)
        res = leastsq(fit, guess, maxfev=500000)

        print res

        sca_x, sca_y, = res[0][5:7]
        dist_cam, offset, z_cam, azim_cam, elev_cam, tilt_cam, offset_angle = \
            res[0][7:14]

        self._sca_x = sca_x
        self._sca_y = sca_y
        self._dist_cam = dist_cam
        self._offset = offset
        self._z_cam = z_cam
        self._azim_cam = azim_cam
        self._elev_cam = elev_cam
        self._tilt_cam = tilt_cam
        self._offset_angle = offset_angle

        self._camera = Camera((2056, 2454), (self._sca_x, self._sca_y))
        self.initialize_camera_frame()


def chess_corners(chessboard):
    square_size = chessboard.square_size
    width, height = chessboard.shape

    chessboard_pts = []
    for j in range(height):
        for i in range(width):
            v = numpy.array([i * square_size, j * square_size, 0.])
            chessboard_pts.append(v)

    return chessboard_pts


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

    shift = rotation_matrix(-pi / 2., x_axis)

    mat_elev = rotation_matrix(elev, x_axis)
    mat_tilt = rotation_matrix(tilt, z_axis)
    rot = concatenate_matrices(shift, mat_elev, mat_tilt)

    return Frame(rot[:3, :3].T, origin)


def camera_frame(dist, offset, z, azim, elev, tilt, offset_angle, alpha):
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
              z)

    shift = rotation_matrix(-pi / 2., x_axis)
    rot_y = rotation_matrix(-alpha + offset_angle, y_axis)

    mat_azim = rotation_matrix(azim, y_axis)
    mat_elev = rotation_matrix(elev, x_axis)
    mat_tilt = rotation_matrix(tilt, z_axis)

    rot = concatenate_matrices(shift, rot_y, mat_azim, mat_elev, mat_tilt)

    return Frame(rot[:3, :3].T, origin)

#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    do_nothing = None