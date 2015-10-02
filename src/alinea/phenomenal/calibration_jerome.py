# -*- python -*-
#
#       calibration_jerome.py : 
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
import pickle
import numpy
from math import radians
from scipy.optimize import leastsq

#       ========================================================================
#       Local Import
import openalea.deploy.shared_data
import alinea.phenomenal

from calibration_model import camera_frame, chess_corners, chess_frame
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

    def write_calibration(self, filename):
        cal_params = (self._sca_x, self._sca_y,
                      self._dist_cam, self._offset, self._z_cam,
                      self._azim_cam, self._elev_cam, self._tilt_cam,
                      self._offset_angle)
        with open(filename + '.pickle', 'wb') as handle:
            pickle.dump(cal_params, handle)

    @staticmethod
    def read_calibration(filename, file_is_in_share_directory=True):

        if file_is_in_share_directory is True:
            share_data_directory = openalea.deploy.shared_data.shared_data(
                alinea.phenomenal)

            file_path = share_data_directory + filename + '.pickle'
        else:
            file_path = filename + '.pickle'


        with open(file_path, 'rb') as handle:
            params = pickle.load(handle)
            print params
            sca_x, sca_y = params[0:2]
            dist_cam, offset, z_cam = params[2:5]
            azim_cam, elev_cam, tilt_cam, offset_angle = params[5:9]

            cal = Calibration()
            cal._sca_x = sca_x
            cal._sca_y = sca_y
            cal._dist_cam = dist_cam
            cal._offset = offset
            cal._z_cam = z_cam
            cal._azim_cam = azim_cam
            cal._elev_cam = elev_cam
            cal._tilt_cam = tilt_cam
            cal._offset_angle = offset_angle
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
                pts = [project(pt, fr_chess, fr_cam, cam) for pt in
                       chessboard_pts]

                err.append(
                    numpy.linalg.norm(numpy.array(pts) - ref_pts, axis=1).sum())

            print sum(err)
            return err

        # print fit(guess)
        res = leastsq(fit, guess, maxfev=5000)

        with open("fitted - step.pkl", 'wb') as f:
            pickle.dump(res[0], f)

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


def project(pt, fr_chess, fr_cam, cam):
    return cam.pixel_coordinates(fr_cam.local_point(fr_chess.global_point(pt)))


def find_calibration_model_parameters(chessboard_ref, chessboard_corners, guess):
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
        dist_cam, offset, z_cam, azim_cam, elev_cam, tilt_cam, offset_angle = params[7:14]

        for alpha, ref_pts in cv_pts.items():
            fr_cam = camera_frame(dist_cam, offset, z_cam, azim_cam, elev_cam, tilt_cam, offset_angle, radians(alpha))
            pts = [project(pt, fr_chess, fr_cam, cam) for pt in chessboard_pts]

            err.append(numpy.linalg.norm(numpy.array(pts) - ref_pts, axis=1).sum())

        print sum(err)
        return err

    # print fit(guess)
    res = leastsq(fit, guess, maxfev=5000)

    with open("fitted - step.pkl", 'wb') as f:
        pickle.dump(res[0], f)

    sca_x, sca_y, = res[0][5:7]
    dist_cam, offset, z_cam, azim_cam, elev_cam, tilt_cam, offset_angle = res[0][7:14]

    cal = Calibration()
    cal._sca_x = sca_x
    cal._sca_y = sca_y
    cal._dist_cam = dist_cam
    cal._offset = offset
    cal._z_cam = z_cam
    cal._azim_cam = azim_cam
    cal._elev_cam = elev_cam
    cal._tilt_cam = tilt_cam
    cal._offset_angle = offset_angle

    cal.initialize_camera_frame()

    return cal


def plot_calibration(chessboard, cv_pts, guess, alpha):
    import matplotlib.pyplot as plt

    img = plt.imread('../../local/data/CHESSBOARD/2013-07-11 15_49_42vis_sv%.3d.png' % alpha)
    plt.imshow(img)
    print cv_pts[alpha].shape

    plt.plot(cv_pts[alpha][:,0], cv_pts[alpha][:,1], 'r+')
    plt.show()


#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    do_nothing = None