# -*- python -*-
# -*- coding: latin-1 -*-
#
#       frame : mechanics package
#
#       Copyright or © or Copr. 2006 INRIA - CIRAD - INRA
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       VPlants WebSite : https://gforge.inria.fr/projects/vplants/
#
""" This module defines a typical pinhole camera
"""

__all__ = ["Camera"]

# TODO: add clipping???


class Camera(object):
    """ Project point in space on the focal plane of the camera
    """

    def __init__(self, image_size, scaling):
        """ Defines a new Camera

        Args:
         - image_size (int, int): size of picture taken by this camera in pix
         - scaling (float, float): scaling factor between real coordinates
                                   and pixel coordinates
        """
        self._w, self._h = image_size
        self._sca_w, self._sca_h = scaling

    def pixel_coordinates(self, point):
        """ Compute image coordinates of a 3d point

        Args:
         - point (float, float, float): a point in space
                    expressed in camera frame coordinates

        return:
         - (int, int): coordinate of point in image in pix
        """
        # if point[2] < 1:
        #     raise UserWarning("point too close to the camera")

        u = point[0] / point[2] * self._sca_w + self._w / 2
        v = point[1] / point[2] * self._sca_h + self._h / 2

        return u, v