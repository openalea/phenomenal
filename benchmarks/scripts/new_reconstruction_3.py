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
import alinea.phenomenal.multi_view_reconstruction_without_loss
import alinea.phenomenal.viewer
import alinea.phenomenal.misc
import alinea.phenomenal.data_transformation
# ==============================================================================
# Define parameters of reconstruction
voxel_size = 4
verbose = True

# ==============================================================================
# Load images binarize
images = alinea.phenomenal.plant_1.plant_1_images_binarize()

# Load camera model parameters
params_camera_path, _ = alinea.phenomenal.plant_1. \
    plant_1_calibration_params_path()

cam_params = alinea.phenomenal.calibration_model.CameraModelParameters.read(
    params_camera_path)

print cam_params

# ==========================================================================
# Load Point_3D of the reference plant

points_3d_path = alinea.phenomenal.plant_1.plant_1_points_3d_path(
    radius=voxel_size)

images_projections_refs = list()
for angle in range(0, 360, 30):
    img = images[angle]
    function = alinea.phenomenal.calibration_model.\
        get_function_projection(cam_params, angle)

    ref = False
    if angle == 150:
        ref = True
    images_projections_refs.append((img, function, ref))


points_3d = alinea.phenomenal.multi_view_reconstruction_without_loss. \
    reconstruction_without_loss(images_projections_refs,
                                voxel_size=voxel_size,
                                error_tolerance=0,
                                verbose=True)

if voxel_size == voxel_size:
    assert len(points_3d) == 23976

if verbose:
    alinea.phenomenal.viewer.show_points_3d(points_3d)
