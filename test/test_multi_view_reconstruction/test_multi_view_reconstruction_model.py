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
from alinea.phenomenal.data_access.data_creation import (
    build_cube)

from alinea.phenomenal.data_access.plant_1 import (
    plant_1_calibration_camera_side)

from alinea.phenomenal.data_structure import (
    ImageView)

from alinea.phenomenal.multi_view_reconstruction import (
        project_voxel_centers_on_image,
        reconstruction_3d,
        compute_reconstruction_error)

# ==============================================================================


def get_image_views_cube_projected():

    # ==========================================================================
    # Create object
    voxels_size = 10
    voxels_position = build_cube(cube_size=10,
                                 voxels_size=voxels_size,
                                 voxels_position=(0, 0, 0))

    assert len(voxels_position) == 1000
    volume = len(voxels_position) * (10**3)
    assert volume == 1000000

    # ==========================================================================
    calibration = plant_1_calibration_camera_side()

    shape_image = (2454, 2056)
    image_views = list()
    for angle in range(0, 360, 30):
        projection = calibration.get_projection(angle)

        img = project_voxel_centers_on_image(voxels_position,
                                             voxels_size,
                                             shape_image,
                                             projection)

        iv = ImageView(img, projection, inclusive=False)
        image_views.append(iv)

    return image_views


def test_multi_view_reconstruction():

    image_views = get_image_views_cube_projected()

    # ==========================================================================

    vpc = reconstruction_3d(image_views, voxels_size=20, verbose=True)

    assert len(vpc.voxels_position) == 288
    assert len(vpc.voxels_position) * vpc.voxels_size ** 3 == 2304000

    for iv in image_views:

        false_positive, true_negative = compute_reconstruction_error(
            vpc.voxels_position,
            vpc.voxels_size,
            iv.image,
            iv.projection)

        assert false_positive < 70
        assert true_negative == 0


# ==============================================================================

if __name__ == "__main__":
    for func_name in dir():
        if func_name.startswith('test_'):
            print("{func_name}".format(func_name=func_name))
            eval(func_name)()