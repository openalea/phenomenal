# -*- python -*-
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
# ==============================================================================
from alinea.phenomenal.data_creation import (
    build_object_1,
    build_images_1)

from alinea.phenomenal.plant_1 import (
    plant_1_calibration_camera_side_2_target)

from alinea.phenomenal.multi_view_reconstruction import (
    project_voxel_centers_on_image,
    reconstruction_3d,
    error_reconstruction)
# ==============================================================================


def test_multi_view_reconstruction_model_1():
    # ==========================================================================
    # Create object
    cube_size = 10
    voxel_size = 10
    voxel_center = (0, 0, 0)

    voxel_centers = build_object_1(cube_size, voxel_size, voxel_center)

    assert len(voxel_centers) == 1000
    volume = len(voxel_centers) * voxel_size**3
    assert volume == 1000000

    # ==========================================================================
    calibration = plant_1_calibration_camera_side_2_target()

    images_projections = list()
    shape_image = (2454, 2056)
    for angle in range(0, 360, 30):
        projection = calibration.get_projection(angle)

        img = project_voxel_centers_on_image(voxel_centers,
                                             voxel_size,
                                             shape_image,
                                             projection)

        images_projections.append((img, projection))

    # ==========================================================================
    voxel_size = 20
    voxel_centers = reconstruction_3d(images_projections,
                                      voxel_size=voxel_size,
                                      verbose=True)

    assert len(voxel_centers) == 288
    volume = len(voxel_centers) * voxel_size**3
    assert volume == 2304000


def test_multi_view_reconstruction_model_2():

    # ==========================================================================
    # Load camera model parameters
    calibration = plant_1_calibration_camera_side_2_target()

    # ==========================================================================
    # Build images_projections
    images = build_images_1()
    images_projections = list()
    for angle in range(0, 360, 30):
        projection = calibration.get_projection(angle)
        img = images[angle]
        images_projections.append((img, projection))

    # ==========================================================================

    voxel_size = 8
    voxel_centers = reconstruction_3d(images_projections,
                                      voxel_size=voxel_size,
                                      verbose=True)

    print len(voxel_centers)
    assert len(voxel_centers) == 7280

    for image, projection in images_projections:
        err = error_reconstruction(
            image, projection, voxel_centers, voxel_size)

        assert err < 4000


# ==============================================================================

if __name__ == "__main__":
    test_multi_view_reconstruction_model_1()
    test_multi_view_reconstruction_model_2()
