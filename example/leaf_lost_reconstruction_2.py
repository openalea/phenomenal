# -*- python -*-
#
#       leaf_lost_reconstruction_2.py :
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       File author(s): Simon Artzet <simon.artzet@gmail.com>
#
#       File contributor(s):
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================

import matplotlib.pyplot
import matplotlib.colors
import matplotlib.cm
import numpy
import gc

# ==============================================================================

import alinea.phenomenal.data_load
import alinea.phenomenal.calibration_model
import alinea.phenomenal.multi_view_reconstruction
import alinea.phenomenal.viewer
import alinea.phenomenal.misc
import alinea.phenomenal.data_transformation

# ==============================================================================


def show_image(image):
    im = image.copy()
    im = im.astype(numpy.uint8)

    fig = matplotlib.pyplot.figure(1)
    matplotlib.pyplot.imshow(im)
    matplotlib.pyplot.show()
    fig.clf()
    matplotlib.pyplot.close()
    del im
    gc.collect()

# ==============================================================================

radius = 10
verbose = True

# ==============================================================================

# Load images binarize
images = alinea.phenomenal.data_load.test_plant_1_images_binarize()

# Load camera model parameters
params_camera_path, _ = alinea.phenomenal.data_load.\
    test_plant_1_calibration_params_path()

cam_params = alinea.phenomenal.calibration_model.CameraModelParameters.read(
    params_camera_path)

# Create model projection object
projection = alinea.phenomenal.calibration_model.ModelProjection(cam_params)

# ==============================================================================

points_3d_path = alinea.phenomenal.data_load.test_plant_1_points_3d_path(
    radius=radius)

points_3d = alinea.phenomenal.misc.read_xyz(points_3d_path)

if verbose:
    alinea.phenomenal.viewer.show_points_3d(points_3d, scale_factor=20)

# ==============================================================================

res = alinea.phenomenal.data_transformation.limit_points_3d(points_3d)
x_min, y_min, z_min, x_max, y_max, z_max = res

if verbose:
    print 'Limits points 3D : ', x_min, y_min, z_min, x_max, y_max, z_max


# ==============================================================================

img_leaf = dict()
for angle in range(0, 360, 30):

    # Build image projection of points_3d cloud
    img = alinea.phenomenal.multi_view_reconstruction.project_points_on_image(
        points_3d, radius, images[angle].shape, projection, angle)

    img_leaf[angle] = numpy.subtract(images[angle], img)
    img_leaf[angle][img_leaf[angle] == -255] = 0

    print "Angle : ", angle, ' Err : ', numpy.count_nonzero(img_leaf[angle])

    # if verbose:
    #     show_image(img_leaf[angle])

# ==============================================================================

import numpy.random
import random


def find_neighbort(img, x, y):
    neighbort = list()
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            if img[x + i, y + j] == 255:
                neighbort.append((x + i, y + j))

    return neighbort


def find_leaf(src):

    img = src.copy()
    index = numpy.where(img == 255)
    leafs = list()

    for i in range(len(index[0])):
        x = index[0][i]
        y = index[1][i]

        if img[x, y] == 255:

            leaf = list()
            leaf.append((x, y))
            img[x, y] = 11

            l = find_neighbort(img, x, y)

            while l:
                x, y = l.pop()
                if img[x, y] == 255:
                    img[x, y] = 11
                    leaf.append((x, y))

                    l += find_neighbort(img, x, y)

            leafs.append(numpy.array(leaf))

    return leafs


def build_image(leafs, shape_image, verbose=False):

    if verbose:
        print 'Nb leaf : ', len(leafs)

    image = numpy.zeros(shape_image)
    image = image.astype(float)

    for i in range(len(leafs)):
        for pt in leafs[i]:
            image[tuple(pt)] = 255

    return image


def move_leafs(leafs, x, y):
    for i in range(len(leafs)):
        leafs[i] = leafs[i] - (x, y)

    return leafs


def fit_function_2(x0):

    img_tmp = dict()
    img_tmp[0] = img_leaf[0]
    index = 0
    step = 2

    for angle in range(30, 60, 30):
        leaf = move_leafs(leaf_dict[angle],
                          x0[index * step], x0[index * step + 1])

        img_tmp[angle] = build_image(leaf, img_leaf[angle].shape)
        index += 1

    points_3d_leaf, err = alinea.phenomenal.multi_view_reconstruction.\
        reconstruction_3d(img_tmp, projection,
                          precision=radius, verbose=True)

    err = 10000000.0 / err
    print err
    return err


# ==============================================================================

print 'Original image : ', len(img_leaf[0]), numpy.count_nonzero(img_leaf[0])
# show_image(img_leaf[0])

leafs = find_leaf(img_leaf[0])
origin_img = build_image(leafs, img_leaf[0].shape, verbose=True)
print 'Build original : ', len(origin_img), numpy.count_nonzero(origin_img)
# show_image(origin_img)

leafs = move_leafs(leafs, 0.0, 0.0)
img = build_image(leafs, img_leaf[0].shape, verbose=True)
print 'Build img : ', len(img), numpy.count_nonzero(img)
# show_image(img)

# ==============================================================================

angle = 180

# ==============================================================================

guess_size = 0
leaf_dict = dict()
leaf_dict[angle] = find_leaf(img_leaf[angle])

# for angle in range(30, 60, 30):
#     print 'Angle : ', angle
#     leaf_dict[angle] = find_leaf(img_leaf[angle])
#     guess_size += len(leaf_dict[angle])

print 'TOTAL Guess: ', guess_size

# ==============================================================================

img_tmp = dict()
img_tmp[0] = img_leaf[0]
for angle in range(30, 60, 30):
    img_tmp[angle] = img_leaf[angle]

points_3d_leaf, err = alinea.phenomenal.multi_view_reconstruction.\
    reconstruction_3d(img_tmp, projection, precision=radius, verbose=True)

err = 10000000.0 / err
print 'Init Error: ', err

# ==============================================================================

x0 = [0.0] * (guess_size * 2)
print len(x0)
print x0

fit_function_2(x0)

# ==============================================================================
import scipy.optimize

scipy.optimize.minimize(fit_function_2, x0, method='BFGS')

# ==============================================================================

# for i in range(10):
#     fit_function_2(x0)

#
# import cv2
# import numpy.random
# import scipy.optimize
#
#
# img_leaf_shape = img_leaf[0].shape
# center = img_leaf_shape[0] / 2.0, img_leaf_shape[1] / 2.0
#
#
#
# def fit_function(x0):
#
#     index = 0
#     step = 6
#     img_tmp = dict()
#     img_tmp[0] = img_leaf[0]
#
#     # alpha = x0[index: index + step]
#     # M = cv2.getRotationMatrix2D(center, alpha, 1.0)
#     # print M
#
#     M = numpy.reshape(x0[index: index + step], (2, 3))
#     img_tmp[30] = cv2.warpAffine(img_leaf[30], M, img_leaf_shape)
#     # for angle in range(30, 360, 30):
#     #     alpha = x0[index]
#     #     M = cv2.getRotationMatrix2D(center, alpha, 1.0)
#     #     img_tmp[angle] = cv2.warpAffine(img_leaf[angle], M, img_leaf_shape)
#     #     index += step
#
#     points_3d_leaf, err = alinea.phenomenal.multi_view_reconstruction.\
#         reconstruction_3d(img_tmp, projection, precision=radius)
#
#     err = 10000.0 / err
#     print err
#     return err
#
# x0 = list()
# for i in range(6):
#     x0.append(numpy.random.random())
#
# print scipy.optimize.minimize(fit_function, x0, method='BFGS')
#
# bounds = list()
# for i in range(6):
#     bounds.append((0.0, 10))
#
# scipy.optimize.differential_evolution(fit_function, bounds)
