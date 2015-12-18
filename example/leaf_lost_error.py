# -*- python -*-
#
#       leaf_lost_error.py : 
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

radius = 4
angle = 90
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

res = alinea.phenomenal.data_transformation.limit_points_3d(points_3d)
x_min, y_min, z_min, x_max, y_max, z_max = res

if verbose:
    print 'Limits points 3D : ', x_min, y_min, z_min, x_max, y_max, z_max

# ==============================================================================
# Build projection image refs

# Select images
images_selected = dict()
images_selected[angle] = images[angle]

image_com = numpy.ones(images[angle].shape) * 255.0
image_diff = numpy.zeros(images[angle].shape)

for i in range(int(x_min), int(x_max), int(radius * 2.0)):
    print i
    # Multi-view reconstruction
    points_3d_tmp = alinea.phenomenal.multi_view_reconstruction.\
        reconstruction_3d(images_selected, projection,
                          precision=radius,
                          origin_point=(float(i), 0.0, 0.0),
                          verbose=True)

    img_tmp = alinea.phenomenal.multi_view_reconstruction.\
        project_points_on_image(
            points_3d_tmp, radius, images[angle], projection, angle)

    print len(points_3d_tmp)

    img_tmp[img_tmp == 255] = 100
    image_com = numpy.subtract(image_com, img_tmp)
    image_com[image_com == 255] = 0
    image_com[image_com == -100] = 0
    image_com[image_com == 155] = 255


image_diff = numpy.subtract(image_diff, image_com)
image_diff[image_diff == 0] = 255
image_diff[image_diff == -255] = 0

if verbose:
    show_image(image_diff)
    show_image(image_com)

# ==============================================================================
# Projection image

# Build image projection of points_3d cloud
img = alinea.phenomenal.multi_view_reconstruction.project_points_on_image(
    points_3d, radius, images[angle], projection, angle)

# if verbose:
#     show_image(img)

img_diff_1 = numpy.subtract(img, image_com)
img_diff_1[img_diff_1 == -255] = 255

if verbose:
    show_image(img_diff_1)

print "Angle : ", angle, ' Err : ', numpy.count_nonzero(img_diff_1)

img_diff_1 = numpy.subtract(img_diff_1, image_diff)
img_diff_1[img_diff_1 == -255] = 0

if verbose:
    show_image(img_diff_1)

print "Angle : ", angle, ' Err : ', numpy.count_nonzero(img_diff_1)

