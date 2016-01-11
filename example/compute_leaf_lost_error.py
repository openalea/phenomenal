# -*- python -*-
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
import numpy

import alinea.phenomenal.data_load
import alinea.phenomenal.calibration_model
import alinea.phenomenal.multi_view_reconstruction
import alinea.phenomenal.viewer
import alinea.phenomenal.misc
import alinea.phenomenal.data_transformation
# ==============================================================================

radius = 4
angle_choose = 120
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

# ==============================================================================
# Compute 'leaf' lost error

images_diff = dict()
for angle in range(0, 360, 30):
    # Build image projection of points_3d cloud
    img = alinea.phenomenal.multi_view_reconstruction.\
        project_points_on_image(points_3d,
                                radius,
                                images[angle].shape,
                                projection,
                                angle)

    images_diff[angle] = numpy.subtract(images[angle], img)
    images_diff[angle][images_diff[angle] == -255] = 0
    images_diff[angle] = images_diff[angle].astype(numpy.uint8)

    leaf_lost_error = numpy.count_nonzero(images_diff[angle])
    print 'Image ', angle, 'degree : leaf lost error =', leaf_lost_error

# ==============================================================================
# Viewing
alinea.phenomenal.viewer.show_image(images_diff[angle_choose])
