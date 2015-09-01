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
#       ========================================================================

"""
Write the doc here...
"""

__revision__ = ""

#       ========================================================================
#       External Import
import math
import numpy as np
import cv2
from collections import deque

#       ========================================================================
#       Local Import
import alinea.phenomenal.reconstruction_3d_algorithm as algo

#       ========================================================================


def reconstruction_3d_manual_calibration(images, calibration, precision=1):
    """ Octree doc

    :param images:
    :param angle:
    :param calibration:
    :param precision:
    :param use_top_image:
    :return:
    """

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
        for angle in images.keys():
            if angle == -1:
                cubes = algo.octree_builder(
                    images[angle],
                    cubes,
                    calibration,
                    algo.top_manual_projection)
                print "HERE"
            else:
                if angle != 0:
                    cubes = algo.side_rotation(cubes, angle, calibration)

                cubes = algo.octree_builder(
                    images[angle],
                    cubes,
                    calibration,
                    algo.side_manual_projection)

                if angle != 0:
                    cubes = algo.side_rotation(cubes, -angle, calibration)

            print "image: ", angle, "end len : ", len(cubes)

    return cubes


def reconstruction_3d(images, calibration, precision=1):
    origin = algo.Cube(0, 0, 0, 2500)

    cubes = deque()
    cubes.append(origin)

    nb_iteration = int(round(math.log10(origin.radius / precision) /
                             math.log10(2)))

    for i in range(nb_iteration):
        print 'octree decimation, iteration', i + 1, '/', nb_iteration
        cubes = algo.split_cubes(cubes)

        print "start len : ", len(cubes)
        for angle in images.keys():
            cubes = algo.octree_builder(
                images[angle], cubes, calibration[angle], algo.side_projection)

            print "image: ", angle, "end len : ", len(cubes)

    return cubes


def new_reconstruction_3d(images, calibration, precision=1):

    origin = algo.Cube(0, 0, 0, 2500)

    my_octree = algo.new_octree_builder(
        images, calibration, algo.side_projection, origin, 0)

    return my_octree


def re_projection_cubes_to_image(cubes, image, calibration):

    h, l = np.shape(image)

    img = image.copy()
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    for cube in cubes:
        x_min, x_max, y_min, y_max = algo.bbox_projection(
            cube, calibration, algo.side_projection)

        x_min = min(max(x_min, 0), l - 1)
        x_max = min(max(x_max, 0), l - 1)
        y_min = min(max(y_min, 0), h - 1)
        y_max = min(max(y_max, 0), h - 1)

        img[y_min:y_max, x_min:x_max] = (255, 0, 0)

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
