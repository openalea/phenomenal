# -*- python -*-
#
#       reconstruction_3d.py :
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
import os
import math
import numpy as np
import cv2
from collections import deque

#       ========================================================================
#       Local Import
import alinea.phenomenal.reconstruction_3d_algorithm as algo

#       ========================================================================


def reconstruction_3d_manual_calibration(images, calibration, precision=1):
    origin = algo.Cube(calibration.cbox / 2.0,
                       calibration.cbox / 2.0,
                       calibration.hbox / 2.0,
                       max(calibration.cbox, calibration.hbox))

    cubes = deque()
    cubes.append(origin)

    nb_iteration = int(round(math.log10(origin.radius / precision) /
                             math.log10(2)))

    for i in range(nb_iteration):
        print 'octree decimation, iteration', i + 1, '/', nb_iteration
        cubes = algo.manual_split_cubes(cubes)
        print "start len : ", len(cubes)
        for angle in images:

            cubes = algo.octree_builder(images[angle],
                                        cubes,
                                        calibration,
                                        angle)

            print "image: ", angle, "end len : ", len(cubes)

    return cubes


def reconstruction_3d(images, calibration, precision=1):
    origin = algo.Cube(0, 0, 0, 1500)

    cubes = deque()
    cubes.append(origin)

    nb_iteration = int(round(math.log10(origin.radius / precision) /
                             math.log10(2)))

    for i in range(nb_iteration):
        print 'octree decimation, iteration', i + 1, '/', nb_iteration
        cubes = algo.split_cubes(cubes)
        print "start len : ", len(cubes)
        for angle in images:

            cubes = algo.octree_builder(images[angle],
                                        cubes,
                                        calibration,
                                        angle)

            print "image: ", angle, "end len : ", len(cubes)

    return cubes


def new_reconstruction_3d(images, calibration):

    origin = algo.Cube(0, 0, 0, 2500)

    my_octree = algo.new_octree_builder(
        images, calibration, algo.side_projection, origin, 0)

    return my_octree


def re_projection_cubes_to_image(cubes, image, calibration, color=(255, 0, 0)):

    img = image.copy()
    if len(image.shape) == 2:
        h, l = np.shape(image)
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    else:
        h, l, _ = np.shape(image)

    for cube in cubes:
        x_min, x_max, y_min, y_max = algo.bbox_projection(
            cube, calibration, algo.side_projection)

        x_min = min(max(x_min, 0), l - 1)
        x_max = min(max(x_max, 0), l - 1)
        y_min = min(max(y_min, 0), h - 1)
        y_max = min(max(y_max, 0), h - 1)

        img[y_min:y_max, x_min:x_max] = color

    return img


def manual_re_projection_cubes_to_image(cubes, image, calibration, angle):

    h, l = np.shape(image)

    img = image.copy()
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    if angle != 0:
        cubes = algo.side_rotation(cubes, angle, calibration)

    for cube in cubes:
        x_min, x_max, y_min, y_max = algo.bbox_projection(
            cube, calibration, algo.side_manual_projection)

        x_min = min(max(x_min, 0), l - 1)
        x_max = min(max(x_max, 0), l - 1)
        y_min = min(max(y_min, 0), h - 1)
        y_max = min(max(y_max, 0), h - 1)

        img[y_min:y_max, x_min:x_max] = (255, 0, 0)

    if angle != 0:
        cubes = algo.side_rotation(cubes, -angle, calibration)

    return img


def re_projection_octree_to_image(octree, image, calibration):

    h, l = np.shape(image)

    img = image.copy()
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    oct_nodes = list()
    oct_nodes.append(octree)

    while True:
        if not oct_nodes:
            break

        oct_node = oct_nodes.pop()

        if oct_node.isLeafNode is True:
            cube = algo.Cube(oct_node.position[0],
                             oct_node.position[1],
                             oct_node.position[2],
                             oct_node.size)

            x_min, x_max, y_min, y_max = algo.bbox_projection(
                cube, calibration, algo.side_projection)

            x_min = min(max(x_min, 0), l - 1)
            x_max = min(max(x_max, 0), l - 1)
            y_min = min(max(y_min, 0), h - 1)
            y_max = min(max(y_max, 0), h - 1)

            img[y_min:y_max, x_min:x_max] = (255, 0, 0)

        else:
            for branch in oct_node.branches:
                if branch is not None:
                    oct_nodes.append(branch)

    return img


def change_orientation(cubes):

    for cube in cubes:
        x = cube.position[0, 0]
        y = - cube.position[0, 2]
        z = - cube.position[0, 1]

        cube.position[0, 0] = x
        cube.position[0, 1] = y
        cube.position[0, 2] = z

    return cubes


def limit_cubes(cubes):
    x_min = float("inf")
    y_min = float("inf")
    z_min = float("inf")

    x_max = - float("inf")
    y_max = - float("inf")
    z_max = - float("inf")

    for cube in cubes:
        x, y, z = cube.position[0, 0], cube.position[0, 1], cube.position[0, 2]

        x_min = min(x_min, x)
        y_min = min(y_min, y)
        z_min = min(z_min, z)

        x_max = max(x_max, x)
        y_max = max(y_max, y)
        z_max = max(z_max, z)

    return x_min, y_min, z_min, x_max, y_max, z_max


def cubes_to_matrix(cubes):

    x_min, y_min, z_min, x_max, y_max, z_max = limit_cubes(cubes)

    r = cubes[0].radius * 2
    print r
    print x_min, x_max, (x_max - x_min) / r
    print y_min, y_max, (y_max - y_min) / r
    print z_min, z_max, (z_max - z_min) / r

    x_r_min = x_min / r
    y_r_min = y_min / r
    z_r_min = z_min / r

    mat = np.zeros((((x_max - x_min) / r) + 1,
                    ((y_max - y_min) / r) + 1,
                    ((z_max - z_min) / r) + 1))

    print mat.shape

    X = list()
    Y = list()
    Z = list()

    for cube in cubes:
        x, y, z = cube.position[0, 0], cube.position[0, 1], cube.position[0, 2]
        x_new = (x / r) - x_r_min
        y_new = (y / r) - y_r_min
        z_new = (z / r) - z_r_min

        print x_new, y_new, z_new

        X.append(np.uint8(x_new))
        Y.append(np.uint8(y_new))
        Z.append(np.uint8(z_new))

        mat[x_new, y_new, z_new] = 1

    return mat


def save_matrix_like_stack_image(matrix, data_directory):

    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    xl, yl, zl = matrix.shape
    print xl, yl, zl
    for i in range(zl):
        mat = matrix[:, :, i] * 255
        cv2.imwrite(data_directory + '%d.png' % i, mat)
