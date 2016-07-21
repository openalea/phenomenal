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
from alinea.phenomenal.plant_1 import (
    plant_1_calibration_camera_side,
    plant_1_images_binarize)

import alinea.phenomenal.calibration_model
import alinea.phenomenal.multi_view_reconstruction_without_loss
import alinea.phenomenal.viewer
import alinea.phenomenal.misc
import alinea.phenomenal.data_transformation
# ==============================================================================
images = plant_1_images_binarize()
calibration = plant_1_calibration_camera_side()

images_projections_refs = list()
for angle in range(0, 360, 30):
    img = images[angle]
    function = calibration.get_projection(angle)

    ref = False
    if angle == 150:
        ref = True
    images_projections_refs.append((img, function, ref))

# ==============================================================================

voxel_size = 4
voxel_centers = alinea.phenomenal.multi_view_reconstruction_without_loss. \
    reconstruction_without_loss(images_projections_refs,
                                voxel_size=voxel_size,
                                error_tolerance=0,
                                verbose=True)

# ==============================================================================

alinea.phenomenal.viewer.show_points_3d(voxel_centers)
