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
import math
import collections


#       ========================================================================
#       Local Import
import alinea.phenomenal.reconstruction_3d_algorithm


#       ========================================================================


def reconstruction_3d_manual_calibration(images, calibration, precision=1):
    origin = alinea.phenomenal.reconstruction_3d_algorithm.Cube(
        calibration.cbox / 2.0,
        calibration.cbox / 2.0,
        calibration.hbox / 2.0,
        max(calibration.cbox, calibration.hbox))

    cubes = collections.deque()
    cubes.append(origin)

    nb_iteration = int(round(math.log10(origin.radius / precision) /
                             math.log10(2)))

    for i in range(nb_iteration):
        print 'octree decimation, iteration', i + 1, '/', nb_iteration
        cubes = \
            alinea.phenomenal.reconstruction_3d_algorithm.manual_split_cubes(
                cubes)
        print "start len : ", len(cubes)
        for angle in images:
            cubes = \
                alinea.phenomenal.reconstruction_3d_algorithm.octree_builder(
                    images[angle],
                    cubes,
                    calibration,
                    angle)

            print "image: ", angle, "end len : ", len(cubes)

    return cubes


def reconstruction_3d(images, calibration, precision=1, verbose=False):
    origin = alinea.phenomenal.reconstruction_3d_algorithm.Cube(0, 0, 0, 2048)

    cubes = collections.deque()
    cubes.append(origin)

    nb_iteration = int(round(math.log10(origin.radius / precision) /
                             math.log10(2)))

    radius = origin.radius
    nb_iteration = 0
    while radius > 0 and precision < radius:
        radius >>= 1
        nb_iteration += 1

    print nb_iteration
    for i in range(nb_iteration):

        if verbose is True:
            print 'octree decimation, iteration', i + 1, '/', nb_iteration
        cubes = alinea.phenomenal.reconstruction_3d_algorithm.split_cubes(cubes)
        if verbose is True:
            print "start len : ", len(cubes)
        for angle in images:

            cubes = alinea.phenomenal.reconstruction_3d_algorithm.octree_builder(
                images[angle],
                cubes,
                calibration,
                angle)

            if verbose is True:
                print "image: ", angle, "end len : ", len(cubes)

    return cubes


def change_orientation(cubes):
    for cube in cubes:
        x = cube.position[0, 0]
        y = - cube.position[0, 2]
        z = - cube.position[0, 1]

        cube.position[0, 0] = x
        cube.position[0, 1] = y
        cube.position[0, 2] = z

    return cubes
