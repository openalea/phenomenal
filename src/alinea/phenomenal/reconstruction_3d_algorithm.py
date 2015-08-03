# -*- python -*-
#
#       calibration_class: Module Description
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       File author(s):
#
#       File contributor(s):
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
#       =======================================================================

"""
Write the doc here...
"""

__revision__ = ""

#       =======================================================================
#       External Import
import math
import numpy as np
from collections import deque
import cv2


#       =======================================================================
#       Class
class Point3D(object):
    __slots__ = ['x', 'y', 'z']

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class Cube(object):
    __slots__ = ['center', 'radius']

    def __init__(self, center, radius):
        self.center = center
        self.radius = radius


#       =======================================================================
#       ROTATION
def side_rotation(cubes, theta, calibration):
    """

    :param cubes:
    :param theta:
    :param calibration:
    :return:
    """
    t = -theta / 180.0 * math.pi
    cbox2 = calibration.cbox / 2.0
    sint = math.sin(t)
    cost = math.cos(t)

    for cube in cubes:
        x = cube.center.x - cbox2
        y = cube.center.y - cbox2

        newx = cost * x - sint * y
        newy = sint * x + cost * y

        cube.center.x = newx + cbox2
        cube.center.y = newy + cbox2

    return cubes


#       =======================================================================
#       PROJECTION
def side_projection(cube, calibration):
    """

    :param cube:
    :param rvec:
    :param mtx:
    :param tvec:
    :return:
    """

    mtx, rvec, tvec, dist_coeff = calibration

    object_points = np.ndarray(
        shape=(1, 3),
        buffer=np.array([[cube.center.x,
                          cube.center.y,
                          cube.center.z]]))

    projs, jac = cv2.projectPoints(object_points,
                                   rvec,
                                   tvec,
                                   mtx,
                                   dist_coeff)

    return projs[0][0][0], projs[0][0][1]


def side_manual_projection(cube, calibration):
    """

    :param cube:
    :param calibration:
    :return:
    """
    # coordinates / optical center in real world
    x = cube.center.x - calibration.xo
    y = cube.center.y - calibration.yo
    z = cube.center.z - calibration.zo

    # scale at this distance
    conv = calibration.convSideref - y * calibration.pSide

    # image coordinates / optical center and real world oriented axes
    ximo = x * conv
    yimo = z * conv

    # EBI image coordinates
    xim = round(calibration.w / 2 + ximo)
    yim = round(calibration.h / 2 - yimo)

    return min(calibration.w, max(1, xim)), min(calibration.h, max(1, yim))


def top_manual_projection(cube, calibration):
    """

    :param cube:
    :param calibration:
    :return:
    """
    # coordinates / optical center in real world
    x = cube.center.x - calibration.xt
    y = cube.center.y - calibration.yt
    z = cube.center.z - calibration.zt
    # scale at this distance
    conv = calibration.convTopref + z * calibration.pTop
    # image coordinates / optical center and real world oriented  axes
    ximo = x * conv
    yimo = y * conv
    # image coordinates
    xim = round(calibration.h / 2 + ximo)
    yim = round(calibration.w / 2 - yimo)

    return min(calibration.h, max(1, xim)), min(calibration.w, max(1, yim))


def bbox_projection(cube, calibration, func_projection):
    """

    :param cube:
    :param rvec:
    :param mtx:
    :param tvec:
    :return:
    """
    new_cubes = split_cube(cube)

    lx = []
    ly = []

    for cube in new_cubes:
        x, y = func_projection(cube, calibration)
        lx.append(x)
        ly.append(y)

    xmin = int(min(lx))
    xmax = int(max(lx))
    ymin = int(min(ly))
    ymax = int(max(ly))

    return [xmin, xmax, ymin, ymax]


#       =======================================================================
#       Create and split cubes
def split_cube(cube):
    """

    :param cube:
    :return:
    """
    radius = cube.radius
    center = cube.center

    cx = center.x
    cy = center.y
    cz = center.z

    x_minus = cx - radius
    x_plus = cx + radius

    y_minus = cy - radius
    y_plus = cy + radius

    z_minus = cz - radius
    z_plus = cz + radius

    l = deque()
    l.append(Cube(Point3D(x_minus, y_minus, z_minus), radius))
    l.append(Cube(Point3D(x_plus, y_minus, z_minus), radius))
    l.append(Cube(Point3D(x_minus, y_plus, z_minus), radius))
    l.append(Cube(Point3D(x_minus, y_minus, z_plus), radius))
    l.append(Cube(Point3D(x_plus, y_plus, z_minus), radius))
    l.append(Cube(Point3D(x_plus, y_minus, z_plus), radius))
    l.append(Cube(Point3D(x_minus, y_plus, z_plus), radius))
    l.append(Cube(Point3D(x_plus, y_plus, z_plus), radius))

    return l


def split_cubes(cubes):
    """

    :param cubes:
    :return:
    """

    if len(cubes) == 0:
        return cubes

    radius = cubes[0].radius / 2.0
    r = radius / 2.0

    l = deque()
    while True:
        try:
            cube = cubes.popleft()
            center = cube.center

            cx = center.x
            cy = center.y
            cz = center.z

            x_minus = cx - r
            x_plus = cx + r

            y_minus = cy - r
            y_plus = cy + r

            z_minus = cz - r
            z_plus = cz + r

            l.append(Cube(Point3D(x_minus, y_minus, z_minus), radius))
            l.append(Cube(Point3D(x_plus, y_minus, z_minus), radius))
            l.append(Cube(Point3D(x_minus, y_plus, z_minus), radius))
            l.append(Cube(Point3D(x_minus, y_minus, z_plus), radius))
            l.append(Cube(Point3D(x_plus, y_plus, z_minus), radius))
            l.append(Cube(Point3D(x_plus, y_minus, z_plus), radius))
            l.append(Cube(Point3D(x_minus, y_plus, z_plus), radius))
            l.append(Cube(Point3D(x_plus, y_plus, z_plus), radius))

        except IndexError:
            break

    return l


#       =======================================================================
#       Algorithm
def octree_builder(image, cubes, calibration, func_projection):
    """

    Algorithm
    =========

    For each cube in cubes :
        - Project center cube position on image:
        - Kept the cube and pass to the next if :
            + The pixel value of center position projected is > 0

        - Compute the bounding box and project the positions on image
        - Kept the cube and pass to the next if :
            + The pixel value of extremity of bounding box projected is > 0

        - Kept the cube and pass to the next if :
            + Any pixel value in the bounding box projected is > 0

    :param image:
    :param cubes:
    :param rvec:
    :param mtx:
    :param tvec:
    :return:
    """
    h, l = np.shape(image)

    kept = deque()
    while True:
        try:
            cube = cubes.popleft()

            x, y = func_projection(cube, calibration)

            if 0 <= y < h and 0 <= x < l:
                if image[y, x] > 0:
                    kept.append(cube)
                    continue

            # =================================================================

            xmin, xmax, ymin, ymax = bbox_projection(
                cube, calibration, func_projection)

            xmin = min(max(xmin, 0), l - 1)
            xmax = min(max(xmax, 0), l - 1)
            ymin = min(max(ymin, 0), h - 1)
            ymax = min(max(ymax, 0), h - 1)

            if image[ymin, xmin] > 0 or \
               image[ymax, xmin] > 0 or \
               image[ymin, xmax] > 0 or \
               image[ymax, xmax] > 0:
                    kept.append(cube)
                    continue


            # =================================================================

            img = image[ymin:ymax + 1, xmin:xmax + 1]

            if img.any() > 0:
                kept.append(cube)

        except IndexError:
            break

    return kept

