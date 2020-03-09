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

    def __init__(self, square_size=50, shape=(7, 7), facing_rotations=None):
        """Instantiate a chessboard object

        Args:
            square_size: length (world units) of the side of an elemental square of the chessboard
            shape: (int, int) the number of square detected along chessboard width and height
            facing_rotations (optional): a {camera_id: facing_rotation} dict indicating for what value
            of the turntable rotation consign the chessboard is facing the camera.

        """
        self.square_size = square_size
        self.shape = shape
        self.image_points = collections.defaultdict(dict)
        self.image_ids = dict()
        self.facing_rotations = dict()
        if facing_rotations is not None:
            self.facing_rotations = facing_rotations


    def __str__(self):
        s = ("Chessboard Attributes :\n"
             "Square size (mm): {}\n"
             "Shape : {}\n".format(self.square_size, self.shape))

        return s

    def get_corners_local_3d(self):
        """ Chessboard local frame is defined by chessboard center, x axis along width (left >right),
            Y-axis along height (bottom -> up) and z axis normal to chessboard plane
            Chessboard corners are returned ordered line by line, from top left to bottom right"""

        square_size = self.square_size
        width, height = self.shape

        corners_local_3d = list()
        origin = numpy.array([width * square_size / 2., height * square_size / 2., 0])
        for y in reversed(range(height)):
            for x in range(width):
                v = numpy.array([x * square_size, y * square_size, 0.0]) - origin
                corners_local_3d.append(v)

        return corners_local_3d

    def get_corners_2d(self, id_camera):
        corners_2d = dict()
        for angle in self.image_points[id_camera]:
            corners_2d[angle] = self.image_points[id_camera][angle][:, 0, :]

        return corners_2d

    def check_order(self, image_points, rotation, facing_rotation):
        """
        order image points to match order of corner points (see details)

        Args:
            image_points: image points detected by openCV findChessboardCorners
            rotation: the turntable rotation consign at image acquisition
            facing_rotation: the turntable rotation consign that make the chessboard face
            the camera

        Returns:
            image_points, in the expected order

        Details:
            Chessboard corners are detected with OpenCV findChessboardCorners function,
            that always return corners from top left to bottom right position on the image
            (left-right axis being chessboard width). This corresponds to expected order
            if chessboard upper side is pointing to the top of the image, but to the reversed
            expected order if chessboard upper side is pointing to the base of the image.
            We suppose that reversed order detection occurs for rotations +/- 90 deg far
            from facing_rotation
        """

        flip_min = (facing_rotation + 90) % 360
        flip_max = (flip_min + 90) % 360

        first_v = image_points[0, 0, 1]
        last_v = image_points[-1, 0, 1]

        if flip_max > flip_min:
            reverse = rotation >= flip_min and rotation < flip_max and last_v > first_v
        else:
            reverse = (rotation >= flip_min or rotation < flip_max) and last_v > first_v

        if reverse:
            return numpy.array([p for p in reversed(image_points.tolist())])
        else:
            return image_points

    def detect_corners(self, id_camera, rotation, image, check_order=True, image_id=None):
        """ Detection of pixel coordinates of chessboard corner points

        Args:
            id_camera: (str) label of the camera that acquired the image
            rotation: (int) rotation consign (positive, in degrees). The
             rotation consign is the rounded angle by which the turntable
             has turned before image acquisition
            image: (image) numpy array of pixel intensities (rgb_color or grayscale)
            check_order: (bool) Check if the detected image points are in the expected order:
             image points order should match local 3d coordinates order
            image_id (str, optional): if given, the image name is kept in image_ids instance
            variable.


        Returns:
            True if chessboard corner are found otherwise False.

        Side effects: image points are added to the instance image point list

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

                if check_order:
                    if id_camera not in self.facing_rotations:
                        raise ValueError('facing rotation should be specified for order checking')
                    corners = self.check_order(corners, rotation, self.facing_rotations[id_camera])

                self.image_points[id_camera][rotation] = corners

        except cv2.error:
            return False

        if image_id is not None:
            self.image_ids[rotation] = image_id

        return found

    def dump(self, filename):
        # Convert to json format
        image_points = collections.defaultdict(dict)
        for id_camera in self.image_points:
            for id_image in self.image_points[id_camera]:
                image_points[id_camera][id_image] = \
                    self.image_points[id_camera][id_image].tolist()

        save_class = dict()
        save_class['square_size'] = self.square_size
        save_class['shape'] = self.shape
        save_class['image_points'] = image_points

        if len(self.facing_rotations) > 0:
            save_class['facing_rotations'] = self.facing_rotations

        if len(self.image_ids) > 0:
            save_class['image_ids'] = self.image_ids

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
                for rotation in image_points[id_camera]:
                    chessboard.image_points[id_camera][rotation] = \
                        numpy.array(image_points[id_camera][rotation])

            if 'facing_rotations' in save_class:
                chessboard.facing_rotations = save_class['facing_rotations']

            if 'image_ids' in save_class:
                chessboard.image_ids = save_class['image_ids']

        return chessboard
