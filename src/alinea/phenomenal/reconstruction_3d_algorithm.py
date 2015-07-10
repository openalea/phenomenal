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


# =======================================================================
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
def side_projection(cube, rvec, mtx, tvec):
    """

    :param cube:
    :param rvec:
    :param mtx:
    :param tvec:
    :return:
    """

    object_points = np.ndarray(
        shape=(1, 3),
        buffer=np.array([[cube.center.x - mtx[0][2],
                          cube.center.y - mtx[0][2],
                          cube.center.z - mtx[1][2]]]))

    projs, jac = cv2.projectPoints(object_points,
                                   rvec,
                                   tvec,
                                   mtx,
                                   None)

    return projs[0][0][0], projs[0][0][1]


def bbox_projection(cube, rvec, mtx, tvec):
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
        x, y = side_projection(cube, rvec, mtx, tvec)
        lx.append(x)
        ly.append(y)

    xmin = int(min(lx))
    xmax = int(max(lx))
    ymin = int(min(ly))
    ymax = int(max(ly))

    return [xmin, xmax, ymin, ymax]


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

    return (min(calibration.w, max(1, xim)),
            min(calibration.h, max(1, yim)),
            conv)


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

    return (min(calibration.h, max(1, xim)),
            min(calibration.w, max(1, yim)),
            conv)


def bbox_manual_projection(cube, calibration, top_image=False):
    """

    :param cube:
    :param calibration:
    :param top_image:
    :return:
    """
    new_cubes = split_cube(cube)

    lx = []
    ly = []

    if top_image is True:
        for cube in new_cubes:
            x, y, z = top_manual_projection(cube, calibration)
            lx.append(x)
            ly.append(y)
    else:
        for cube in new_cubes:
            x, y, z = side_manual_projection(cube, calibration)
            lx.append(x)
            ly.append(y)

    xmin = int(min(lx))
    xmax = int(max(lx))
    ymin = int(min(ly))
    ymax = int(max(ly))

    return xmin, xmax, ymin, ymax


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

def fast_screen(image, cubes, rvec, mtx, tvec):
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
    """ fast screen documentation


    """
    h, l = np.shape(image)

    kept = deque()
    while True:
        try:
            cube = cubes.popleft()

            x, y = side_projection(cube, rvec, mtx, tvec)

            if y >= 0 and y < h and x >= 0 and x < l:
                if image[y, x] > 0:
                    kept.append(cube)
                    continue

            # ===========================================================

            b = False
            bbox = bbox_projection(cube, rvec, mtx, tvec)

            for i in range(4):
                if bbox[i] < 0:
                    bbox[i] = 0

            for i in [0, 1]:
                for j in [2, 3]:
                    if bbox[i] > 0 and bbox[i] < l and bbox[j] > 0 and bbox[
                        j] < h:
                        if image[bbox[j], bbox[i]] > 0:
                            b = True

            if b is True:
                kept.append(cube)
                continue

            # ===========================================================

            if bbox[3] > h:
                bbox[3] = h - 1

            if bbox[1] > l:
                bbox[1] = l - 1

            img = image[bbox[2]:bbox[3], bbox[0]:bbox[1]]

            if img.any() > 0:
                kept.append(cube)

        except IndexError:
            break

    return kept


def fast_manual_screen(image, cubes, calibration, top_image=False):
    """ fast screen documentation

    :param image:
    :param cubes:
    :param calibration:
    :param top_image:
    :return:

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
    """
    dim_image = np.shape(image)

    kept = deque()
    while True:
        try:
            cube = cubes.popleft()

            if top_image is True:
                x, y, z = top_manual_projection(cube, calibration)
            else:
                x, y, z = side_manual_projection(cube, calibration)

            if y < dim_image[0] and x < dim_image[1]:
                if image[y, x] > 0:
                    kept.append(cube)
                    continue

            # =================================================================

            b = False
            bbox = bbox_manual_projection(cube, calibration, top_image)

            for i in [0, 1]:
                for j in [2, 3]:
                    if bbox[i] < dim_image[1] and bbox[j] < dim_image[0]:
                        if image[bbox[j], bbox[i]] > 0:
                            b = True

            if b is True:
                kept.append(cube)
                continue

            # =================================================================

            img = image[bbox[2]:bbox[3], bbox[0]:bbox[1]]
            if img.any() > 0:
                kept.append(cube)

        except IndexError:
            break

    return kept
