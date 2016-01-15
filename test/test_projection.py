# -*- python -*-
#
#       test_projection.py :
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
import alinea.phenomenal.calibration_model
import alinea.phenomenal.plant_1
import alinea.phenomenal.frame
# ==============================================================================


def test_projection_1():

    # Load camera model parameters
    params_camera_path, _ = alinea.phenomenal.plant_1.\
        plant_1_calibration_params_path()

    cam_params = alinea.phenomenal.calibration_model.CameraModelParameters.read(
        params_camera_path)

    # Create model projection object
    projection = alinea.phenomenal.calibration_model.ModelProjection(cam_params)

    angle = 0
    pt3D = (0.0, 0.0, 0.0)
    pt2D = projection.project_point(pt3D, angle)
    assert pt2D == (1021.4986140136053, 1261.8663825892806)

    pt3D = (100.0, 100.0, 0.0)
    pt2D = projection.project_point(pt3D, angle)
    assert pt2D == (900.46445486999426, 1261.4446298508358)

    angle = 90
    pt2D = projection.project_point(pt3D, angle)
    assert pt2D == (1009.1478179983641, 1261.823345300649)


def test_local_point():
    # Load camera model parameters
    params_camera_path, _ = alinea.phenomenal.plant_1.\
        plant_1_calibration_params_path()

    cam_params = alinea.phenomenal.calibration_model.CameraModelParameters.read(
        params_camera_path)

    # Create model projection object
    projection = alinea.phenomenal.calibration_model.ModelProjection(cam_params)

    pt3D = (100.0, 0.0, 0.0)
    pt_2d_0 = projection.project_point(pt3D, 0)
    pt_2d_100 = projection.project_point(pt3D, 100)
    pt_2d_90 = projection.project_point(pt3D, 90)

    print pt_2d_0, pt_2d_100, pt_2d_90

    pts_2d_0 = projection.project_points([pt3D, pt3D, pt3D, pt3D, pt3D], 0)
    pts_2d_100 = projection.project_points([pt3D, pt3D, pt3D, pt3D, pt3D], 100)
    pts_2d_90 = projection.project_points([pt3D, pt3D, pt3D, pt3D, pt3D], 90)

    print pts_2d_0

    pts_2d_0[pts_2d_0 < 0] = 0

    print pts_2d_0[0]



if __name__ == '__main__':
    test_projection_1()
    test_local_point()