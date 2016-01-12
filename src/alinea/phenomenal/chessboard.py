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
import json

import alinea.phenomenal.calibration_model
# ==============================================================================


class Chessboard(object):
    def __init__(self, square_size, shape):

        # Initialization
        self.square_size = square_size
        self.shape = shape
        self.corners_points = dict()

    def __str__(self):
        my_str = ''
        my_str += 'Chessboard Object Values :\n'
        my_str += 'Square size (mm): ' + str(self.square_size) + '\n'
        my_str += 'Shape : ' + str(self.shape) + '\n'

        for angle in self.corners_points:
            my_str += str(angle) + '\n'
            my_str += str(self.corners_points[angle]) + '\n'

        return my_str

    def local_corners_position_3d(self):
        square_size = self.square_size
        width, height = self.shape

        chessboard_pts = []
        for j in range(height):
            for i in range(width):
                v = numpy.array([i * square_size, j * square_size, 0.])
                chessboard_pts.append(v)

        return chessboard_pts

    def global_corners_position_3d(self, x, y, z, elev, tilt, azim):

        chessboard_pts = self.local_corners_position_3d()

        fr_chess = alinea.phenomenal.calibration_model.chess_frame(
            x, y, z, elev, tilt, azim)

        pts = [fr_chess.global_point(pt) for pt in chessboard_pts]

        return pts

    def find_corners(self, image):
        try:
            found, corners = cv2.findChessboardCorners(
                image,
                tuple(self.shape),
                flags=cv2.CALIB_CB_ADAPTIVE_THRESH +
                      cv2.CALIB_CB_NORMALIZE_IMAGE)

            if found:
                cv2.cornerSubPix(image, corners, (11, 11), (-1, -1),
                                 criteria=(cv2.TERM_CRITERIA_EPS +
                                           cv2.TERM_CRITERIA_MAX_ITER,
                                           30,
                                           0.001))
            else:
                print "Error : Corners not find"
                return None

        except cv2.error:
            print "Error : cv2, get_corners, calibration.py"
            return None

        return corners

    def find_and_add_corners(self, angle, image):
        corners_points = self.find_corners(image)
        if corners_points is not None:
            self.corners_points[angle] = corners_points

    def write(self, file_path):

        # Convert to json format
        for angle in self.corners_points:
            self.corners_points[angle] = self.corners_points[angle].tolist()

        save_class = dict()
        save_class['square_size'] = self.square_size
        save_class['shape'] = self.shape
        save_class['corners_points'] = self.corners_points

        with open(file_path + '.json', 'w') as output_file:
            json.dump(save_class, output_file)

    @staticmethod
    def read(file_path):

        with open(file_path + '.json', 'r') as input_file:
            save_class = json.load(input_file)

            square_size = float(save_class['square_size'])
            shape = [int(val) for val in save_class['shape']]

            chessboard = Chessboard(square_size, shape)

            corners_points = save_class['corners_points']

            # Convert to numpy format
            for angle in corners_points:
                chessboard.corners_points[float(angle)] = numpy.array(
                    corners_points[angle]).astype(numpy.float)

        return chessboard
