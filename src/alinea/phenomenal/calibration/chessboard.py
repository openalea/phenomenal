# -*- python -*-
#
#       Copyright 2015 INRIA - CIRAD - INRA
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
    def __init__(self, square_size, shape):
        self.square_size = square_size
        self.shape = shape
        self.image_points = collections.defaultdict(dict)

    def __str__(self):
        my_str = ''
        my_str += 'Chessboard Attributes :\n'
        my_str += 'Square size (mm): ' + str(self.square_size) + '\n'
        my_str += 'Shape : ' + str(self.shape) + '\n'

        my_str += 'Number of angle : ' + str(len(self.image_points)) + '\n'
        for angle in self.image_points:
            my_str += str(angle) + ', '

        if len(self.image_points) > 0:
            my_str += '\n'

        return my_str

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

    def find_corners(self, image):
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
            else:
                return None

        except cv2.error:
            return None

        return corners

    def find_and_add_corners(self, id_camera, angle, image, verbose=False):

        image_points = self.find_corners(image)
        if image_points is not None:
            self.image_points[id_camera][angle] = image_points

        if verbose:
            print str(id_camera) + " camera, ",
            print str(angle).zfill(3) + " angle",
            if image_points is not None:
                print "\t- corners detected"
            else:
                print "\t- corners not found"

    def dump(self, file_path):
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

        with open(file_path + '.json', 'w') as output_file:
            json.dump(save_class, output_file,
                      sort_keys=True,
                      indent=4,
                      separators=(',', ': '))

    @staticmethod
    def load(file_path):

        with open(file_path + '.json', 'r') as input_file:
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
