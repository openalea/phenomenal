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
import alinea.phenomenal.data_load
import alinea.phenomenal.calibration_model
import alinea.phenomenal.multi_view_reconstruction
import alinea.phenomenal.viewer
import alinea.phenomenal.misc
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

# Select images
images_selected = dict()
for angle in range(0, 360, 30):
    images_selected[angle] = images[angle]

radius = 4
# Multi-view reconstruction
points_3d = alinea.phenomenal.multi_view_reconstruction.reconstruction_3d(
    images_selected, projection, radius, verbose=True)

# Write
alinea.phenomenal.misc.write_xyz(points_3d, 'points_3d_radius_' + str(radius))

# Read
points_3d = alinea.phenomenal.misc.read_xyz('points_3d_radius_' + str(radius))

# Viewing
alinea.phenomenal.viewer.show_points_3d(points_3d, scale_factor=2)
