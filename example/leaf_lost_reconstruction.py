# -*- coding: utf-8 -*-
# -*- python -*-
#
#       leaf_lost_reconstruction.py : 
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
import numpy

import alinea.phenomenal.data_load
import alinea.phenomenal.calibration_model
import alinea.phenomenal.multi_view_reconstruction
import alinea.phenomenal.viewer
import alinea.phenomenal.misc
import alinea.phenomenal.data_transformation


# ==============================================================================


def show_image(image):
    matplotlib.pyplot.imshow(image)
    matplotlib.pyplot.show()


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

shape_image = images[0].shape

# ==============================================================================

image_leaf = dict()
for angle in range(0, 360, 30):

    # Build image projection of points_3d cloud
    img = alinea.phenomenal.multi_view_reconstruction.project_points_on_image(
        points_3d, radius, shape_image, projection, angle)

    image_leaf[angle] = numpy.subtract(images[angle], img)
    image_leaf[angle][image_leaf[angle] == -255] = 0

    print "Angle : ", angle, ' Err : ', numpy.count_nonzero(image_leaf[angle])

    # if verbose:
    #     show_image(img_diff[angle])

# ==============================================================================

angle_ref = 150

# ==============================================================================
import collections

points_3d_origin = collections.deque()
for i in range(int(x_min), int(x_max), int(radius * 2.0)):
    points_3d_origin.append((float(i), 0.0, 0.0))


images_selected = dict()
images_selected[angle_ref] = image_leaf[angle_ref]
points_3d_leaf, err = alinea.phenomenal.multi_view_reconstruction.reconstruction_3d(
    images_selected, projection,
    precision=radius, points_3d=points_3d_origin, verbose=True)

if verbose:
    import mayavi.mlab

    mayavi.mlab.figure('figure')

    mayavi.mlab.quiver3d(0, 0, 0, 1, 0, 0, line_width=5.0, scale_factor=100)
    mayavi.mlab.quiver3d(0, 0, 0, 0, 1, 0, line_width=5.0, scale_factor=100)
    mayavi.mlab.quiver3d(0, 0, 0, 0, 0, 1, line_width=5.0, scale_factor=100)

    alinea.phenomenal.viewer.plot_points_3d(points_3d_leaf)
    alinea.phenomenal.viewer.plot_points_3d(points_3d)
    mayavi.mlab.show()


# ==============================================================================

points_3d_leaf_plan = dict()
images_selected = dict()
images_selected[angle_ref] = image_leaf[angle_ref]

for i in range(int(x_min), int(x_max), int(radius * 2.0)):
    print i
    points_3d_leaf_plan[i], err = alinea.phenomenal.multi_view_reconstruction.\
        reconstruction_3d(images_selected, projection,
                          precision=radius,
                          origin_point=(float(i), 0.0, 0.0))


if verbose:
    import mayavi.mlab

    mayavi.mlab.figure('figure')

    mayavi.mlab.quiver3d(0, 0, 0, 1, 0, 0, line_width=5.0, scale_factor=100)
    mayavi.mlab.quiver3d(0, 0, 0, 0, 1, 0, line_width=5.0, scale_factor=100)
    mayavi.mlab.quiver3d(0, 0, 0, 0, 0, 1, line_width=5.0, scale_factor=100)

    for i in points_3d_leaf_plan:
        alinea.phenomenal.viewer.plot_points_3d(points_3d_leaf_plan[i])
    alinea.phenomenal.viewer.plot_points_3d(points_3d)
    mayavi.mlab.show()

# ==============================================================================

mat, index, origin = alinea.phenomenal.data_transformation.\
    points_3d_to_matrix_2(points_3d, points_3d_leaf_plan, radius)

print mat.shape
x_length, y_length, z_length = mat.shape


def have_neighbort(x, y, z):

    if 0 < x < x_length - 1 and 0 < y < y_length - 1 and 0 < z < z_length - 1:
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if mat[x + i, y, z + j] == 1:
                    return True
    return False


def next_neighbort(x, y, z, value):
    l = list()
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            for k in [-1, 0, 1]:
                if mat[x + i, y + j, z + k] == value:
                    l.append((x + i, y + j, z + k))
    return l

mat = mat.astype(int)

for point_3d in index:
    value = mat[point_3d]
    if value > 1:
        if have_neighbort(*point_3d):
            mat[point_3d] = -1
            x, y, z = point_3d

            l = next_neighbort(x, y, z, value)

            while True:
                try:
                    xx, yy, zz = l.pop()
                    if mat[xx, yy, zz] == value:
                        mat[xx, yy, zz] = -1
                        l += next_neighbort(xx, yy, zz, value)

                except IndexError:
                    break


mat[mat == -1] = 111

points_3d, points_3d_leaf = alinea.phenomenal.data_transformation.\
    matrix_to_points_3d_2(mat, radius, origin)

print len(points_3d_leaf)
print len(points_3d)

if verbose:
    import mayavi.mlab

    mayavi.mlab.figure('figure')

    mayavi.mlab.quiver3d(0, 0, 0, 1, 0, 0, line_width=5.0, scale_factor=100)
    mayavi.mlab.quiver3d(0, 0, 0, 0, 1, 0, line_width=5.0, scale_factor=100)
    mayavi.mlab.quiver3d(0, 0, 0, 0, 0, 1, line_width=5.0, scale_factor=100)

    alinea.phenomenal.viewer.plot_points_3d(points_3d_leaf)
    alinea.phenomenal.viewer.plot_points_3d(points_3d)
    mayavi.mlab.show()

groups = dict()
for pt in points_3d_leaf:
    x, y, z = pt

    if x not in groups:
        groups[x] = list()

    groups[x].append(pt)


import math

groups = dict()
for pt in points_3d_leaf_plan[10]:
    pt2D = projection.project_point(pt, angle_ref)
    groups[pt2D] = list()

print len(groups.keys())

for pt in points_3d_leaf:
    pt_x, pt_y = projection.project_point(pt, angle_ref)

    pt2D_save = None
    min_dist = float("inf")
    for x, y in groups:
        dist = math.sqrt((pt_x - x) ** 2 + (pt_y - y) ** 2)

        if dist < min_dist:
            min_dist = dist
            pt2D_save = (x, y)

    groups[pt2D_save].append(pt)

print 'Number of points', len(points_3d_leaf)
print 'Length groups : ', len(groups.keys())
print 'Length leafs : ', len(points_3d_leaf[10])

# ==============================================================================

if verbose:
    import mayavi.mlab

    mayavi.mlab.figure('figure')

    mayavi.mlab.quiver3d(0, 0, 0, 1, 0, 0, line_width=5.0, scale_factor=100)
    mayavi.mlab.quiver3d(0, 0, 0, 0, 1, 0, line_width=5.0, scale_factor=100)
    mayavi.mlab.quiver3d(0, 0, 0, 0, 0, 1, line_width=5.0, scale_factor=100)

    for pt2D in groups:
        mypt3d = list()
        for pt3D in groups[pt2D]:
            mypt3d.append(pt3D)

        alinea.phenomenal.viewer.plot_points_3d(mypt3d)

    alinea.phenomenal.viewer.plot_points_3d(points_3d)
    mayavi.mlab.show()

# ==============================================================================

shape_image = images[0].shape
height_image, length_image = shape_image

where_x_y = dict()
for angle in range(0, 360, 30):
    where_x_y[angle] = numpy.where(image_leaf[angle] > 0)


def distance_closest_point(angle, pt_x, pt_y):
    xx, yy = where_x_y[angle]

    return min((xx - pt_x) ** 2 + (yy - pt_y) ** 2)


# ==========================================================================

print 'Number of groups : ', len(groups.keys())

mypt3d = list()
for pt2d in groups:

    min_dist = float('inf')
    save_pt = None

    print 'Len group : ', len(groups[pt2d])
    for pt3D in groups[pt2d]:
        sum_dist = 0
        for angle in range(0, 360, 30):
            pt_x, pt_y = projection.project_point(pt3D, angle)

            if pt_x < 0 or pt_x > length_image:
                sum_dist = float('inf')
                break
            if pt_y < 0 or pt_y > height_image:
                sum_dist = float('inf')
                break

            sum_dist += distance_closest_point(angle, int(pt_x), int(pt_y))

        if sum_dist < min_dist:
            min_dist = sum_dist
            save_pt = pt3D

    print 'Res : ', save_pt
    if save_pt is not None:
        mypt3d.append(save_pt)

img = alinea.phenomenal.multi_view_reconstruction. \
    project_points_on_image(
    mypt3d, radius, shape_image, projection, angle_ref)

img = numpy.subtract(image_leaf[angle_ref], img)
img[img == -255] = 0

print 'Valid error reconstruction 0 : ', numpy.count_nonzero(img)

if verbose:
    import mayavi.mlab

    mayavi.mlab.figure('figure')

    mayavi.mlab.quiver3d(0, 0, 0, 1, 0, 0, line_width=5.0, scale_factor=100)
    mayavi.mlab.quiver3d(0, 0, 0, 0, 1, 0, line_width=5.0, scale_factor=100)
    mayavi.mlab.quiver3d(0, 0, 0, 0, 0, 1, line_width=5.0, scale_factor=100)

    alinea.phenomenal.viewer.plot_points_3d(mypt3d)
    alinea.phenomenal.viewer.plot_points_3d(points_3d)
    mayavi.mlab.show()