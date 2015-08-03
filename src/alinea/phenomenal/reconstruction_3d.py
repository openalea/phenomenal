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
#       Local Import
import alinea.phenomenal.reconstruction_3d_algorithm as algo

#       =======================================================================

def reconstruction_3d_manual_calibration(images, calibration, precision=1):
    """ Octree doc

    :param images:
    :param angle:
    :param calibration:
    :param precision:
    :param use_top_image:
    :return:
    """

    origin = algo.Cube(
        algo.Point3D(calibration.cbox / 2.0,
                     calibration.cbox / 2.0,
                     calibration.hbox / 2.0),
        max(calibration.cbox, calibration.hbox))

    cubes = deque()
    cubes.append(origin)

    nb_iteration = int(round(math.log10(origin.radius / precision) /
                             math.log10(2)))

    for i in range(nb_iteration):
        print 'octree decimation, iteration', i + 1, '/', nb_iteration

        cubes = algo.split_cubes(cubes)

        print "start len : ", len(cubes)
        for angle in images.keys():
            if angle == -1:
                cubes = algo.octree_builder(images[angle],
                                         cubes,
                                         calibration,
                                         algo.top_manual_projection)
            else:
                if angle != 0:
                    cubes = algo.side_rotation(cubes, angle, calibration)

                cubes = algo.octree_builder(images[angle],
                                         cubes,
                                         calibration,
                                         algo.side_manual_projection)
                if angle != 0:
                    cubes = algo.side_rotation(cubes, -angle, calibration)

            print "image: ", angle, "end len : ", len(cubes)

    return cubes


def reconstruction_3d(images, calibration, precision=1):
    """

    :param images:
    :param angle:
    :param calibration:
    :param precision:
    :param use_top_image:
    :return:
    """
    origin = algo.Cube(algo.Point3D(0, 0, 0), 5000)

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


def reprojection_3d_objects_to_images(images, cubes, calibration):
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

    h, l = np.shape(images[0])

    for angle in images.keys():
        img = images[angle]
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        for cube in cubes:
            xmin, xmax, ymin, ymax = algo.bbox_projection(
                cube, calibration[angle], algo.side_projection)

            xmin = min(max(xmin, 0), l - 1)
            xmax = min(max(xmax, 0), l - 1)
            ymin = min(max(ymin, 0), h - 1)
            ymax = min(max(ymax, 0), h - 1)

            img[ymin:ymax, xmin:xmax] = (255, 0, 0)

        cv2.namedWindow(str(angle), cv2.WINDOW_NORMAL)
        cv2.imshow(str(angle), img)
        cv2.waitKey()
        cv2.destroyAllWindows()

