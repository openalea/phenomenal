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
import alinea.phenomenal.calibration_model
import alinea.phenomenal.multi_view_reconstruction
import alinea.phenomenal.data_transformation
import alinea.phenomenal.data_creation
import alinea.phenomenal.plant_1
# ==============================================================================


def test_multi_view_reconstruction_model_1():

    point_3d = (-472, -472, 200)
    angle = 0

    # Load camera model parameters
    params_camera_path, _ = alinea.phenomenal.plant_1.\
        plant_1_calibration_params_path()

    cam_params = alinea.phenomenal.calibration_model.CameraModelParameters.read(
        params_camera_path)

    # Create model projection object
    projection = alinea.phenomenal.calibration_model.ModelProjection(cam_params)

    pt_2d = projection.project_point(point_3d, angle)
    assert pt_2d == (1584.369708483704, 1094.5132593357166)

    function = alinea.phenomenal.calibration_model.get_function_projection(
        cam_params, angle)
    print function(point_3d)


# ==============================================================================
# LOCAL TEST

if __name__ == "__main__":
    test_multi_view_reconstruction_model_1()
