# -*- python -*-
#
#       chessboard.py : 
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
import os
import cv2
import numpy


#       ========================================================================
#       Code
class Chessboard(object):
    def __init__(self, square_size, length, height):

        # Initialization
        self.square_size = square_size
        self.shape = (length, height)
        self.object_points = numpy.zeros((length * height, 3), numpy.float32)

        # Build Chessboard
        self.object_points[:, :2] = \
            numpy.mgrid[0:length, 0:height].T.reshape(-1, 2) * self.square_size

        # 48 points are stored in an 48x3 array obj
        # choose bottom-left corner as origin, to match australian convention
        self.object_points = self.object_points - self.object_points[40, :]

    def __str__(self):
        s = ''
        s += 'Chessboard Object Values :' + os.linesep
        s += 'Square size : ' + str(self.square_size) + os.linesep
        s += 'Shape : ' + str(self.shape) + os.linesep
        s += 'Object points : ' + str(self.object_points) + os.linesep

        return s

    def find_corners(self, image):
        try:

            found, corners = cv2.findChessboardCorners(
                image,
                self.shape,
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

    def draw_chessboard_corners_on_image(self,
                                         corners,
                                         image):

        y_min = min(corners[:, 0, 0])
        y_max = max(corners[:, 0, 0])
        x_min = min(corners[:, 0, 1])
        x_max = max(corners[:, 0, 1])
        r = 50

        image = cv2.drawChessboardCorners(image, self.shape, corners, True)
        image = image[x_min - r:x_max + r, y_min - r:y_max + r]

        return image

    def draw_points_on_image(self, projection_points, image):

        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        projection_points = projection_points.astype(int)
        image[projection_points[:, 0, 1],
              projection_points[:, 0, 0]] = [0, 0, 255]

        return image

#       ========================================================================
#       LOCAL TEST

if __name__ == "__main__":
    do_nothing = None
