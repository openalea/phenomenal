# -*- python -*-
#
#       reconstruction_3d_algorithm.py :
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
#       ========================================================================


#       ========================================================================
#       External Import
import math
import numpy as np
import cv2
from collections import deque

#       ========================================================================
#       Local Import
import alinea.phenomenal.octree as octree


#       ========================================================================
#       Class

class Cube(object):
    __slots__ = ['radius', 'position']

    def __init__(self, x, y, z, radius):
        self.radius = radius
        self.position = np.float32([[x, y, z]])

    def oct_split(self):

        radius = self.radius / 2.0

        cx = self.position[0, 0]
        cy = self.position[0, 1]
        cz = self.position[0, 2]

        x_minus = cx - radius
        x_plus = cx + radius

        y_minus = cy - radius
        y_plus = cy + radius

        z_minus = cz - radius
        z_plus = cz + radius

        l = deque()
        l.append(Cube(x_minus, y_minus, z_minus, radius))
        l.append(Cube(x_plus, y_minus, z_minus, radius))
        l.append(Cube(x_minus, y_plus, z_minus, radius))
        l.append(Cube(x_minus, y_minus, z_plus, radius))
        l.append(Cube(x_plus, y_plus, z_minus, radius))
        l.append(Cube(x_plus, y_minus, z_plus, radius))
        l.append(Cube(x_minus, y_plus, z_plus, radius))
        l.append(Cube(x_plus, y_plus, z_plus, radius))

        return l

    def get_corner(self):
        radius = self.radius

        cx = self.position[0, 0]
        cy = self.position[0, 1]
        cz = self.position[0, 2]

        x_minus = cx - radius
        x_plus = cx + radius

        y_minus = cy - radius
        y_plus = cy + radius

        z_minus = cz - radius
        z_plus = cz + radius

        l = deque()
        l.append(Cube(x_minus, y_minus, z_minus, radius))
        l.append(Cube(x_plus, y_minus, z_minus, radius))
        l.append(Cube(x_minus, y_plus, z_minus, radius))
        l.append(Cube(x_minus, y_minus, z_plus, radius))
        l.append(Cube(x_plus, y_plus, z_minus, radius))
        l.append(Cube(x_plus, y_minus, z_plus, radius))
        l.append(Cube(x_minus, y_plus, z_plus, radius))
        l.append(Cube(x_plus, y_plus, z_plus, radius))

        return l

    def print_value(self):
        print (self.position[0, 0],
               self.position[0, 1],
               self.position[0, 2],
               self.radius)

#       ========================================================================
#       ROTATION
def side_rotation(cubes, theta, calibration):

    t = -theta / 180.0 * math.pi
    cbox2 = calibration.cbox / 2.0
    sint = math.sin(t)
    cost = math.cos(t)

    for cube in cubes:
        x = cube.position[0, 0] - cbox2
        y = cube.position[0, 1] - cbox2

        tmp_x = cost * x - sint * y
        tmp_y = sint * x + cost * y

        cube.position[0, 0] = tmp_x + cbox2
        cube.position[0, 1] = tmp_y + cbox2

    return cubes

#       ========================================================================
#       PROJECTION

def side_manual_projection(cube, calibration):
    # coordinates / optical center in real world
    x = cube.position[0, 0] - calibration.xo
    y = cube.position[0, 1] - calibration.yo
    z = cube.position[0, 2] - calibration.zo

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
    # coordinates / optical center in real world
    x = cube.position[0, 0] - calibration.xt
    y = cube.position[0, 1] - calibration.yt
    z = cube.position[0, 2] - calibration.zt

    # scale at this distance
    conv = calibration.convTopref + z * calibration.pTop

    # image coordinates / optical center and real world oriented  axes
    ximo = x * conv
    yimo = y * conv
    # image coordinates
    xim = round(calibration.h / 2 + ximo)
    yim = round(calibration.w / 2 - yimo)

    return min(calibration.h, max(1, xim)), min(calibration.w, max(1, yim))


def bbox_projection(cube, calibration, angle):

    cubes_corners = cube.get_corner()

    lx = []
    ly = []

    for cube in cubes_corners:
        x, y = calibration.project_position(cube.position, angle)
        lx.append(x)
        ly.append(y)

    x_min = min(lx)
    x_max = max(lx)
    y_min = min(ly)
    y_max = max(ly)

    return [x_min, x_max, y_min, y_max]


#       ========================================================================
#       Create and split cubes

def split_cubes(cubes):

    if len(cubes) == 0:
        return cubes

    l = deque()
    while True:
        try:
            cube = cubes.popleft()
            l += cube.oct_split()

        except IndexError:
            break

    return l


def manual_split_cubes(cubes):

    if len(cubes) == 0:
        return cubes

    radius = cubes[0].radius / 2.0
    r = radius / 2.0

    l = deque()
    while True:
        try:
            cube = cubes.popleft()

            cx = cube.position[0, 0]
            cy = cube.position[0, 1]
            cz = cube.position[0, 2]

            x_minus = cx - r
            x_plus = cx + r

            y_minus = cy - r
            y_plus = cy + r

            z_minus = cz - r
            z_plus = cz + r

            l.append(Cube(x_minus, y_minus, z_minus, radius))
            l.append(Cube(x_plus, y_minus, z_minus, radius))
            l.append(Cube(x_minus, y_plus, z_minus, radius))
            l.append(Cube(x_minus, y_minus, z_plus, radius))
            l.append(Cube(x_plus, y_plus, z_minus, radius))
            l.append(Cube(x_plus, y_minus, z_plus, radius))
            l.append(Cube(x_minus, y_plus, z_plus, radius))
            l.append(Cube(x_plus, y_plus, z_plus, radius))

        except IndexError:
            break

    return l

#       =======================================================================
#       Algorithm


def cube_is_in_image(image, cube, calibration, angle):
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
    """

    h, l = np.shape(image)
    x, y = calibration.project_position(cube.position, angle)

    if 0 <= y < h and 0 <= x < l:
        if image[y, x] > 0:
            return True

    # =================================================================

    x_min, x_max, y_min, y_max = bbox_projection(
        cube, calibration, angle)

    x_min = min(max(x_min, 0), l - 1)
    x_max = min(max(x_max, 0), l - 1)
    y_min = min(max(y_min, 0), h - 1)
    y_max = min(max(y_max, 0), h - 1)

    if (image[y_min, x_min] > 0 or
        image[y_max, x_min] > 0 or
        image[y_min, x_max] > 0 or
        image[y_max, x_max] > 0):
        return True
    # ==================================================================

    img = image[y_min:y_max + 1, x_min:x_max + 1]

    if np.any(img > 0):
        return True

    return False


def octree_builder(image, cubes, calibration, angle):
    kept = deque()
    while True:
        try:
            cube = cubes.popleft()

            if cube_is_in_image(image, cube, calibration, angle):
                kept.append(cube)

        except IndexError:
            break

    return kept


def new_octree_builder(images, calibrations, angle, cube, iteration):

    ok = True
    for angle in images:
        image = images[angle]
        calibration = calibrations[angle]

        if not cube_is_in_image(image, cube, calibration, angle):
            ok = False

    if ok is False:
        return None

    oct_node = octree.OctNode((cube.position[0, 0],
                               cube.position[0, 1],
                               cube.position[0, 2]), cube.radius)

    if iteration == 9:
        return oct_node

    oct_node.isLeafNode = False

    l = cube.oct_split()

    for i in range(len(l)):
        oct_node.branches[i] = new_octree_builder(
            images, calibrations, angle, l[i], iteration + 1)

    no_branch = True
    for i in range(len(l)):
        if oct_node.branches[i] is not None:
            no_branch = False

    if no_branch is True:
        return None

    return oct_node


#       =======================================================================
#       LOCAL TEST

if __name__ == "__main__":
    do_nothing = None


