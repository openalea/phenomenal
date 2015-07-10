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

#       =======================================================================
#       Local Import
import alinea.phenomenal.reconstruction_3d_algorithm as algo




def reconstruction_3d_manual_calibration(images, angles, calibration,
                                         precision=1, use_top_image=True):
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

        for j in range(len(images)):
            if angles[j] == -1:
                cubes = algo.fast_manual_screen(images[j], cubes, calibration, True)
            else:
                if angles[j] != 0:
                    cubes = algo.side_rotation(cubes, angles[j], calibration)

                cubes = algo.fast_manual_screen(images[j], cubes, calibration)

                if angles[j] != 0:
                    cubes = algo.side_rotation(cubes, -angles[j], calibration)

    return cubes




def reprojection_3d_objects_to_images(image, cubes, rvec, mtx, tvec):
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

    image[:] = 0
    h, l = np.shape(image)

    for cube in cubes:
        bbox = algo.bbox_projection(cube, rvec, mtx, tvec)

        for i in range(4):
            if bbox[i] < 0:
                bbox[i] = 0
        # ===========================================================

        if bbox[3] > h:
            bbox[3] = h - 1

        if bbox[1] > l:
            bbox[1] = l - 1

        image[bbox[2]:bbox[3], bbox[0]:bbox[1]] = 255

    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    cv2.imshow('image', image)
    cv2.waitKey()
    cv2.destroyAllWindows()


def reconstruction_3d(images, rvecs, mtx, tvecs, precision=1):
    """

    :param images:
    :param angle:
    :param calibration:
    :param precision:
    :param use_top_image:
    :return:
    """

    h, l = np.shape(images[0])
    print h, l

    origin = algo.Cube(algo.Point3D(l / 2.0, l / 2.0, h / 2.0), h / 2.0)
    print origin.center.x, origin.center.y, origin.center.z, origin.radius

    cubes = deque()
    cubes.append(origin)

    nb_iteration = int(round(math.log10(origin.radius / precision) /
                             math.log10(2)))

    nb_iteration = 8

    for i in range(nb_iteration):
        print 'octree decimation, iteration', i + 1, '/', nb_iteration
        cubes = algo.split_cubes(cubes)

        for j in range(len(images)):
            print i, "start len : ", len(cubes)
            cubes = algo.fast_screen(images[j], cubes, rvecs[j], mtx, tvecs[j])
            print i, "end len : ", len(cubes)

    return cubes


#       =======================================================================

import cv2
# images_path = [data/'top.png', data/'side0.png', data/'side90.png']

def load_images(images_path):
    images = []
    for image_name in images_path:
        print image_name
        im = cv2.imread(image_name, cv2.CV_LOAD_IMAGE_GRAYSCALE)
        images.append(im)
    return images


def binarize_images(images):
    for im in images:
        im[im == 255] = 0
        im[im != 0] = 255
    return images


import alinea.phenomenal.calibration_manual as calib_class


def get_configuration_camera():
    return calib_class.CameraConfiguration()


def get_calibration(configuration_camera):
    return calib_class.Calibration(configuration_camera)


def create_matrix(calibration):
    dtype = np.uint8
    matrix = np.zeros([calibration.cbox,
                       calibration.cbox,
                       calibration.hbox], dtype=dtype)

    return matrix


def fill_matrix(cubes, m):
    while True:
        try:
            cube = cubes.popleft()

            r = cube.radius
            x = cube.center.x
            y = cube.center.y
            z = cube.center.z

            m[x - r:x + r,
              y - r:y + r,
              z - r:z + r] = 50

        except IndexError:
            break

    return m


def write_images_on_matrix(images, m):
    img = images[1]
    h, l = np.shape(img)
    xl, yl, zl = np.shape(m)
    resized_image = cv2.resize(img, (xl, zl), interpolation=cv2.INTER_AREA)
    resized_image[resized_image > 0] = 255
    for h in range(zl):
        for l in range(xl):
            if resized_image[h, l] == 255:
                m[l, 0, zl - 30 - h - 1] = 100
            else:
                m[l, 0, zl - 30 - h - 1] = 70

    # ======================================================================

    img = images[2]
    h, l = np.shape(img)
    xl, yl, zl = np.shape(m)
    resized_image = cv2.resize(img, (xl, zl), interpolation=cv2.INTER_AREA)
    resized_image[resized_image > 0] = 255
    for h in range(zl):
        for l in range(xl):
            if resized_image[h, l] == 255:
                m[0, l, zl - 30 - h - 1] = 100
            else:
                m[0, l, zl - 30 - h - 1] = 70

    # ======================================================================

    img = images[0]
    h, l = np.shape(img)
    print h, l

    xl, yl, zl = np.shape(m)
    print xl, yl, zl

    resized_image = cv2.resize(img, (xl, yl), interpolation=cv2.INTER_AREA)
    resized_image[resized_image > 0] = 255

    print np.shape(resized_image)
    for h in range(xl):
        for l in range(yl):
            if resized_image[h, l] == 255:
                m[l, yl - h - 1, zl - 1] = 100
            else:
                m[l, yl - h - 1, zl - 1] = 70
    return m
