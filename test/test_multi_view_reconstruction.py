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
# ==============================================================================


def test_1():
    # Load images binarize
    images = alinea.phenomenal.plant_1.plant_1_images_binarize()

    # Load camera model parameters
    params_camera_path, _ = alinea.phenomenal.plant_1.\
        plant_1_calibration_params_path()

    cam_params = alinea.phenomenal.calibration_model.CameraModelParameters.read(
        params_camera_path)

    images_and_projections = list()
    for angle in range(0, 360, 30):
        img = images[angle]
        function = alinea.phenomenal.calibration_model.\
            get_function_projection(cam_params, angle)

        images_and_projections.append((img, function))

    voxel_size = 4
    # Multi-view reconstruction
    voxel_centers = alinea.phenomenal.multi_view_reconstruction.\
        reconstruction_3d(images_and_projections,
                          voxel_size=voxel_size,
                          verbose=True)

    if voxel_size == 8:
        assert len(voxel_centers) == 22965
    if voxel_size == 4:
        assert len(voxel_centers) == 120276
    if voxel_size == 2:
        assert len(voxel_centers) == 750529

    # # Viewing
    # alinea.phenomenal.viewer.show_points_3d(voxel_centers, scale_factor=20)

if __name__ == "__main__":
    test_1()
