# -*- python -*-
#
#       leaf_lost_error_2.py : 
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

radius = 2
angle = 120
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

# Build image projection of points_3d cloud
img = alinea.phenomenal.multi_view_reconstruction.project_points_on_image(
    points_3d, radius, images[angle], projection, angle)

if verbose:
    show_image(img)

img_diff = numpy.subtract(images[angle], img)
img_diff[img_diff == -255] = 0

if verbose:
    show_image(img_diff)

print "Angle : ", angle, ' Err : ', numpy.count_nonzero(img_diff)
