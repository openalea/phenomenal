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
import alinea.phenomenal.plant_1
import alinea.phenomenal.calibration_model
import alinea.phenomenal.multi_view_reconstruction
import alinea.phenomenal.viewer
import alinea.phenomenal.misc
import alinea.phenomenal.data_transformation
# ==============================================================================
# Define parameters of reconstruction
radius = 4
verbose = True

# ==============================================================================
# Load images binarize
images = alinea.phenomenal.plant_1.plant_1_images_binarize()

# Load camera model parameters
params_camera_path, _ = alinea.phenomenal.plant_1. \
    plant_1_calibration_params_path()

cam_params = alinea.phenomenal.calibration_model.CameraModelParameters.read(
    params_camera_path)

# Create model projection object
projection = alinea.phenomenal.calibration_model.ModelProjection(cam_params)

# ==========================================================================
# Load Point_3D of the reference plant

points_3d_path = alinea.phenomenal.plant_1.plant_1_points_3d_path(
    radius=radius)

images_selected = dict()
for angle in range(0, 360, 30):
    images_selected[angle] = images[angle]

points_3d = alinea.phenomenal.multi_view_reconstruction. \
    new_reconstruction_3d(images_selected, projection, radius, [150],
                          verbose=True)

if verbose:
    alinea.phenomenal.viewer.show_points_3d(points_3d)
