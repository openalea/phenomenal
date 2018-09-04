# -*- python -*-
#
#       Copyright INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
# ==============================================================================
from __future__ import division, print_function, absolute_import

import cv2
import numpy
import json
import collections
# ==============================================================================

__all__ = ["Target", "Chessboard"]

# ==============================================================================


class Target(object):

    def __init__(self):
        self.image_points = collections.defaultdict(dict)

    def add_image_points(self, camera_view, angle, image):
        pass

    def get_3d_local_points(self):
        pass

    def get_image_points(self):
        pass


class Chessboard(object):

    def __init__(self, square_size=50, shape=(7, 7)):
        self.square_size = square_size
        self.shape = shape
        self.image_points = collections.defaultdict(dict)

    def __str__(self):

        s = ("Chessboard Attributes :\n"
             "Square size (mm): {}\n"
             "Shape : {}\n".format(self.square_size, self.shape))

        return s

    def get_corners_local_3d(self):
        square_size = self.square_size
        width, height = self.shape

        corners_local_3d = list()
        for y in range(height):
            for x in range(width):
                v = numpy.array([x * square_size, y * square_size, 0.0])
                corners_local_3d.append(v)

        return corners_local_3d

    def get_corners_2d(self, id_camera):
        corners_2d = dict()
        for angle in self.image_points[id_camera]:
            corners_2d[angle] = self.image_points[id_camera][angle][:, 0, :]

        return corners_2d

    def detect_corners(self, id_camera, angle, image):
        """
        Detect chessboard corner in a image and save it in object with the
        id_camera and angle like keys.

        :param id_camera: id/label/name_key of the camera who take the picture
        :param angle: Angle of chessboard on the turnable platform
        :param image: numpy GRAYSCALE Image containing the chessboard target
        :return: True if chessboard corner are found otherwise False.
        """

        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        try:

            found, corners = cv2.findChessboardCorners(
                image,
                tuple(self.shape),
                flags=cv2.CALIB_CB_ADAPTIVE_THRESH +
                cv2.CALIB_CB_NORMALIZE_IMAGE)

            if found:

                cv2.cornerSubPix(
                    image, corners, (11, 11), (-1, -1),
                    criteria=(cv2.TERM_CRITERIA_EPS +
                              cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))

                self.image_points[id_camera][angle] = corners

        except cv2.error:
            return False

        return found

    def dump(self, filename):
        # Convert to json format
        image_points = collections.defaultdict(dict)
        for id_camera in self.image_points:
            for angle in self.image_points[id_camera]:
                image_points[id_camera][angle] = \
                    self.image_points[id_camera][angle].tolist()

        save_class = dict()
        save_class['square_size'] = self.square_size
        save_class['shape'] = self.shape
        save_class['image_points'] = image_points

        with open(filename, 'w') as output_file:
            json.dump(save_class, output_file,
                      sort_keys=True,
                      indent=4,
                      separators=(',', ': '))

    @staticmethod
    def load(filename):

        with open(filename, 'r') as input_file:
            save_class = json.load(input_file)

            square_size = float(save_class['square_size'])
            shape = [int(val) for val in save_class['shape']]

            chessboard = Chessboard(square_size, shape)

            image_points = save_class['image_points']

            # Convert to numpy format
            for id_camera in image_points:
                for angle in image_points[id_camera]:
                    chessboard.image_points[id_camera][float(angle)] = \
                        numpy.array(image_points[id_camera][angle]).astype(
                            numpy.float)

        return chessboard
