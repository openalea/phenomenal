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

__all__ = ["Target", "Chessboard", "Chessboards"]

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

    def __init__(self, square_size=50, shape=(7, 7), facing_angles=None):
        """Instantiate a chessboard object

        Args:
            square_size: length (world units) of the side of an elemental square of the chessboard
            shape: (int, int) the number of square detected along chessboard width and height
            facing_angles: a {camera_id: facing_angle} dict indicating for what value
            of the turntable rotation consign the chessboard is facing the camera with topleft corner closest to topleft
            side of the image.

        """
        self.square_size = square_size
        self.shape = shape
        self.image_points = collections.defaultdict(dict)
        self.image_ids = dict()
        self.facing_angles = dict()
        self.image_sizes = dict()
        if facing_angles is not None:
            self.facing_angles = facing_angles


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
        if id_camera in self.image_points:
            for rotation in self.image_points[id_camera]:
                corners_2d[rotation] = self.image_points[id_camera][rotation][:, 0, :]

        return corners_2d

    @staticmethod
    def order_image_points(image_points, rotation, facing_angle, clockwise_rotation=True):
        """
        order image points to match order of corner points (see details)

        Args:
            image_points: image points detected by openCV findChessboardCorners
            rotation: (int) rotation consign (positive, in degrees). The
             rotation consign is the rounded angle by which the turntable
             has turned before image acquisition
            facing_angle: the turntable rotation consign that make the chessboard face
            the camera
            clockwise_rotation (bool): are targets rotating clockwise ? (default True)

        Returns:
            image_points, in the expected order

        Details:
            Chessboard corners are detected with OpenCV findChessboardCorners function,
            that always return corners from top left to bottom right position on the image
            (left-right axis being chessboard width). This corresponds to expected order
            if chessboard upper side is pointing to the top of the image, but to the reversed
            expected order if chessboard upper side is pointing to the base of the image.
            We suppose that reversed order detection occurs for rotations +/- 90 deg far
            from facing_angle
        """

        m = 1
        if not clockwise_rotation:
            m = -1
        flip_start = ((facing_angle + m * 90) % 360 + 360) % 360
        flip_end = ((flip_start + m * 180) % 360 + 360) % 360

        du = image_points[1, 0, 0] - image_points[0, 0, 0]

        if flip_end > flip_start:
            reverse = flip_end > rotation >= flip_start and du > 0
        else:
            reverse = (rotation >= flip_start or rotation < flip_end) and du > 0

        if reverse:
            return image_points[::-1]
        else:
            return image_points

    def check_order(self):
        """Re-order detected image points using facing angles"""
        for id_camera in self.image_points:
            for rotation in self.image_points[id_camera]:
                facing = self.facing_angles[id_camera]
                self.image_points[id_camera][rotation] = self.order_image_points(self.image_points[id_camera][rotation],
                                                                                 rotation, facing)

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
                    if id_camera not in self.facing_angles:
                        raise ValueError('facing rotation should be specified for order checking')
                    corners = self.order_image_points(corners, rotation, self.facing_angles[id_camera])

                self.image_points[id_camera][rotation] = corners

        except cv2.error:
            return False

        if image_id is not None:
            self.image_ids[rotation] = image_id

        return found

    def image_resolutions(self):

        def _dist(pix1, pix2):
            x1, y1 = pix1
            x2, y2 = pix2
            return numpy.sqrt((x2-x1)**2 +(y2 -y1)**2)

        def pixel_area(a, w):
            topleft = a[0]
            topright = a[:w, :][-1]
            bottomleft = a[-w, :]
            bottomright = a[-1]
            top = _dist(topleft, topright)
            bottom = _dist(bottomleft, bottomright)
            left = _dist(topleft, bottomleft)
            right = _dist(topright, bottomright)
            return numpy.mean([top, bottom]) * numpy.mean([left, right])

        width, height = self.shape
        area = width * height * self.square_size**2

        resolutions = {cid: [] for cid in self.image_points}
        for id_camera, cam_pts in self.image_points.items():
            for rotation in cam_pts:
                pts = self.get_corners_2d(id_camera)[rotation]
                pix_area = pixel_area(pts, width)
                resolutions[id_camera].append(numpy.sqrt(pix_area / area))

        resolutions = {cid: numpy.mean(res) for cid, res in resolutions.items()}

        return resolutions

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

        if len(self.facing_angles) > 0:
            save_class['facing_angles'] = self.facing_angles

        if len(self.image_ids) > 0:
            save_class['image_ids'] = self.image_ids

        if len(self.image_sizes) > 0:
            save_class['image_sizes'] = self.image_sizes

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
                    rot = int(float(rotation))
                    chessboard.image_points[id_camera][rot] = \
                        numpy.array(image_points[id_camera][rotation])

            if 'facing_angles' in save_class:
                chessboard.facing_angles = save_class['facing_angles']

            if 'image_ids' in save_class:
                chessboard.image_ids = save_class['image_ids']

            if 'image_sizes' in save_class:
                chessboard.image_sizes = save_class['image_sizes']

        return chessboard


class Chessboards(object):
    """A class for handling a collection of Chessboards objects imaged in the same system"""

    def __init__(self, chessboards):
        """

        Args:
            chessboards: a {chessboard_id: Chessboard, ...} dict
        """
        self.chessboards = chessboards

    @staticmethod
    def load(filenames):
        """

        Args:
            filenames: a {chessboard_id: chessboard_filename, ...} dict

        Returns:

        """
        chessboards = {k: Chessboard.load(v) for k, v in filenames.items()}
        return Chessboards(chessboards)

    def image_sizes(self):
        image_sizes = {}
        for chess in self.chessboards.values():
            image_sizes.update(chess.image_sizes)
        return image_sizes

    def cameras(self):
        return self.image_sizes().keys()

    def image_resolutions(self):
        image_resolutions = {cid: [] for cid in self.cameras()}
        for chess in self.chessboards.values():
            for cid, res in chess.image_resolutions().items():
                image_resolutions[cid].append(res)
        return {cid: numpy.mean(res) for cid, res in image_resolutions.items()}

    def facings(self):
        return {k: v.facing_angles for k, v in self.chessboards.items()}

    def image_points(self):
        return {camera: {k: v.get_corners_2d(camera) for k, v in self.chessboards.items()} for camera in self.cameras()}

    def target_points(self):
        return {k: v.get_corners_local_3d() for k, v in self.chessboards.items()}