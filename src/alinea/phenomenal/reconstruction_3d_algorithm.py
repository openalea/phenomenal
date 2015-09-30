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
import collections
import math
import numpy


#       ========================================================================
#       Local Import


#       ========================================================================
#       Class

class Cube(object):
    __slots__ = ['radius', 'position']

    def __init__(self, x, y, z, radius):
        self.radius = radius
        self.position = numpy.float32([x, y, z])

    def oct_split(self):

        radius = self.radius / 2.0

        cx = self.position[0]
        cy = self.position[1]
        cz = self.position[2]

        x_minus = cx - radius
        x_plus = cx + radius

        y_minus = cy - radius
        y_plus = cy + radius

        z_minus = cz - radius
        z_plus = cz + radius

        l = collections.deque()
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

        cx = self.position[0]
        cy = self.position[1]
        cz = self.position[2]

        x_minus = cx - radius
        x_plus = cx + radius

        y_minus = cy - radius
        y_plus = cy + radius

        z_minus = cz - radius
        z_plus = cz + radius

        l = collections.deque()
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
        print (self.position[0],
               self.position[1],
               self.position[2],
               self.radius)


#       ========================================================================
#       PROJECTION

def bbox_projection(cube, calibration, angle):

    cubes_corners = cube.get_corner()

    lx = []
    ly = []

    for cube in cubes_corners:
        # x, y = angle(cube, calibration)
        x, y = calibration.project_point(cube.position, angle)
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

    l = collections.deque()
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

    l = collections.deque()
    while True:
        try:
            cube = cubes.popleft()

            cx = cube.position[0]
            cy = cube.position[1]
            cz = cube.position[2]

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

    h, l = numpy.shape(image)
    x, y = calibration.project_point(cube.position, angle)

    if 0 <= y < h and 0 <= x < l:
        if image[y, x] > 0:
            return True

    # =================================================================

    x_min, x_max, y_min, y_max = bbox_projection(cube, calibration, angle)

    x_min = min(max(math.floor(x_min), 0), l - 1)
    x_max = min(max(math.ceil(x_max), 0), l - 1)
    y_min = min(max(math.floor(y_min), 0), h - 1)
    y_max = min(max(math.ceil(y_max), 0), h - 1)

    if (image[y_min, x_min] > 0 or
        image[y_max, x_min] > 0 or
        image[y_min, x_max] > 0 or
            image[y_max, x_max] > 0):
        return True
    # ==================================================================

    img = image[y_min:y_max + 1, x_min:x_max + 1]

    if numpy.any(img > 0):
        return True

    return False


def octree_builder(image, cubes, calibration, angle):
    kept = collections.deque()
    while True:
        try:
            cube = cubes.popleft()

            if cube_is_in_image(image, cube, calibration, angle):
                kept.append(cube)

        except IndexError:
            break

    return kept


#       =======================================================================
#       LOCAL TEST

if __name__ == "__main__":
    do_nothing = None


